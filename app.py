import pandas as pd
import plotly.express as px
import streamlit as st
from googleapiclient.discovery import build

# Configuração da página
st.set_page_config(page_title="Analisador Completo de Shorts", layout="wide")
st.title("📊 Analisador Avançado de YouTube Shorts")

# Puxa a chave de API (local pelo secrets.toml ou no Streamlit Cloud)
api_key = st.secrets.get("YOUTUBE_API_KEY")

# Sidebar - Parâmetros de Entrada
st.sidebar.header("⚙️ Configurações da Busca")
channel_id = st.sidebar.text_input("ID do Canal (ex: UCxxxx...):")
max_results = st.sidebar.slider("Quantidade de vídeos para analisar:", 10, 100, 50, step=10)

if channel_id and api_key:
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)

        with st.spinner('Buscando e processando dados do YouTube...'):
            # 1. Obter a playlist de uploads do canal
            res = youtube.channels().list(id=channel_id, part='contentDetails,snippet').execute()
            if not res['items']:
                st.error("Canal não encontrado. Verifique o ID digitado.")
                st.stop()
                
            nome_canal = res['items'][0]['snippet']['title']
            playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            # 2. Obter lista de vídeos
            playlist_res = youtube.playlistItems().list(
                playlistId=playlist_id,
                part='snippet',
                maxResults=max_results
            ).execute()

            video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_res['items']]

            # 3. Obter estatísticas detalhadas dos vídeos
            stats_res = youtube.videos().list(
                id=','.join(video_ids),
                part='snippet,statistics'
            ).execute()

            dados = []
            dias_semana_pt = {
                'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 
                'Wednesday': 'Quarta-feira', 'Thursday': 'Quinta-feira', 
                'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
            }

            for item in stats_res['items']:
                data_utc = pd.to_datetime(item['snippet']['publishedAt'])
                data_br = data_utc.tz_convert('America/Sao_Paulo')
                
                dados.append({
                    'Título': item['snippet']['title'],
                    'Data': data_br.date(),
                    'Dia da Semana': dias_semana_pt[data_br.strftime('%A')],
                    'Hora_Cheia': f"{data_br.hour:02d}:00",
                    'Visualizações': int(item['statistics'].get('viewCount', 0)),
                    'Curtidas': int(item['statistics'].get('likeCount', 0)),
                    'Comentários': int(item['statistics'].get('commentCount', 0)),
                    'URL': f"https://www.youtube.com/shorts/{item['id']}"
                })

            df = pd.DataFrame(dados)

        st.subheader(f"Canal Analisado: **{nome_canal}**")

        # --- FILTROS DE DATA NA SIDEBAR ---
        st.sidebar.markdown("---")
        st.sidebar.header("📅 Filtros de Análise")
        
        data_min = df['Data'].min()
        data_max = df['Data'].max()
        
        data_inicio, data_fim = st.sidebar.date_input(
            "Filtrar Período:",
            value=(data_min, data_max),
            min_value=data_min,
            max_value=data_max
        )

        # Aplicar filtro de data no DataFrame
        df_filtrado = df[(df['Data'] >= data_inicio) & (df['Data'] <= data_fim)]

        if df_filtrado.empty:
            st.warning("Nenhum vídeo encontrado no período selecionado.")
            st.stop()

        # --- METRICAS DE RESUMO (KPIs) ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Vídeos Analisados", len(df_filtrado))
        col2.metric("Total de Visualizações", f"{df_filtrado['Visualizações'].sum():,}")
        col3.metric("Média de Views / Short", f"{int(df_filtrado['Visualizações'].mean()):,}")
        col4.metric("Média de Curtidas", f"{int(df_filtrado['Curtidas'].mean()):,}")

        st.markdown("---")

        # --- GRÁFICOS EM ABAS ---
        aba1, aba2 = st.tabs(["⏰ Média por Horário", "📅 Média por Dia da Semana"])

        with aba1:
            media_por_hora = df_filtrado.groupby('Hora_Cheia')['Visualizações'].mean().reset_index()
            media_por_hora = media_por_hora.sort_values(by='Hora_Cheia')

            fig_hora = px.bar(
                media_por_hora, 
                x='Hora_Cheia', 
                y='Visualizações',
                title="Média de Visualizações por Horário de Publicação (Horário de Brasília)",
                labels={'Hora_Cheia': 'Horário do Upload', 'Visualizações': 'Média de Views'},
                color_discrete_sequence=['#FF0000']
            )
            fig_hora.update_layout(template="plotly_white")
            st.plotly_chart(fig_hora, use_container_width=True)

        with aba2:
            ordem_dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
            media_por_dia = df_filtrado.groupby('Dia da Semana')['Visualizações'].mean().reindex(ordem_dias).dropna().reset_index()

            fig_dia = px.bar(
                media_por_dia, 
                x='Dia da Semana', 
                y='Visualizações',
                title="Média de Visualizações por Dia da Semana",
                labels={'Dia da Semana': 'Dia da Semana', 'Visualizações': 'Média de Views'},
                color_discrete_sequence=['#1E88E5']
            )
            fig_dia.update_layout(template="plotly_white")
            st.plotly_chart(fig_dia, use_container_width=True)

        st.markdown("---")

        # --- TABELA DE DADOS DETALHADA ---
        st.subheader("📋 Tabela Detalhada dos Vídeos")
        
        ordem_coluna = st.selectbox(
            "Ordenar tabela por:",
            ["Visualizações", "Curtidas", "Comentários", "Data"]
        )
        
        df_exibicao = df_filtrado.sort_values(by=ordem_coluna, ascending=False)
        
        st.dataframe(
            df_exibicao[['Título', 'Data', 'Dia da Semana', 'Hora_Cheia', 'Visualizações', 'Curtidas', 'Comentários', 'URL']],
            use_container_width=True
        )

        # Botão para baixar CSV
        csv = df_exibicao.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Tabela em CSV (Excel)",
            data=csv,
            file_name=f'analise_shorts_{nome_canal}.csv',
            mime='text/csv',
        )

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar os dados: {e}")
else:
    st.info("Digite o ID de um canal na barra lateral esquerda para iniciar a análise.")
