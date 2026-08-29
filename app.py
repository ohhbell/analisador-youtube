import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from googleapiclient.discovery import build

# =========================================================
# CONFIGURAÇÃO DE PÁGINA E CSS (EXATAMENTE COMO NA IMAGEM)
# =========================================================
st.set_page_config(
    page_title="Analisador de Horários",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        /* Fundo Geral Ultra Escuro */
        .stApp {
            background-color: #0c0c0e !important;
            color: #a1a1aa !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        /* Ocultar elementos nativos do Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display:none;}
        
        /* Cabeçalho Superior do App */
        .app-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 0 25px 0;
        }
        .app-title-box {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .avatar-green {
            background-color: #16a34a;
            color: #ffffff;
            font-weight: bold;
            font-size: 1.1rem;
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .header-text h2 {
            color: #f4f4f5 !important;
            font-size: 1.15rem !important;
            font-weight: 600 !important;
            margin: 0 !important;
            line-height: 1.2;
        }
        .header-text p {
            color: #71717a !important;
            font-size: 0.8rem !important;
            margin: 0 !important;
        }

        /* Card de Comportamento Geral */
        .general-card {
            background-color: #141417;
            border: 1px solid #27272a;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }
        .general-subtitle {
            font-size: 0.7rem;
            font-weight: 700;
            color: #71717a;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }
        .general-desc {
            color: #e4e4e7;
            font-size: 0.95rem;
            font-weight: 500;
            margin-bottom: 16px;
        }
        .general-metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
        }
        .submetric-box {
            background-color: #0c0c0e;
            border: 1px solid #27272a;
            border-radius: 8px;
            padding: 12px 14px;
        }
        .submetric-label {
            font-size: 0.7rem;
            color: #71717a;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .submetric-value {
            font-size: 1rem;
            font-weight: 700;
            color: #f4f4f5;
        }

        /* Título da Seção Padrão por Dia */
        .section-header {
            margin-top: 10px;
            margin-bottom: 16px;
        }
        .section-header h3 {
            color: #f4f4f5 !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            margin: 0 0 4px 0 !important;
        }
        .section-header p {
            color: #71717a !important;
            font-size: 0.8rem !important;
            margin: 0 !important;
        }

        /* Estilização dos Cards por Dia da Semana */
        .day-card {
            background-color: #141417;
            border: 1px solid #242427;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 16px;
            min-height: 220px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .day-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }
        .day-title {
            color: #f4f4f5;
            font-size: 0.95rem;
            font-weight: 600;
            margin: 0;
        }
        .day-badge-green {
            background-color: #052e16;
            color: #22c55e;
            border: 1px solid #14532d;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        /* Linhas de Métricas no Card */
        .metric-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.82rem;
            margin-bottom: 8px;
        }
        .metric-name {
            color: #71717a;
        }
        .metric-val {
            color: #e4e4e7;
            font-weight: 500;
        }
        .text-green {
            color: #22c55e !important;
            font-weight: 600;
        }

        /* Footer do Card com o resumo em texto */
        .card-footer-summary {
            font-size: 0.75rem;
            color: #71717a;
            border-top: 1px dashed #27272a;
            padding-top: 10px;
            margin-top: 6px;
        }

        /* Customização de Tabs do Streamlit para o Estilo Pill Dark */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
            margin-bottom: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 34px;
            background-color: #18181b;
            border: 1px solid #27272a;
            border-radius: 8px;
            color: #a1a1aa;
            font-size: 0.85rem;
            font-weight: 500;
            padding: 0 16px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #f4f4f5 !important;
            color: #09090b !important;
            font-weight: 600 !important;
            border-color: #f4f4f5 !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Dicionários e constantes
dias_semana_pt = {
    "Monday": "Segunda",
    "Tuesday": "Terça",
    "Wednesday": "Quarta",
    "Thursday": "Quinta",
    "Friday": "Sexta",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
}

ordem_dias = [
    "Domingo",
    "Segunda",
    "Terça",
    "Quarta",
    "Quinta",
    "Sexta",
    "Sábado",
]

api_key = st.secrets.get("YOUTUBE_API_KEY")


# --- COLETA DE DADOS ---
def buscar_dados_canal(youtube_api, channel_id, max_results):
  res = (
      youtube_api.channels()
      .list(id=channel_id, part="contentDetails,snippet")
      .execute()
  )
  if not res["items"]:
    return None, None

  nome_canal = res["items"][0]["snippet"]["title"]
  playlist_id = res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

  playlist_res = (
      youtube_api.playlistItems()
      .list(playlistId=playlist_id, part="snippet", maxResults=max_results)
      .execute()
  )

  video_ids = [
      item["snippet"]["resourceId"]["videoId"] for item in playlist_res["items"]
  ]

  stats_res = (
      youtube_api.videos()
      .list(id=",".join(video_ids), part="snippet,statistics")
      .execute()
  )

  dados = []
  for item in stats_res["items"]:
    data_utc = pd.to_datetime(item["snippet"]["publishedAt"])
    data_br = data_utc.tz_convert("America/Sao_Paulo")

    views = int(item["statistics"].get("viewCount", 0))
    likes = int(item["statistics"].get("likeCount", 0))
    taxa_eng = (likes / views * 100) if views > 0 else 0.0

    minutos_do_dia = data_br.hour * 60 + data_br.minute

    dados.append({
        "Canal": nome_canal,
        "Título": item["snippet"]["title"],
        "Data": data_br.date(),
        "Dia da Semana": dias_semana_pt[data_br.strftime("%A")],
        "Hora_Cheia": f"{data_br.hour:02d}h",
        "Hora_Num": data_br.hour,
        "Minutos_Dia": minutos_do_dia,
        "Visualizações": views,
        "Curtidas": likes,
        "Taxa Engajamento (%)": round(taxa_eng, 2),
        "URL": f"https://www.youtube.com/shorts/{item['id']}",
    })

  return nome_canal, pd.DataFrame(dados)


# --- LAYOUT SUPERIOR (HEADER ESTILO SAAS) ---
st.markdown(
    """
    <div class="app-header">
        <div class="app-title-box">
            <div class="avatar-green">A</div>
            <div class="header-text">
                <h2>Analisador de Horários</h2>
                <p>Descubra quando seu público engaja mais</p>
            </div>
        </div>
        <div style="font-size: 0.75rem; color: #22c55e; display: flex; align-items: center; gap: 6px;">
            <span style="height: 8px; width: 8px; background-color: #22c55e; border-radius: 50%; display: inline-block;"></span>
            client-side • token local
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# BARRA LATERAL PARA CONTROLES
st.sidebar.title("⚙️ Configurações")
modo_app = st.sidebar.radio(
    "Navegação:", ["Análise Única", "⚔️ Comparativo"]
)
max_results = st.sidebar.slider("Vídeos para analisar:", 10, 100, 50, step=10)

if api_key:
  youtube = build("youtube", "v3", developerKey=api_key)

  if modo_app == "Análise Única":
    channel_id = st.sidebar.text_input("ID do Canal:")

    if channel_id:
      try:
        with st.spinner("Buscando dados..."):
          nome_canal, df = buscar_dados_canal(
              youtube, channel_id, max_results
          )

        if df is None:
          st.error("Canal não encontrado.")
        else:
          # Filtro de Período
          data_min, data_max = df["Data"].min(), df["Data"].max()
          data_inicio, data_fim = st.sidebar.date_input(
              "Período:",
              value=(data_min, data_max),
              min_value=data_min,
              max_value=data_max,
          )
          df_filtrado = df[
              (df["Data"] >= data_inicio) & (df["Data"] <= data_fim)
          ]

          # ABAS DE NAVEGAÇÃO SUPERIORES
          tab_geral, tab_padrao, tab_insights, tab_tabela = st.tabs([
              "Visão Geral",
              "Padrão por Dia",
              "Insights Cruzados",
              "Tabela de Vídeos",
          ])

          # =========================================================
          # ABA 1: VISÃO GERAL + COMPORTAMENTO GERAL
          # =========================================================
          with tab_geral:
            st.markdown("### 📊 Visão Geral da Conta")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Shorts Analisados", len(df_filtrado))
            c2.metric("Total de Views", f"{df_filtrado['Visualizações'].sum():,}")
            c3.metric(
                "Média de Views", f"{int(df_filtrado['Visualizações'].mean()):,}"
            )
            c4.metric(
                "Média de Likes", f"{int(df_filtrado['Curtidas'].mean()):,}"
            )

            fig_bar = px.bar(
                df_filtrado.groupby("Hora_Cheia")["Visualizações"]
                .mean()
                .reset_index(),
                x="Hora_Cheia",
                y="Visualizações",
                title="Média de Views por Horário",
                color_discrete_sequence=["#22c55e"],
            )
            fig_bar.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_bar, use_container_width=True)

          # =========================================================
          # ABA 2: PADRÃO POR DIA (ESTILO EXATO DA SUGESTÃO/IMAGEM)
          # =========================================================
          with tab_padrao:
            # Cálculos do Card "COMPORTAMENTO GERAL"
            total_posts = len(df_filtrado)

            # Janela mais frequente
            df_filtrado["Faixa_Horario"] = pd.cut(
                df_filtrado["Hora_Num"],
                bins=[-1, 5, 8, 12, 17, 21, 24],
                labels=[
                    "00h–05h",
                    "06h–08h",
                    "09h–12h",
                    "13h–17h",
                    "18h–21h",
                    "22h–23h",
                ],
            )
            faixa_top = df_filtrado["Faixa_Horario"].mode()
            faixa_str = faixa_top.iloc[0] if not faixa_top.empty else "09h–12h"
            posts_faixa = (df_filtrado["Faixa_Horario"] == faixa_str).sum()
            pct_faixa = int((posts_faixa / total_posts) * 100)

            # Horário Pico
            hora_pico = df_filtrado["Hora_Cheia"].mode()
            hora_pico_str = hora_pico.iloc[0] if not hora_pico.empty else "10h"

            # 1. RENDERIZAR CARD COMPORTAMENTO GERAL
            st.markdown(
                f"""
                            <div class="general-card">
                                <div class="general-subtitle">Comportamento Geral</div>
                                <div class="general-desc">
                                    Essa conta posta <b>{pct_faixa}% das vezes entre {faixa_str}</b> de Seg a Sex, com foco em Shorts às <b>{hora_pico_str}</b>.
                                </div>
                                <div class="general-metrics-grid">
                                    <div class="submetric-box">
                                        <div class="submetric-label">Janela {pct_faixa}%</div>
                                        <div class="submetric-value">{faixa_str}</div>
                                    </div>
                                    <div class="submetric-box">
                                        <div class="submetric-label">Cobertura</div>
                                        <div class="submetric-value">{pct_faixa}% dos posts</div>
                                    </div>
                                    <div class="submetric-box">
                                        <div class="submetric-label">Intervalo Médio</div>
                                        <div class="submetric-value">4.5h</div>
                                    </div>
                                    <div class="submetric-box">
                                        <div class="submetric-label">Foco</div>
                                        <div class="submetric-value">Shorts • {total_posts} posts</div>
                                    </div>
                                </div>
                            </div>
                            """,
                unsafe_allow_html=True,
            )

            # Título da Subseção
            st.markdown(
                """
                            <div class="section-header">
                                <h3>Padrão por Dia da Semana</h3>
                                <p>Para cada dia, horário mais frequente, melhor engajamento, consistência e total</p>
                            </div>
                            """,
                unsafe_allow_html=True,
            )

            # 2. RENDERIZAR GRID 3 COLUNAS COM CARDS DIÁRIOS
            col1, col2, col3 = st.columns(3)
            colunas_grid = [col1, col2, col3]

            for idx, dia in enumerate(ordem_dias):
              df_dia = df_filtrado[df_filtrado["Dia da Semana"] == dia]
              col_alvo = colunas_grid[idx % 3]

              if not df_dia.empty:
                qtd_posts = len(df_dia)

                # Horário Mais Frequente
                freq_hora = df_dia["Hora_Cheia"].mode()
                hora_freq = freq_hora.iloc[0] if not freq_hora.empty else "N/A"
                qtd_freq = (df_dia["Hora_Cheia"] == hora_freq).sum()

                # Melhor Engajamento (Likes)
                melhor_vid = df_dia.sort_values(
                    by="Curtidas", ascending=False
                ).iloc[0]
                melhor_hora = melhor_vid["Hora_Cheia"]
                melhor_likes = melhor_vid["Curtidas"]

                # Consistência (Desvio padrão em min)
                if qtd_posts > 1:
                  desvio_min = int(np.std(df_dia["Minutos_Dia"]))
                  status_consist = f"±{desvio_min}min • Bem variável"
                else:
                  status_consist = "Frequência Única"

                # Média Likes
                media_likes = int(df_dia["Curtidas"].mean())

                # Card HTML idêntico ao layout escuro da imagem
                card_html = f"""
                                <div class="day-card">
                                    <div>
                                        <div class="day-header">
                                            <span class="day-title">{dia}</span>
                                            <span class="day-badge-green">{qtd_posts} posts</span>
                                        </div>
                                        <div class="metric-item">
                                            <span class="metric-name">Mais frequente</span>
                                            <span class="metric-val">{hora_freq} ({qtd_freq}x)</span>
                                        </div>
                                        <div class="metric-item">
                                            <span class="metric-name">Melhor engaj.</span>
                                            <span class="metric-val text-green">{melhor_hora} • {melhor_likes:,} likes</span>
                                        </div>
                                        <div class="metric-item">
                                            <span class="metric-name">Consistência</span>
                                            <span class="metric-val">{status_consist}</span>
                                        </div>
                                        <div class="metric-item">
                                            <span class="metric-name">Média dia</span>
                                            <span class="metric-val">{media_likes:,} likes</span>
                                        </div>
                                    </div>
                                    <div class="card-footer-summary">
                                        {dia[:3].capitalize()}: posta sempre {hora_freq} {status_consist.split('•')[0]}, melhor engajamento {melhor_hora}
                                    </div>
                                </div>
                                """
                col_alvo.markdown(card_html, unsafe_allow_html=True)
              else:
                card_vazio = f"""
                                <div class="day-card" style="opacity: 0.4;">
                                    <div class="day-header">
                                        <span class="day-title">{dia}</span>
                                        <span class="day-badge-green" style="background-color:#18181b; color:#71717a; border:none;">0 posts</span>
                                    </div>
                                    <div class="card-footer-summary">Sem publicações registradas neste dia.</div>
                                </div>
                                """
                col_alvo.markdown(card_vazio, unsafe_allow_html=True)

          # =========================================================
          # ABA 3: INSIGHTS CRUZADOS (HEATMAP)
          # =========================================================
          with tab_insights:
            st.markdown("### 🔥 Mapa de Calor Cruzado")
            df_pivot = (
                df_filtrado.pivot_table(
                    index="Dia da Semana",
                    columns="Hora_Cheia",
                    values="Visualizações",
                    aggfunc="mean",
                )
                .reindex(ordem_dias)
                .dropna(how="all")
            )

            fig_heat = px.imshow(
                df_pivot,
                labels=dict(
                    x="Horário", y="Dia da Semana", color="Média Views"
                ),
                x=df_pivot.columns,
                y=df_pivot.index,
                color_continuous_scale="Greens",
                aspect="auto",
            )
            fig_heat.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_heat, use_container_width=True)

          # =========================================================
          # ABA 4: TABELA
          # =========================================================
          with tab_tabela:
            st.dataframe(
                df_filtrado[[
                    "Título",
                    "Data",
                    "Dia da Semana",
                    "Hora_Cheia",
                    "Visualizações",
                    "Curtidas",
                    "URL",
                ]],
                use_container_width=True,
            )

      except Exception as e:
        st.error(f"Erro ao carregar canal: {e}")
    else:
      st.info("Digite o ID do canal na barra lateral para começar.")

  elif modo_app == "⚔️ Comparativo":
    st.info("Insira dois IDs na barra lateral para abrir a visão comparativa.")

else:
  st.error("Configure sua YOUTUBE_API_KEY no secrets.toml.")
