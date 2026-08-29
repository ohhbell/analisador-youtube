import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from googleapiclient.discovery import build

# =========================================================
# CONFIGURAÇÃO E ESTILIZAÇÃO PREMIUM (TAILWIND/DARK STYLE)
# =========================================================
st.set_page_config(
    page_title="YouTube Shorts Analytics Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Injeção de CSS para um visual Premium
st.markdown(
    """
    <style>
        /* Fundo Geral e Tipografia */
        .stApp {
            background-color: #0f172a;
            color: #f8fafc;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }
        
        /* Ocultar elementos nativos desnecessários */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Estilização dos Cards por Dia */
        .day-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .day-card:hover {
            border-color: #6366f1;
            transform: translateY(-2px);
        }
        
        /* Títulos dos Cards */
        .day-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
            padding-bottom: 12px;
            margin-bottom: 16px;
        }
        .day-name {
            font-size: 1.25rem;
            font-weight: 700;
            color: #f8fafc;
            margin: 0;
        }
        .day-badge {
            background-color: #312e81;
            color: #818cf8;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        /* Métricas dentro do Card */
        .metric-row {
            margin-bottom: 12px;
        }
        .metric-label {
            font-size: 0.8rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 2px;
        }
        .metric-value {
            font-size: 1rem;
            font-weight: 600;
            color: #e2e8f0;
        }
        .highlight-accent {
            color: #38bdf8;
        }
        .highlight-green {
            color: #4ade80;
        }
        .highlight-amber {
            color: #fbbf24;
        }
        
        /* Caixa de Resumo do Padrão */
        .pattern-summary {
            background-color: #1e1b4b;
            border-left: 4px solid #6366f1;
            padding: 10px 14px;
            border-radius: 0 8px 8px 0;
            font-size: 0.875rem;
            color: #c7d2fe;
            margin-top: 14px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Dicionários de Suporte
dias_semana_pt = {
    'Monday': 'Segunda-feira',
    'Tuesday': 'Terça-feira',
    'Wednesday': 'Quarta-feira',
    'Thursday': 'Quinta-feira',
    'Friday': 'Sexta-feira',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo',
}

ordem_dias = [
    'Segunda-feira',
    'Terça-feira',
    'Quarta-feira',
    'Quinta-feira',
    'Sexta-feira',
    'Sábado',
    'Domingo',
]

api_key = st.secrets.get('YOUTUBE_API_KEY')


# --- FUNÇÃO PRINCIPAL DE COLETA DE DADOS ---
def buscar_dados_canal(youtube_api, channel_id, max_results):
  res = (
      youtube_api.channels()
      .list(id=channel_id, part='contentDetails,snippet')
      .execute()
  )
  if not res['items']:
    return None, None

  nome_canal = res['items'][0]['snippet']['title']
  playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

  playlist_res = (
      youtube_api.playlistItems()
      .list(playlistId=playlist_id, part='snippet', maxResults=max_results)
      .execute()
  )

  video_ids = [
      item['snippet']['resourceId']['videoId'] for item in playlist_res['items']
  ]

  stats_res = (
      youtube_api.videos()
      .list(id=','.join(video_ids), part='snippet,statistics')
      .execute()
  )

  dados = []
  for item in stats_res['items']:
    data_utc = pd.to_datetime(item['snippet']['publishedAt'])
    data_br = data_utc.tz_convert('America/Sao_Paulo')

    views = int(item['statistics'].get('viewCount', 0))
    likes = int(item['statistics'].get('likeCount', 0))

    taxa_eng = (likes / views * 100) if views > 0 else 0.0

    # Minutos totais do dia para cálculo de consistência/desvio
    minutos_do_dia = data_br.hour * 60 + data_br.minute

    dados.append({
        'Canal': nome_canal,
        'Título': item['snippet']['title'],
        'Data': data_br.date(),
        'Dia da Semana': dias_semana_pt[data_br.strftime('%A')],
        'Hora_Cheia': f'{data_br.hour:02d}:00',
        'Hora_Exata': data_br.strftime('%H:%M'),
        'Minutos_Dia': minutos_do_dia,
        'Visualizações': views,
        'Curtidas': likes,
        'Taxa Engajamento (%)': round(taxa_eng, 2),
        'Comentários': int(item['statistics'].get('commentCount', 0)),
        'URL': f"https://www.youtube.com/shorts/{item['id']}",
    })

  return nome_canal, pd.DataFrame(dados)


# --- NAVEGAÇÃO LATERAL ---
st.sidebar.title('⚡ Analytics Pro')
modo_app = st.sidebar.radio(
    'Selecione a ferramenta:',
    ['Análise Única + Insights', '⚔️ Comparar 2 Canais'],
)
max_results = st.sidebar.slider(
    'Quantidade de vídeos por canal:', 10, 100, 50, step=10
)

if api_key:
  youtube = build('youtube', 'v3', developerKey=api_key)

  if modo_app == 'Análise Única + Insights':
    channel_id = st.sidebar.text_input('ID do Canal (ex: UCxxxx...):')

    if channel_id:
      try:
        with st.spinner('Buscando e analisando dados do canal...'):
          nome_canal, df = buscar_dados_canal(
              youtube, channel_id, max_results
          )

        if df is None:
          st.error('Canal não encontrado. Verifique o ID fornecido.')
        else:
          st.title(f'📊 Painel: **{nome_canal}**')

          # Filtro de Período
          st.sidebar.markdown('---')
          data_min, data_max = df['Data'].min(), df['Data'].max()
          data_inicio, data_fim = st.sidebar.date_input(
              'Filtrar Período:',
              value=(data_min, data_max),
              min_value=data_min,
              max_value=data_max,
          )
          df_filtrado = df[
              (df['Data'] >= data_inicio) & (df['Data'] <= data_fim)
          ]

          # Cards Principais de Métricas Top-Level
          st.markdown('### 📌 Visão Geral do Canal')
          tot_views = df_filtrado['Visualizações'].sum()
          tot_likes = df_filtrado['Curtidas'].sum()
          taxa_global = (tot_likes / tot_views * 100) if tot_views > 0 else 0.0

          c1, c2, c3, c4, c5 = st.columns(5)
          c1.metric('Shorts Analisados', len(df_filtrado))
          c2.metric('Total de Views', f"{df_filtrado['Visualizações'].sum():,}")
          c3.metric(
              'Média de Views', f"{int(df_filtrado['Visualizações'].mean()):,}"
          )
          c4.metric(
              'Média de Likes', f"{int(df_filtrado['Curtidas'].mean()):,}"
          )
          c5.metric('Engajamento Médio', f'{taxa_global:.2f}%')

          st.markdown('---')

          # ESTRUTURA DE ABAS
          aba_padrao, aba_agenda, aba_heat, aba_horarios, aba_dias, aba_tabela = (
              st.tabs([
                  '🗓️ Padrão por Dia da Semana',
                  '📅 Agenda Semanal',
                  '🔥 Mapa de Calor (Dia x Hora)',
                  '⏰ Média por Horário',
                  '📊 Média por Dia',
                  '📋 Todos os Vídeos',
              ])
          )

          # =========================================================
          # ABA 1: PADRÃO POR DIA DA SEMANA (CARDS PREMIUM)
          # =========================================================
          with aba_padrao:
            st.markdown(
                '### 📅 Padrão & Consistência de Postagens por Dia da Semana'
            )
            st.write(
                'Esta análise calcula a frequência de publicação, o melhor'
                ' engajamento atingido (Views/Likes), a variação (desvio'
                ' padrão) dos horários de postagem e a média diária.'
            )

            # Criar grid de cards de 2 colunas para exibição dos dias
            cols_grid = st.columns(2)

            for idx, dia in enumerate(ordem_dias):
              df_dia = df_filtrado[df_filtrado['Dia da Semana'] == dia]

              if not df_dia.empty:
                qtd_posts = len(df_dia)

                # Horário Mais Frequente
                freq_hora = df_dia['Hora_Cheia'].mode()
                hora_frequente = (
                    freq_hora.iloc[0] if not freq_hora.empty else 'N/A'
                )
                qtd_freq = (df_dia['Hora_Cheia'] == hora_frequente).sum()

                # Melhor Engajamento (com base em Likes ou Views)
                melhor_video = df_dia.sort_values(
                    by='Curtidas', ascending=False
                ).iloc[0]
                melhor_hora_eng = melhor_video['Hora_Cheia']
                melhor_likes = melhor_video['Curtidas']
                melhor_views = melhor_video['Visualizações']

                # Consistência (Desvio padrão em minutos)
                if len(df_dia) > 1:
                  desvio_min = int(np.std(df_dia['Minutos_Dia']))
                  if desvio_min <= 60:
                    status_consist = f'±{desvio_min}min • Alta consistência'
                  elif desvio_min <= 180:
                    status_consist = f'±{desvio_min}min • Consistência média'
                  else:
                    status_consist = f'±{desvio_min}min • Bem variável'
                else:
                  desvio_min = 0
                  status_consist = 'Único registro'

                # Médias do Dia
                media_likes_dia = int(df_dia['Curtidas'].mean())
                media_views_dia = int(df_dia['Visualizações'].mean())

                # Renderização HTML do Card Premium
                card_html = f"""
                                <div class="day-card">
                                    <div class="day-header">
                                        <h3 class="day-name">{dia}</h3>
                                        <span class="day-badge">{qtd_posts} posts</span>
                                    </div>
                                    <div class="metric-row">
                                        <div class="metric-label">Horário Mais Frequente</div>
                                        <div class="metric-value highlight-accent">{hora_frequente} ({qtd_freq}x)</div>
                                    </div>
                                    <div class="metric-row">
                                        <div class="metric-label">Melhor Engajamento</div>
                                        <div class="metric-value highlight-green">{melhor_hora_eng} • {melhor_likes:,} likes ({melhor_views:,} views)</div>
                                    </div>
                                    <div class="metric-row">
                                        <div class="metric-label">Consistência de Horário</div>
                                        <div class="metric-value highlight-amber">{status_consist}</div>
                                    </div>
                                    <div class="metric-row">
                                        <div class="metric-label">Média do Dia</div>
                                        <div class="metric-value">{media_views_dia:,} views • {media_likes_dia:,} likes</div>
                                    </div>
                                    <div class="pattern-summary">
                                        💡 <b>Resumo:</b> {dia[:3]}: posta comumente às {hora_frequente} ({status_consist.lower()}), melhor engajamento às {melhor_hora_eng}.
                                    </div>
                                </div>
                                """

                # Distribuição alternada nas colunas do Streamlit
                col_destino = cols_grid[idx % 2]
                col_destino.markdown(card_html, unsafe_allow_html=True)
              else:
                # Caso não haja posts no dia
                card_html_vazio = f"""
                                <div class="day-card" style="opacity: 0.5;">
                                    <div class="day-header">
                                        <h3 class="day-name">{dia}</h3>
                                        <span class="day-badge" style="background-color: #334155; color: #94a3b8;">0 posts</span>
                                    </div>
                                    <p style="color: #64748b; margin: 0;">Nenhum short publicado neste dia no período selecionado.</p>
                                </div>
                                """
                cols_grid[idx % 2].markdown(
                    card_html_vazio, unsafe_allow_html=True
                )

          # =========================================================
          # ABA 2: AGENDA SEMANAL
          # =========================================================
          with aba_agenda:
            st.markdown(
                '### 📌 Horários Identificados por Dia da Semana (Tabela)'
            )
            agenda_df = (
                df_filtrado.groupby(['Dia da Semana', 'Hora_Cheia'])
                .agg(
                    Qtd_Videos=('Visualizações', 'count'),
                    Media_Views=(
                        'Visualizações',
                        lambda x: int(x.mean()),
                    ),
                    Media_Likes=('Curtidas', lambda x: int(x.mean())),
                )
                .reset_index()
            )

            agenda_df['Dia_Ordem'] = agenda_df['Dia da Semana'].map(
                lambda d: ordem_dias.index(d) if d in ordem_dias else 99
            )
            agenda_df = agenda_df.sort_values(
                by=['Dia_Ordem', 'Hora_Cheia']
            ).drop(columns=['Dia_Ordem'])
            agenda_df.columns = [
                'Dia da Semana',
                'Horário de Postagem',
                'Vídeos Postados',
                'Média de Views',
                'Média de Likes',
            ]

            st.dataframe(agenda_df, use_container_width=True)

          # =========================================================
          # ABA 3: MAPA DE CALOR (HEATMAP)
          # =========================================================
          with aba_heat:
            st.markdown(
                '### 🔥 Média de Visualizações por Combinação (Dia x Horário)'
            )
            df_pivot = (
                df_filtrado.pivot_table(
                    index='Dia da Semana',
                    columns='Hora_Cheia',
                    values='Visualizações',
                    aggfunc='mean',
                )
                .reindex(ordem_dias)
                .dropna(how='all')
            )

            fig_heatmap = px.imshow(
                df_pivot,
                labels=dict(
                    x='Horário', y='Dia da Semana', color='Média Views'
                ),
                x=df_pivot.columns,
                y=df_pivot.index,
                color_continuous_scale='Purples',
                aspect='auto',
            )
            fig_heatmap.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

          # =========================================================
          # ABA 4: MÉDIA POR HORÁRIO
          # =========================================================
          with aba_horarios:
            media_hora = (
                df_filtrado.groupby('Hora_Cheia')['Visualizações']
                .mean()
                .reset_index()
            )
            fig_hora = px.bar(
                media_hora.sort_values(by='Hora_Cheia'),
                x='Hora_Cheia',
                y='Visualizações',
                title='Média de Visualizações por Horário (Horário de Brasília)',
                color_discrete_sequence=['#6366f1'],
            )
            fig_hora.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_hora, use_container_width=True)

          # =========================================================
          # ABA 5: MÉDIA POR DIA
          # =========================================================
          with aba_dias:
            media_dia = (
                df_filtrado.groupby('Dia da Semana')['Visualizações']
                .mean()
                .reset_index()
            )
            media_dia_ord = (
                media_dia.set_index('Dia da Semana')
                .reindex(ordem_dias)
                .dropna()
                .reset_index()
            )
            fig_dia = px.bar(
                media_dia_ord,
                x='Dia da Semana',
                y='Visualizações',
                title='Média de Visualizações por Dia da Semana',
                color_discrete_sequence=['#38bdf8'],
            )
            fig_dia.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_dia, use_container_width=True)

          # =========================================================
          # ABA 6: DADOS BRUTOS
          # =========================================================
          with aba_tabela:
            st.subheader('📋 Dados Detalhados dos Shorts')
            st.dataframe(
                df_filtrado[[
                    'Título',
                    'Data',
                    'Dia da Semana',
                    'Hora_Cheia',
                    'Visualizações',
                    'Curtidas',
                    'Taxa Engajamento (%)',
                    'URL',
                ]],
                use_container_width=True,
            )

      except Exception as e:
        st.error(f'Erro ao processar o canal: {e}')
    else:
      st.info('Digite um ID de canal válido na barra lateral.')

  # =========================================================
  # MODALIDADE 2: COMPARAR 2 CANAIS
  # =========================================================
  elif modo_app == '⚔️ Comparar 2 Canais':
    st.sidebar.markdown('---')
    id_canal1 = st.sidebar.text_input('ID do Canal 1:')
    id_canal2 = st.sidebar.text_input('ID do Canal 2:')

    if id_canal1 and id_canal2:
      try:
        with st.spinner('Processando dados comparativos...'):
          nome1, df1 = buscar_dados_canal(youtube, id_canal1, max_results)
          nome2, df2 = buscar_dados_canal(youtube, id_canal2, max_results)

        if df1 is None or df2 is None:
          st.error('Um ou ambos os IDs informados são inválidos.')
        else:
          st.title(f'⚔️ Comparativo: **{nome1}** vs **{nome2}**')

          v1, l1 = df1['Visualizações'].sum(), df1['Curtidas'].sum()
          taxa1 = (l1 / v1 * 100) if v1 > 0 else 0.0

          v2, l2 = df2['Visualizações'].sum(), df2['Curtidas'].sum()
          taxa2 = (l2 / v2 * 100) if v2 > 0 else 0.0

          col_c1, col_c2 = st.columns(2)
          with col_c1:
            st.markdown(f'### 🟣 {nome1}')
            st.metric(
                'Média de Views', f"{int(df1['Visualizações'].mean()):,}"
            )
            st.metric('Taxa Engajamento Global', f'{taxa1:.2f}%')

          with col_c2:
            st.markdown(f'### 🔵 {nome2}')
            st.metric(
                'Média de Views', f"{int(df2['Visualizações'].mean()):,}"
            )
            st.metric('Taxa Engajamento Global', f'{taxa2:.2f}%')

          st.markdown('---')
          df_comb = pd.concat([df1, df2])

          # Gráfico Comparativo de Horários
          st.markdown('### ⏰ Comparativo de Views por Horário')
          media_hora_comb = (
              df_comb.groupby(['Canal', 'Hora_Cheia'])['Visualizações']
              .mean()
              .reset_index()
          )
          fig_comp_hora = px.bar(
              media_hora_comb,
              x='Hora_Cheia',
              y='Visualizações',
              color='Canal',
              barmode='group',
              color_discrete_sequence=['#818cf8', '#38bdf8'],
          )
          fig_comp_hora.update_layout(
              template='plotly_dark',
              paper_bgcolor='rgba(0,0,0,0)',
              plot_bgcolor='rgba(0,0,0,0)',
          )
          st.plotly_chart(fig_comp_hora, use_container_width=True)

      except Exception as e:
        st.error(f'Erro ao comparar canais: {e}')
    else:
      st.info('Forneça os IDs de dois canais para realizar a comparação.')

else:
  st.error('Chave de API não configurada em secrets.toml.')
