import pandas as pd
import plotly.express as px
import streamlit as st
from googleapiclient.discovery import build

# Configuração da página
st.set_page_config(page_title="Analisador & Comparador de Shorts", layout="wide")
st.title("📊 Analisador & Comparador de YouTube Shorts")

# Puxa a chave de API (local pelo secrets.toml ou no Streamlit Cloud)
api_key = st.secrets.get("YOUTUBE_API_KEY")

dias_semana_pt = {
    'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 
    'Wednesday': 'Quarta-feira', 'Thursday': 'Quinta-feira', 
    'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}

ordem_dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']

# --- FUNÇÃO PRINCIPAL DE COLETA DE DADOS ---
def buscar_dados_canal(youtube_api, channel_id, max_results):
    res = youtube_api.channels().list(id=channel_id, part='contentDetails,snippet').execute()
    if not res['items']:
        return None, None
        
    nome_canal = res['items'][0]['snippet']['title']
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    playlist_res = youtube_api.playlistItems().list(
        playlistId=playlist_id,
        part='snippet',
        maxResults=max_results
    ).execute()

    video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_res['items']]

    stats_res = youtube_api.videos().list(
        id=','.join(video_ids),
        part='snippet,statistics'
    ).execute()

    dados = []
    for item in stats_res['items']:
        data_utc = pd.to_datetime(item['snippet']['publishedAt'])
        data_br = data_utc.tz_convert('America/Sao_Paulo')
        
        views = int(item['statistics'].get('viewCount', 0))
        likes = int(item['statistics'].get('likeCount', 0))
        
        taxa_eng = (likes / views * 100) if views > 0 else 0.0

        dados.append({
            'Canal': nome_canal,
            'Título': item['snippet']['title'],
            'Data': data_br.date(),
            'Dia da Semana': dias_semana_pt[data_br.strftime('%A')],
            'Hora_Cheia': f"{data_br.hour:02d}:00",
            'Visualizações': views,
            'Curtidas': likes,
            'Taxa Engajamento (%)': round(taxa_eng, 2),
            'Comentários': int(item['statistics'].get('commentCount', 0)),
            'URL': f"https://www.youtube.com/shorts/{item['id']}"
        })

    return nome_canal, pd.DataFrame(dados)


# --- BARRA LATERAL (NAVEGAÇÃO) ---
modo_app = st.sidebar.radio("Selecione a ferramenta:", ["Análise Única + Insights", "⚔️ Comparar 2 Canais"])
max_results = st.sidebar.slider("Quantidade de vídeos por canal:", 10, 100, 50, step=10)

