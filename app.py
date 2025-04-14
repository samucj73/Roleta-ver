import streamlit as st
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

st.set_page_config(page_title="Captura Betfair", layout="wide")
st.title("Captura de Números da Roleta - Betfair")

def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def coletar_resultados_roleta(url):
    driver = iniciar_driver()
    driver.get(url)
    time.sleep(10)
    resultados = []
    try:
        elementos = driver.find_elements(By.XPATH, "//*[contains(text(), '')]")
        for el in elementos:
            texto = el.text.strip()
            if texto.isdigit() and 0 <= int(texto) <= 36:
                resultados.append(texto)
    except Exception as e:
        st.error(f"Erro ao coletar: {e}")
    driver.quit()
    return resultados

# URL padrão
url = st.text_input("Cole a URL da roleta da Betfair:", value="https://play.betfair.bet.br/launch/mobile?returnURL=...")
if st.button("Capturar Números"):
    with st.spinner("Capturando números da roleta..."):
        resultados = coletar_resultados_roleta(url)
        if resultados:
            st.success("Números capturados com sucesso!")
            st.write(resultados)
        else:
            st.warning("Nenhum número encontrado.")
