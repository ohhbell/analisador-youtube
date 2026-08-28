import pandas as pd
import plotly.express as px
import streamlit as st
from googleapiclient.discovery import build

st.set_page_config(page_title="Analisador de Shorts", layout="wide")
st.title("📊 Analisador de Horários do YouTube Shorts")

# Puxa a chave das variáveis seguras
api_key = st.secrets.get("YOUTUBE_API_KEY")

channel_id = st.text_input("Digite o ID do Canal (ex: UCxxxx...):")

if channel_id and api_key:
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)

        with st.spinner('Coletando dados do canal...'):
            res = youtube.channels().list(id=channel_id, part='contentDetails').execute()
            playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            playlist_res = youtube.playlistItems().list(
                playlistId=playlist_id,
                part='snippet',
                maxResults=50
            ).execute()

            video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_res['items']]

            stats_res = youtube.videos().list(
                id=','.join(video_ids),
                part='snippet,statistics'
            ).execute()

            dados = []
            for item in stats_res['items']:
                data_utc = pd.to_datetime(item['snippet']['publishedAt'])
                data_br = data_utc.tz_convert('America/Sao_Paulo')
                
                dados.append({
                    'Título': item['snippet']['title'],
                    'Hora_Cheia': f"{data_br.hour:02d}:00",
                    'Visualizações': int(item['statistics'].get('viewCount', 0))
                })

            df = pd.DataFrame(dados)
            media_por_hora = df.groupby('Hora_Cheia')['Visualizações'].mean().reset_index()
            media_por_hora = media_por_hora.sort_values(by='Hora_Cheia')

            # Gráfico Interativo com Plotly
            fig = px.bar(
                media_por_hora, 
                x='Hora_Cheia', 
                y='Visualizações',
                title="Média de Visualizações por Horário de Publicação (Horário de Brasília)",
                labels={'Hora_Cheia': 'Horário do Upload', 'Visualizações': 'Média de Views'},
                color_discrete_sequence=['#FF0000']
            )
            fig.update_layout(template="plotly_white")
            
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao buscar dados. Verifique o ID do canal. Detalhes: {e}")