if api_key:
    youtube = build('youtube', 'v3', developerKey=api_key)

    # =========================================================
    # MODALIDADE 1: ANÁLISE ÚNICA + INSIGHTS
    # =========================================================
    if modo_app == "Análise Única + Insights":
        channel_id = st.sidebar.text_input("ID do Canal (ex: UCxxxx...):")

        if channel_id:
            try:
                with st.spinner('Buscando e processando dados...'):
                    nome_canal, df = buscar_dados_canal(youtube, channel_id, max_results)

                if df is None:
                    st.error("Canal não encontrado. Verifique o ID digitado.")
                else:
                    st.subheader(f"Canal Analisado: **{nome_canal}**")

                    # Filtro de Período
                    st.sidebar.markdown("---")
                    data_min, data_max = df['Data'].min(), df['Data'].max()
                    data_inicio, data_fim = st.sidebar.date_input(
                        "Filtrar Período:", value=(data_min, data_max), min_value=data_min, max_value=data_max
                    )
                    df_filtrado = df[(df['Data'] >= data_inicio) & (df['Data'] <= data_fim)]

                    # Insights Inteligentes
                    media_hora = df_filtrado.groupby('Hora_Cheia')['Visualizações'].mean().reset_index()
                    melhor_horario = media_hora.sort_values(by='Visualizações', ascending=False).iloc[0]

                    media_dia = df_filtrado.groupby('Dia da Semana')['Visualizações'].mean().reset_index()
                    melhor_dia = media_dia.sort_values(by='Visualizações', ascending=False).iloc[0]

                    # Cruzamento Dia x Horário
                    matriz_cruzada = df_filtrado.groupby(['Dia da Semana', 'Hora_Cheia'])['Visualizações'].mean().reset_index()
                    melhor_combinacao = matriz_cruzada.sort_values(by='Visualizações', ascending=False).iloc[0]

                    st.markdown("### 🎯 Melhores Momentos do Canal")
                    col_ins1, col_ins2, col_ins3 = st.columns(3)
                    col_ins1.info(f"⏰ **Melhor Horário Geral:** `{melhor_horario['Hora_Cheia']}`")
                    col_ins2.success(f"📅 **Melhor Dia Geral:** `{melhor_dia['Dia da Semana']}`")
                    col_ins3.warning(f"🔥 **Combinação Perfeita:** `{melhor_combinacao['Dia da Semana']}` às `{melhor_combinacao['Hora_Cheia']}`")

                    st.markdown("---")

                    # KPIs Básicos
                    tot_views = df_filtrado['Visualizações'].sum()
                    tot_likes = df_filtrado['Curtidas'].sum()
                    taxa_global = (tot_likes / tot_views * 100) if tot_views > 0 else 0.0

                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("Vídeos Analisados", len(df_filtrado))
                    col2.metric("Total de Views", f"{df_filtrado['Visualizações'].sum():,}")
                    col3.metric("Média de Views", f"{int(df_filtrado['Visualizações'].mean()):,}")
                    col4.metric("Média de Curtidas", f"{int(df_filtrado['Curtidas'].mean()):,}")
                    col5.metric("Engajamento Global", f"{taxa_global:.2f}%")

                    st.markdown("---")

                    # Gráficos em Abas
                    aba1, aba2, aba3, aba4 = st.tabs([
                        "🔥 Mapa de Calor (Dia x Hora)", 
                        "⏰ Média por Horário", 
                        "📅 Média por Dia", 
                        "📈 Engajamento"
                    ])

                    with aba1:
                        st.markdown("#### Média de Views por Combinação de Dia da Semana e Horário")
                        # Prepara matriz pivô para o Heatmap
                        df_pivot = df_filtrado.pivot_table(
                            index='Dia da Semana', 
                            columns='Hora_Cheia', 
                            values='Visualizações', 
                            aggfunc='mean'
                        ).reindex(ordem_dias).dropna(how='all')

                        fig_heatmap = px.imshow(
                            df_pivot,
                            labels=dict(x="Horário do Upload", y="Dia da Semana", color="Média de Views"),
                            x=df_pivot.columns,
                            y=df_pivot.index,
                            color_continuous_scale="Reds",
                            aspect="auto"
                        )
                        fig_heatmap.update_layout(template="plotly_white")
                        st.plotly_chart(fig_heatmap, use_container_width=True)

                    with aba2:
                        fig_hora = px.bar(
                            media_hora.sort_values(by='Hora_Cheia'), 
                            x='Hora_Cheia', y='Visualizações',
                            title="Média de Visualizações por Horário (Horário de Brasília)",
                            color_discrete_sequence=['#FF0000']
                        )
                        fig_hora.update_layout(template="plotly_white")
                        st.plotly_chart(fig_hora, use_container_width=True)

                    with aba3:
                        media_dia_ord = media_dia.set_index('Dia da Semana').reindex(ordem_dias).dropna().reset_index()
                        fig_dia = px.bar(
                            media_dia_ord, 
                            x='Dia da Semana', y='Visualizações',
                            title="Média de Visualizações por Dia da Semana",
                            color_discrete_sequence=['#1E88E5']
                        )
                        fig_dia.update_layout(template="plotly_white")
                        st.plotly_chart(fig_dia, use_container_width=True)

                    with aba4:
                        fig_eng_single = px.box(
                            df_filtrado, 
                            y='Taxa Engajamento (%)',
                            points="all",
                            title="Taxa de Engajamento por Short (% Curtidas/Views)",
                            color_discrete_sequence=['#2E7D32']
                        )
                        fig_eng_single.update_layout(template="plotly_white")
                        st.plotly_chart(fig_eng_single, use_container_width=True)

                    # Tabela detalhada
                    st.subheader("📋 Tabela Detalhada")
                    st.dataframe(
                        df_filtrado[['Título', 'Data', 'Dia da Semana', 'Hora_Cheia', 'Visualizações', 'Curtidas', 'Taxa Engajamento (%)', 'URL']], 
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"Erro ao carregar o canal: {e}")
        else:
            st.info("Digite o ID de um canal na barra lateral para começar.")

    # =========================================================
    # MODALIDADE 2: COMPARAR 2 CANAIS
    # =========================================================
    elif modo_app == "⚔️ Comparar 2 Canais":
        st.sidebar.markdown("---")
        id_canal1 = st.sidebar.text_input("ID do Canal 1:")
        id_canal2 = st.sidebar.text_input("ID do Canal 2:")

        if id_canal1 and id_canal2:
            try:
                with st.spinner('Comparando canais...'):
                    nome1, df1 = buscar_dados_canal(youtube, id_canal1, max_results)
                    nome2, df2 = buscar_dados_canal(youtube, id_canal2, max_results)

                if df1 is None or df2 is None:
                    st.error("Um ou ambos os IDs digitados são inválidos.")
                else:
                    st.subheader(f"⚔️ Comparativo: **{nome1}** vs **{nome2}**")

                    v1, l1 = df1['Visualizações'].sum(), df1['Curtidas'].sum()
                    taxa_global1 = (l1 / v1 * 100) if v1 > 0 else 0.0

                    v2, l2 = df2['Visualizações'].sum(), df2['Curtidas'].sum()
                    taxa_global2 = (l2 / v2 * 100) if v2 > 0 else 0.0

                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        st.markdown(f"### 🔴 {nome1}")
                        st.metric("Média de Views", f"{int(df1['Visualizações'].mean()):,}")
                        st.metric("Taxa de Engajamento Global", f"{taxa_global1:.2f}%")
                    
                    with col_c2:
                        st.markdown(f"### 🔵 {nome2}")
                        st.metric("Média de Views", f"{int(df2['Visualizações'].mean()):,}")
                        st.metric("Taxa de Engajamento Global", f"{taxa_global2:.2f}%")

                    st.markdown("---")

                    df_comb = pd.concat([df1, df2])

                    # Gráfico Comparativo 1: Horários
                    st.markdown("### ⏰ Média de Views por Horário")
                    media_hora_comb = df_comb.groupby(['Canal', 'Hora_Cheia'])['Visualizações'].mean().reset_index()
                    fig_comp_hora = px.bar(
                        media_hora_comb, 
                        x='Hora_Cheia', y='Visualizações', color='Canal', barmode='group',
                        color_discrete_sequence=['#FF0000', '#1E88E5']
                    )
                    fig_comp_hora.update_layout(template="plotly_white")
                    st.plotly_chart(fig_comp_hora, use_container_width=True)

                    # Gráfico Comparativo 2: Dias da Semana
                    st.markdown("### 📅 Média de Views por Dia da Semana")
                    media_dia_comb = df_comb.groupby(['Canal', 'Dia da Semana'])['Visualizações'].mean().reset_index()
                    fig_comp_dia = px.bar(
                        media_dia_comb, 
                        x='Dia da Semana', y='Visualizações', color='Canal', barmode='group',
                        category_orders={'Dia da Semana': ordem_dias},
                        color_discrete_sequence=['#FF0000', '#1E88E5']
                    )
                    fig_comp_dia.update_layout(template="plotly_white")
                    st.plotly_chart(fig_comp_dia, use_container_width=True)

                    # Gráfico Comparativo 3: Boxplot de Engajamento
                    st.markdown("### 📊 Comparativo da Taxa de Engajamento por Short (%)")
                    fig_eng = px.box(
                        df_comb, 
                        x='Canal', 
                        y='Taxa Engajamento (%)', 
                        color='Canal',
                        points="all",
                        title="Distribuição do Engajamento por Vídeo (Curtidas / Views)",
                        color_discrete_sequence=['#FF0000', '#1E88E5']
                    )
                    fig_eng.update_layout(template="plotly_white")
                    st.plotly_chart(fig_eng, use_container_width=True)

            except Exception as e:
                st.error(f"Erro ao comparar canais: {e}")
        else:
            st.info("Digite os IDs de dois canais na barra lateral para ver o comparativo.")

else:
    st.error("Chave de API não configurada.")
