import streamlit as st
import pandas as pd
st.set_page_config(layout="wide", initial_sidebar_state="auto")
with st.container(horizontal_alignment='center', vertical_alignment='center'):
    st.title("IPNJ-EUSÉBIO", text_alignment='center')
    st.image('static/logoescurosemfundo.png', width=50)
    st.html('''
      <p>A Igreja Presbiteriana Nova Jerusalém Eusébio é congregação que nasceu do trabalho missionário da IPNJ Fortaleza - filiada à Igreja Presbiteriana do Brasil (IPB). Fundada em 08 de janeiro de 2023, a IPNOVA-EUSÉBIO é uma comunidade centrada na Palavra de Deus, que prioriza relacionamentos em Pequenos Grupos como exercício pleno de sua missão.<br> Nos reunimos para celebrações públicas no município do Eusébio sendo um culto de Adoração aos <span style="color: #C7DE52; font-weight: bold, font-size: 1.5rem;">Domingos - 10:30</span> e um culto de Oração às <span style="color: #C7DE52; font-weight: bold, font-size: 1.5rem;">Quartas-feiras - 19:30</span>. O que expressa bem a imagem de quem queremos ser é a nossa declaração de visão:
    “Uma comunidade contemporânea, comprometida com o evangelho de Jesus Cristo, que encoraja e capacita seus membros a viverem de forma integral os valores do Reino de Deus“.</p><br><br>
      <h4>PASTOR: Gabriel Brasil</h4>
    ''')

with st.container(border=True, horizontal_alignment='center'):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image('https://instagram.ffor50-1.fna.fbcdn.net/v/t51.82787-15/620834427_17982744911954937_5044246248611264876_n.webp?_nc_cat=104&ig_cache_key=MzgxNzkzMzA0NjIzNTEwNjY0Mw%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjEwODB4MTA4MC5zZHIuQzMifQ%3D%3D&_nc_ohc=Z6HH0w3iqBQQ7kNvwEinuKq&_nc_oc=Adm5RQWcrFSLVX64qpqV7iziBj8SrgZju5DTQvtlvT4OCIzzszAUhK9Ctva4xJtZOKw&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=instagram.ffor50-1.fna&_nc_gid=Cdqh6Qh-sxd9Thgi5FD8SQ&_nc_ss=8&oh=00_AfwlIeufYVLCxyDoVHaGPYTpC0ntjgIsLCwLYCqoph35sg&oe=69BA7B52', width=250)
    with col2:
        st.image('https://instagram.ffor50-1.fna.fbcdn.net/v/t51.82787-15/634419847_17984611244954937_2728811754737899674_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=110&ig_cache_key=MzgzMTAwNDg1ODc0MTI1Nzk1Ng%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjEwODB4MTM1MC5zZHIuQzMifQ%3D%3D&_nc_ohc=_RjGfR-jSeAQ7kNvwGQYYGB&_nc_oc=AdkMBoYiv_VSgGaSskhcgBPmHjBwUtgAgQAaIJTwZafiZVRNEkc1NtrAFp2EhjIqOWk&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=instagram.ffor50-1.fna&_nc_gid=Cdqh6Qh-sxd9Thgi5FD8SQ&_nc_ss=8&oh=00_Afy9E-ArVFJb1uF_ZA1V_cUMYJa_7gf2xNT8SilyQHB4pg&oe=69BA92B1', width=250)
    with col3:
        st.image('https://instagram.ffor50-1.fna.fbcdn.net/v/t51.82787-15/649116391_17987498429954937_2571352060521956640_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=100&ig_cache_key=Mzg0OTExNDgwMjgyNDc4NjM2OQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjEzNTB4MTY4OC5zZHIuQzMifQ%3D%3D&_nc_ohc=XolifqnqD7sQ7kNvwF7okG-&_nc_oc=AdnqiMG7oWMS57U3NOrbI6EWjVlCHt5IXWB76itO2pZ15ksm1pWR27-o-d2XE-RmEmc&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=instagram.ffor50-1.fna&_nc_gid=oEZ7X-mDow_4wu-bmQ0E0g&_nc_ss=8&oh=00_AfwV_jAAQNQqdtQCTm3djmE4-0_RrWwakplr-UwneyqbrA&oe=69BA6E06', width=250)
    
    with st.expander("Venha nos visitar"):
        with st.container(border=True, horizontal_alignment='center'):
            st.html('''
                <h2 style='text-align: center; color: #080E08; background-color: #C7DE52; padding: 1rem; border-radius: 0.5rem;'>
                    IPNOVA - EUSÉBIO
                </h2>
                <p style='text-align:center; font-weight: 100; font-style: italic;'>Venha nos visitar em: Rua Sebastião Queiroz, 111. Centro - Eusébio.</p>
            ''')
        with st.container(border=True, horizontal_alignment='center'):
            df = pd.DataFrame({
                'lat': [-3.887724],
                'lon': [-38.444828],
            })
            st.map(df, size=30, zoom=15, color="#0044ff")