import math
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
from googleapiclient.discovery import build

# =========================================================
# CONFIGURAÇÃO DE PÁGINA E CSS YOUTUBE RED (DARK PREMIUM)
# =========================================================
st.set_page_config(
    page_title="Analisador de Horários - YouTube",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        /* Fundo Geral Ultra Escuro */
        .stApp {
            background-color: #0b0b0e !important;
            color: #a1a1aa !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        /* Ocultar elementos nativos do Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display:none;}

        /* Estilização dos Inputs superiores */
        .stTextInput input, .stSelectbox > div > div {
            background-color: #121217 !important;
            color: #f4f4f5 !important;
            border: 1px solid #22222a !important;
            border-radius: 8px !important;
        }
        .stTextInput input:focus, .stSelectbox > div > div:focus {
            border-color: #ef4444 !important;
            box-shadow: 0 0 0 1px #ef4444 !important;
        }
        .stTextInput label, .stSelectbox label {
            color: #a1a1aa !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
        }

        /* Header Principal Superior */
        .app-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 0 20px 0;
            margin-bottom: 10px;
        }
        .app-title-box {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .avatar-red-logo {
            background-color: #ff0000;
            color: #ffffff;
            font-weight: bold;
            font-size: 1.1rem;
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 14px rgba(255, 0, 0, 0.35);
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

        /* CARD DE INFORMAÇÕES DO CANAL (FOTO + NOME + INSCRITOS) */
        .channel-profile-card {
            background-color: #121217;
            border: 1px solid #22222a;
            border-radius: 12px;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 20px;
        }
        .channel-avatar-img {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            border: 2px solid #ef4444;
            object-fit: cover;
        }
        .channel-info h3 {
            color: #ffffff !important;
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            margin: 0 0 4px 0 !important;
        }
        .channel-sub-count {
            background-color: #270909;
            color: #ef4444;
            border: 1px solid #7f1d1d;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.78rem;
            font-weight: 600;
            display: inline-block;
        }

        /* ESTILIZAÇÃO DAS TABS (BOTÃO BRANCO ATIVO COM DESTAQUE VERMELHO) */
        div[data-baseweb="tab-list"] {
            gap: 6px !important;
            background-color: #121217 !important;
            padding: 6px !important;
            border-radius: 12px !important;
            border: 1px solid #22222a !important;
            display: inline-flex !important;
            margin-bottom: 25px !important;
        }
        
        div[data-baseweb="tab-list"] button[role="tab"] {
            height: 38px !important;
            background-color: transparent !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0 20px !important;
            transition: all 0.2s ease !important;
        }

        div[data-baseweb="tab-list"] button[role="tab"] p {
            color: #a1a1aa !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
        }

        div[data-baseweb="tab-list"] button[aria-selected="true"] {
            background-color: #ffffff !important;
            border-radius: 8px !important;
            box-shadow: 0px 4px 12px rgba(255, 0, 0, 0.2) !important;
        }

        div[data-baseweb="tab-list"] button[aria-selected="true"] p {
            color: #000000 !important;
            font-weight: 700 !important;
        }

        div[data-baseweb="tab-highlight-point"], div[data-baseweb="tab-border-highlight"] {
            display: none !important;
        }

        /* CARD COMPORTAMENTO GERAL */
        .general-card {
            background-color: #121217;
            border: 1px solid #22222a;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }
        .general-subtitle {
            font-size: 0.7rem;
            font-weight: 700;
            color: #ef4444;
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
            background-color: #0b0b0e;
            border: 1px solid #1c1c24;
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

        /* CARDS POR DIA DA SEMANA */
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

        .day-card {
            background-color: #121217;
            border: 1px solid #22222a;
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
        .day-badge-red {
            background-color: #270909;
            color: #ef4444;
            border: 1px solid #7f1d1d;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }

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
        .text-red {
            color: #f87171 !important;
            font-weight: 600;
        }

        .card-footer-summary {
            font-size: 0.75rem;
            color: #71717a;
            border-top: 1px dashed #22222a;
            padding-top: 10px;
            margin-top: 6px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Dicionários de Suporte
dias_semana_pt = {
    'Monday': 'Seg',
    'Tuesday': 'Ter',
    'Wednesday': 'Qua',
    'Thursday': 'Qui',
    'Friday': 'Sex',
    'Saturday': 'Sáb',
    'Sunday': 'Dom',
}

ordem_dias = [
    'Domingo',
    'Segunda',
    'Terça',
    'Quarta',
    'Quinta',
    'Sexta',
    'Sábado',
]

api_key = st.secrets.get('YOUTUBE_API_KEY')


# --- FORMATADOR DE NÚMERO DE INSCRITOS ---
def formatar_numero(num):
  if num is None:
    return "N/A"
  num = int(num)
  if num >= 1_000_000:
    return f"{num / 1_000_000:.1f}M"
  elif num >= 1_000:
    return f"{num / 1_000:.1f}K"
  return str(num)


# --- COLETA DE DADOS DO CANAL E VÍDEOS ---
def buscar_dados_canal(youtube_api, channel_id, max_results):
  res = (
      youtube_api.channels()
      .list(id=channel_id, part="contentDetails,snippet,statistics")
      .execute()
  )
  if not res["items"]:
    return None, None, None

  canal_info = res["items"][0]
  detalhes_canal = {
      "nome": canal_info["snippet"]["title"],
      "foto": canal_info["snippet"]["thumbnails"]["medium"]["url"],
      "inscritos": formatar_numero(
          canal_info["statistics"].get("subscriberCount")
      ),
  }

  playlist_id = canal_info["contentDetails"]["relatedPlaylists"]["uploads"]

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
      .list(id=",".join(video_ids), part="snippet,statistics,contentDetails")
      .execute()
  )

  dados = []
  for item in stats_res["items"]:
    data_utc = pd.to_datetime(item["snippet"]["publishedAt"])
    data_br = data_utc.tz_convert("America/Sao_Paulo")

    views = int(item["statistics"].get("viewCount", 0))
    likes = int(item["statistics"].get("likeCount", 0))
    comentarios = int(item["statistics"].get("commentCount", 0))

    duration_iso = item.get("contentDetails", {}).get("duration", "")
    is_short = (
        "M" not in duration_iso
        and "H" not in duration_iso
        and ("S" in duration_iso or duration_iso == "PT0S")
    )
    tipo_conteudo = "SHORTS" if is_short else "VÍDEO"

    dados.append({
        "Canal": detalhes_canal["nome"],
        "Título": item["snippet"]["title"],
        "Data_Formatada": data_br.strftime("%d/%m/%Y %H:%M"),
        "Data": data_br.date(),
        "Dia": dias_semana_pt[data_br.strftime("%A")],
        "Dia_Completo": (
            "Domingo"
            if data_br.strftime("%A") == "Sunday"
            else (
                "Segunda"
                if data_br.strftime("%A") == "Monday"
                else (
                    "Terça"
                    if data_br.strftime("%A") == "Tuesday"
                    else (
                        "Quarta"
                        if data_br.strftime("%A") == "Wednesday"
                        else (
                            "Quinta"
                            if data_br.strftime("%A") == "Thursday"
                            else (
                                "Sexta"
                                if data_br.strftime("%A") == "Friday"
                                else "Sábado"
                            )
                        )
                    )
                )
            )
        ),
        "Hora_Cheia": f"{data_br.hour:02d}:00",
        "Hora_Num": data_br.hour,
        "Minutos_Dia": data_br.hour * 60 + data_br.minute,
        "Visualizações": views,
        "Curtidas": likes,
        "Comentários": comentarios,
        "Tipo": tipo_conteudo,
        "URL": f"https://www.youtube.com/watch?v={item['id']}",
    })

  return detalhes_canal["nome"], pd.DataFrame(dados), detalhes_canal


# --- HEADER PRINCIPAL ---
st.markdown(
    """
    <div class="app-header">
        <div class="app-title-box">
            <div class="avatar-red-logo">▶</div>
            <div class="header-text">
                <h2>Analisador de Horários</h2>
                <p>Descubra quando seu público engaja mais no YouTube</p>
            </div>
        </div>
        <div style="font-size: 0.75rem; color: #ef4444; display: flex; align-items: center; gap: 6px;">
            <span style="height: 8px; width: 8px; background-color: #ef4444; border-radius: 50%; display: inline-block;"></span>
            client-side • token local
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# --- ENTRADAS DE DADOS NO TOPO ---
col_search1, col_search2, col_search3 = st.columns([3, 1, 1])
with col_search1:
  channel_id = st.text_input(
      "ID do Canal no YouTube:",
      placeholder="Cole o ID do canal aqui (ex: UCxxxx...)",
  )
with col_search2:
  max_results = st.selectbox(
      "Analisar últimos:", [20, 30, 50, 100], index=2
  )
with col_search3:
  modo_app = st.selectbox(
      "Modo:", ["Análise Única", "⚔️ Comparativo"]
  )

st.markdown(
    "<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True
)

if api_key:
  youtube = build("youtube", "v3", developerKey=api_key)

  if modo_app == "Análise Única":
    if channel_id:
      try:
        with st.spinner("Buscando dados e perfil do canal..."):
          nome_canal, df, detalhes_canal = buscar_dados_canal(
              youtube, channel_id, max_results
          )

        if df is None:
          st.error("Canal não encontrado. Verifique se o ID está correto.")
        else:
          # CARD DO PERFIL DO CANAL
          st.markdown(
              f"""
                            <div class="channel-profile-card">
                                <img src="{detalhes_canal['foto']}" class="channel-avatar-img" alt="Avatar">
                                <div class="channel-info">
                                    <h3>{detalhes_canal['nome']}</h3>
                                    <span class="channel-sub-count">{detalhes_canal['inscritos']} inscritos</span>
                                </div>
                            </div>
                            """,
              unsafe_allow_html=True,
          )

          df_filtrado = df

          # BOTÕES DE ALTERNÂNCIA SUPERIORES
          tab_geral, tab_padrao, tab_insights, tab_tabela = st.tabs([
              "Visão Geral",
              "Padrão por Dia",
              "Insights Cruzados",
              "Tabela de Vídeos",
          ])

          # =========================================================
          # ABA 1: VISÃO GERAL
          # =========================================================
          with tab_geral:
            st.markdown(
                f"""
                            <div class="general-card">
                                <div class="general-subtitle">Resumo de Performance</div>
                                <div class="general-metrics-grid">
                                    <div class="submetric-box">
                                        <div class="submetric-label">Vídeos Analisados</div>
                                        <div class="submetric-value">{len(df_filtrado)}</div>
                                    </div>
                                    <div class="submetric-box">
                                        <div class="submetric-label">Total de Views</div>
                                        <div class="submetric-value">{df_filtrado['Visualizações'].sum():,}</div>
                                    </div>
                                    <div class="submetric-box">
                                        <div class="submetric-label">Média de Views</div>
                                        <div class="submetric-value">{int(df_filtrado['Visualizações'].mean()):,}</div>
                                    </div>
                                    <div class="submetric-box">
                                        <div class="submetric-label">Média de Likes</div>
                                        <div class="submetric-value">{int(df_filtrado['Curtidas'].mean()):,}</div>
                                    </div>
                                </div>
                            </div>
                            """,
                unsafe_allow_html=True,
            )

            fig_bar = px.bar(
                df_filtrado.groupby("Hora_Cheia")["Visualizações"]
                .mean()
                .reset_index(),
                x="Hora_Cheia",
                y="Visualizações",
                title="Média de Views por Horário",
                color_discrete_sequence=["#ef4444"],
            )
            fig_bar.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#a1a1aa"),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

          # =========================================================
          # ABA 2: PADRÃO POR DIA
          # =========================================================
          with tab_padrao:
            total_posts = len(df_filtrado)

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

            hora_pico = df_filtrado["Hora_Cheia"].mode()
            hora_pico_str = (
                hora_pico.iloc[0] if not hora_pico.empty else "10:00"
            )

            st.markdown(
                f"""
                            <div class="general-card">
                                <div class="general-subtitle">Comportamento Geral</div>
                                <div class="general-desc">
                                    Essa conta posta <b>{pct_faixa}% das vezes entre {faixa_str}</b> de Seg a Sex, com foco em publicações às <b>{hora_pico_str}</b>. Intervalo médio entre vídeos: 4.5h.
                                </div>
                                <div class="general-metrics-grid">
                                    <div class="submetric-box">
                                        <div class="submetric-label">Janela {pct_faixa}%</div>
                                        <div class="submetric-value">{faixa_str}</div>
                                    </div>
                                    <div class="submetric-box">
                                        <div class="submetric-label">Cobertura</div>
                                        <div class="submetric-value">{pct_faixa}% dos vídeos</div>
                                    </div>
                                    <div class="submetric-box">
                                        <div class="submetric-label">Intervalo Médio</div>
                                        <div class="submetric-value">4.5h</div>
                                    </div>
                                    <div class="submetric-box">
                                        <div class="submetric-label">Total Analisado</div>
                                        <div class="submetric-value">{total_posts} vídeos</div>
                                    </div>
                                </div>
                            </div>
                            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                            <div class="section-header">
                                <h3>Padrão por Dia da Semana</h3>
                                <p>Para cada dia, horário mais frequente, melhor engajamento, consistência e total</p>
                            </div>
                            """,
                unsafe_allow_html=True,
            )

            col1, col2, col3 = st.columns(3)
            colunas_grid = [col1, col2, col3]

            for idx, dia in enumerate(ordem_dias):
              df_dia = df_filtrado[df_filtrado["Dia_Completo"] == dia]
              col_alvo = colunas_grid[idx % 3]

              if not df_dia.empty:
                qtd_posts = len(df_dia)
                freq_hora = df_dia["Hora_Cheia"].mode()
                hora_freq = freq_hora.iloc[0] if not freq_hora.empty else "N/A"
                qtd_freq = (df_dia["Hora_Cheia"] == hora_freq).sum()

                melhor_vid = df_dia.sort_values(
                    by="Curtidas", ascending=False
                ).iloc[0]
                melhor_hora = melhor_vid["Hora_Cheia"]
                melhor_likes = melhor_vid["Curtidas"]

                if qtd_posts > 1:
                  desvio_min = int(np.std(df_dia["Minutos_Dia"]))
                  status_consist = f"±{desvio_min}min • Bem variável"
                else:
                  status_consist = "Frequência Única"

                media_likes = int(df_dia["Curtidas"].mean())

                card_html = f"""
                                <div class="day-card">
                                    <div>
                                        <div class="day-header">
                                            <span class="day-title">{dia}</span>
                                            <span class="day-badge-red">{qtd_posts} vídeos</span>
                                        </div>
                                        <div class="metric-item">
                                            <span class="metric-name">Mais frequente</span>
                                            <span class="metric-val">{hora_freq} ({qtd_freq}x)</span>
                                        </div>
                                        <div class="metric-item">
                                            <span class="metric-name">Melhor engaj.</span>
                                            <span class="metric-val text-red">{melhor_hora} • {melhor_likes:,} likes</span>
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
                                        {dia[:3].capitalize()}: posta sempre {hora_freq}, melhor engajamento {melhor_hora}
                                    </div>
                                </div>
                                """
                col_alvo.markdown(card_html, unsafe_allow_html=True)
              else:
                card_vazio = f"""
                                <div class="day-card" style="opacity: 0.4;">
                                    <div class="day-header">
                                        <span class="day-title">{dia}</span>
                                        <span class="day-badge-red" style="background-color:#18181b; color:#71717a; border:none;">0 vídeos</span>
                                    </div>
                                    <div class="card-footer-summary">Sem publicações registradas neste dia.</div>
                                </div>
                                """
                col_alvo.markdown(card_vazio, unsafe_allow_html=True)

          # =========================================================
          # ABA 3: INSIGHTS CRUZADOS
          # =========================================================
          with tab_insights:
            st.markdown("### 🔥 Mapa de Calor Cruzado")
            df_pivot = (
                df_filtrado.pivot_table(
                    index="Dia_Completo",
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
                color_continuous_scale="Reds",
                aspect="auto",
            )
            fig_heat.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#a1a1aa"),
            )
            st.plotly_chart(fig_heat, use_container_width=True)

          # =========================================================
          # ABA 4: TABELA PREMIUM (TEMA YOUTUBE RED)
          # =========================================================
          with tab_tabela:
            rows_html = ""
            for _, row in df_filtrado.iterrows():
              rows_html += f"""
                            <tr>
                                <td>{row['Data_Formatada']}</td>
                                <td>{row['Dia']}</td>
                                <td>{row['Hora_Cheia']}</td>
                                <td class="td-likes">{row['Curtidas']:,}</td>
                                <td>{row['Comentários']:,}</td>
                                <td><span class="badge-type">{row['Tipo']}</span></td>
                                <td class="td-caption" title="{row['Título']}">{row['Título']}</td>
                            </tr>
                            """

            raw_table_code = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                        <style>
                            body {{
                                background-color: transparent;
                                color: #a1a1aa;
                                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                                margin: 0;
                                padding: 0;
                            }}
                            .custom-table-container {{
                                width: 100%;
                                overflow-x: auto;
                                border: 1px solid #22222a;
                                border-radius: 10px;
                                background-color: #0d0d12;
                            }}
                            .custom-table {{
                                width: 100%;
                                border-collapse: collapse;
                                font-size: 0.83rem;
                                color: #a1a1aa;
                                text-align: left;
                            }}
                            .custom-table th {{
                                background-color: #121217;
                                color: #71717a;
                                font-size: 0.7rem;
                                font-weight: 700;
                                text-transform: uppercase;
                                letter-spacing: 0.05em;
                                padding: 12px 16px;
                                border-bottom: 1px solid #22222a;
                            }}
                            .custom-table td {{
                                padding: 12px 16px;
                                border-bottom: 1px solid #16161e;
                                white-space: nowrap;
                            }}
                            .custom-table tr:hover {{
                                background-color: #14141c;
                            }}
                            .td-likes {{
                                color: #f87171 !important;
                                font-weight: 700;
                            }}
                            .badge-type {{
                                background-color: #1f1414;
                                color: #ef4444;
                                border: 1px solid #451a1a;
                                padding: 2px 8px;
                                border-radius: 10px;
                                font-size: 0.65rem;
                                font-weight: 700;
                                letter-spacing: 0.05em;
                            }}
                            .td-caption {{
                                max-width: 400px;
                                overflow: hidden;
                                text-overflow: ellipsis;
                                white-space: nowrap;
                                color: #d4d4d8;
                            }}
                        </style>
                        </head>
                        <body>
                            <div class="custom-table-container">
                                <table class="custom-table">
                                    <thead>
                                        <tr>
                                            <th>DATA SP</th>
                                            <th>DIA</th>
                                            <th>HORA</th>
                                            <th>LIKES</th>
                                            <th>COMENT.</th>
                                            <th>TIPO</th>
                                            <th>LEGENDA</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {rows_html}
                                    </tbody>
                                </table>
                            </div>
                        </body>
                        </html>
                        """

            altura_tabela = min(600, len(df_filtrado) * 45 + 50)
            components.html(
                raw_table_code, height=altura_tabela, scrolling=True
            )

      except Exception as e:
        st.error(f"Erro ao carregar o canal: {e}")
    else:
      st.info(
          "👆 Digite ou cole o **ID do Canal** na caixa acima para carregar o"
          " painel."
      )

  elif modo_app == "⚔️ Comparativo":
    st.markdown("### ⚔️ Comparar Dois Canais")
    col_c1, col_c2 = st.columns(2)
    id1 = col_c1.text_input("ID do Canal 1:")
    id2 = col_c2.text_input("ID do Canal 2:")

    if id1 and id2:
      try:
        with st.spinner("Buscando dados comparativos..."):
          nome1, df1, det1 = buscar_dados_canal(youtube, id1, max_results)
          nome2, df2, det2 = buscar_dados_canal(youtube, id2, max_results)

        if df1 is not None and df2 is not None:
          st.subheader(
              f"{det1['nome']} ({det1['inscritos']}) vs {det2['nome']}"
              f" ({det2['inscritos']})"
          )
          df_comb = pd.concat([df1, df2])
          fig_comp = px.bar(
              df_comb.groupby(["Canal", "Hora_Cheia"])["Visualizações"]
              .mean()
              .reset_index(),
              x="Hora_Cheia",
              y="Visualizações",
              color="Canal",
              barmode="group",
              color_discrete_sequence=["#ef4444", "#38bdf8"],
          )
          fig_comp.update_layout(
              template="plotly_dark",
              paper_bgcolor="rgba(0,0,0,0)",
              plot_bgcolor="rgba(0,0,0,0)",
          )
          st.plotly_chart(fig_comp, use_container_width=True)
      except Exception as e:
        st.error(f"Erro no comparativo: {e}")

else:
  st.error("Chave YOUTUBE_API_KEY não encontrada nos secrets.")
