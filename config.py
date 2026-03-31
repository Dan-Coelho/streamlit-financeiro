import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", initial_sidebar_state="auto")
with st.container(horizontal_alignment="center", vertical_alignment="center"):
    st.title("IPNJ-EUSÉBIO", text_alignment="center")
    st.image("static/logoescurosemfundo.png", width=50)
    st.html("""
      <p>A Igreja Presbiteriana Nova Jerusalém Eusébio é congregação que nasceu do trabalho missionário da IPNJ Fortaleza - filiada à Igreja Presbiteriana do Brasil (IPB). Fundada em 08 de janeiro de 2023, a IPNOVA-EUSÉBIO é uma comunidade centrada na Palavra de Deus, que prioriza relacionamentos em Pequenos Grupos como exercício pleno de sua missão.<br> Nos reunimos para celebrações públicas no município do Eusébio sendo um culto de Adoração aos <span style="color: #C7DE52; font-weight: bold, font-size: 1.5rem;">Domingos - 10:30</span> e um culto de Oração às <span style="color: #C7DE52; font-weight: bold, font-size: 1.5rem;">Quartas-feiras - 19:30</span>. O que expressa bem a imagem de quem queremos ser é a nossa declaração de visão:
    “Uma comunidade contemporânea, comprometida com o evangelho de Jesus Cristo, que encoraja e capacita seus membros a viverem de forma integral os valores do Reino de Deus“.</p><br><br>
      <h4>PASTOR: Gabriel Brasil</h4>
    """)

with st.container(border=True, horizontal_alignment="center"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image(
            "static/cultoOracao.jpg",
            width=250,
        )
    with col2:
        st.image(
            "static/agenda.jpg",
            width=250,
        )
    with col3:
        st.image(
            "static/fraseipnj.jpg",
            width=250,
        )

    with st.expander("Venha nos visitar"):
        with st.container(border=True, horizontal_alignment="center"):
            st.html("""
                <h2 style='text-align: center; color: #080E08; background-color: #C7DE52; padding: 1rem; border-radius: 0.5rem;'>
                    IPNOVA - EUSÉBIO
                </h2>
                <p style='text-align:center; font-weight: 100; font-style: italic;'>Venha nos visitar em: Rua Sebastião Queiroz, 111. Centro - Eusébio.</p>
            """)
        with st.container(border=True, horizontal_alignment="center"):
            df = pd.DataFrame(
                {
                    "lat": [-3.887724],
                    "lon": [-38.444828],
                }
            )
            st.map(df, size=30, zoom=15, color="#0044ff")
