import streamlit as st
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

st.set_page_config(page_title="Captura Betfair", layout="centered")
st.title("🎰 Captura de Números da Roleta - Betfair")

# Sessão de estado
if "resultados" not in st.session_state:
    st.session_state.resultados = []

def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def coletar_resultados_roleta(url, seletor_css):
    driver = iniciar_driver()
    driver.get(url)
    time.sleep(10)
    resultados = []
    try:
        elementos = driver.find_elements(By.CSS_SELECTOR, seletor_css)
        for el in elementos:
            texto = el.text.strip()
            if texto.isdigit() and 0 <= int(texto) <= 36:
                resultados.append(texto)
    except Exception as e:
        st.error(f"Erro ao coletar: {e}")
    driver.quit()
    return resultados

# Entrada de dados
url = st.text_input("Cole a URL da roleta da Betfair:", value="https://play.betfair.bet.br/launch/mobile?returnURL=...")

seletor_css = st.text_input("Seletor CSS dos números:", value=".roulette-history .number")

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🎯 Capturar Números"):
        with st.spinner("Capturando números da roleta..."):
            resultados = coletar_resultados_roleta(url, seletor_css)
            if resultados:
                st.session_state.resultados.extend(resultados)
                st.success("Números capturados com sucesso!")
            else:
                st.warning("Nenhum número encontrado.")

with col2:
    if st.button("🔄 Resetar"):
        st.session_state.resultados = []
        st.info("Resultados resetados!")

# Exibir e salvar resultados
if st.session_state.resultados:
    st.subheader("Resultados Capturados:")
    st.write(", ".join(st.session_state.resultados))

    # Salvar em .txt
    with open("resultados_roleta.txt", "w") as f:
        f.write("\n".join(st.session_state.resultados))
    
    with open("resultados_roleta.txt", "rb") as f:
        st.download_button("📥 Baixar resultados (.txt)", f, file_name="resultados_roleta.txt")
