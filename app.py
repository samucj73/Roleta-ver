import streamlit as st
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

st.set_page_config(page_title="Captura Betfair", layout="wide")
st.title("Captura de Números da Roleta - Betfair")

# Lista de seletores sugeridos para testar automaticamente
SELETORES_SUGERIDOS = [
    ".roulette-history .number",         # comum em páginas da Betfair
    ".history-bar .number",              # comum em Sportingbet
    ".statistics .number",               # alternativa estatística
    ".number-history-item",              # comum em componentes JavaScript
    ".last-numbers span",                # possível estrutura dinâmica
    ".latest-results .number",           # outro comum
]

def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def tentar_seletores(url):
    driver = iniciar_driver()
    driver.get(url)
    time.sleep(10)
    resultados = []

    seletor_usado = None
    for seletor in SELETORES_SUGERIDOS:
        try:
            elementos = driver.find_elements(By.CSS_SELECTOR, seletor)
            temp_resultados = []
            for el in elementos:
                texto = el.text.strip()
                if texto.isdigit() and 0 <= int(texto) <= 36:
                    temp_resultados.append(texto)
            if temp_resultados:
                resultados = temp_resultados
                seletor_usado = seletor
                break
        except Exception:
            continue
    driver.quit()
    return resultados, seletor_usado

# UI
url = st.text_input("Cole a URL da roleta:", value="https://...")

col1, col2 = st.columns([1, 1])
with col1:
    capturar = st.button("Capturar Números")
with col2:
    resetar = st.button("Resetar Resultados")

if "resultados" not in st.session_state:
    st.session_state.resultados = []

# Captura automática testando seletores
if capturar:
    with st.spinner("Tentando capturar números com seletores sugeridos..."):
        resultados, seletor_utilizado = tentar_seletores(url)
        if resultados:
            st.session_state.resultados.extend(resultados)
            st.success(f"Números capturados com sucesso! Seletor usado: `{seletor_utilizado}`")
            st.write(resultados)
            with open("numeros_capturados.txt", "w") as f:
                f.write("\n".join(st.session_state.resultados))
        else:
            st.warning("Nenhum número foi capturado com os seletores disponíveis.")

if resetar:
    st.session_state.resultados = []
    st.success("Resultados resetados.")

# Exibição final
if st.session_state.resultados:
    st.subheader("Números Coletados:")
    st.write(st.session_state.resultados)
    st.download_button("Baixar como .txt", "\n".join(st.session_state.resultados), file_name="numeros_capturados.txt")
