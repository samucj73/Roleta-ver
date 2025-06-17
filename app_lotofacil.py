import streamlit as st
import random
import requests
from datetime import datetime

# === Funções ===

def capturar_ultimos_resultados(qtd=10):
    url_base = "https://loteriascaixa-api.herokuapp.com/api/lotofacil/"
    concursos = []
    try:
        resp = requests.get(url_base)
        if resp.status_code != 200:
            return []
        dados = resp.json()
        if isinstance(dados, list):
            ultimo = dados[0]
        else:
            ultimo = dados
        numero_atual = int(ultimo.get("concurso"))
        dezenas = sorted([int(d) for d in ultimo.get("dezenas")])
        data_concurso = ultimo.get("data")
        concursos.append((numero_atual, data_concurso, dezenas))
        for i in range(1, qtd):
            concurso_numero = numero_atual - i
            resp = requests.get(f"{url_base}{concurso_numero}")
            if resp.status_code == 200:
                dados = resp.json()
                if isinstance(dados, list):
                    data = dados[0]
                else:
                    data = dados
                numero = int(data.get("concurso"))
                dezenas = sorted([int(d) for d in data.get("dezenas")])
                data_concurso = data.get("data")
                concursos.append((numero, data_concurso, dezenas))
            else:
                break
    except Exception:
        return []
    return concursos[::-1]

def formatar_data(data_str):
    formatos = [
        "%Y-%m-%dT%H:%M:%S.000Z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d"
    ]
    for fmt in formatos:
        try:
            return datetime.strptime(data_str, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return data_str

def gerar_cartao_possivel(padrao):
    tentativas = 0
    while tentativas < 500:
        jogo = sorted(random.sample(range(1, 26), 15))
        if verificar_padroes(jogo, padrao):
            return jogo
        tentativas += 1
    return []

def verificar_padroes(jogo, padrao):
    pares = sum(1 for d in jogo if d % 2 == 0)
    primos = sum(1 for d in jogo if d in [2, 3, 5, 7, 11, 13, 17, 19, 23])
    moldura = sum(1 for d in jogo if d in [1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25])
    sequencias = sum(1 for i in range(len(jogo)-1) if jogo[i]+1 == jogo[i+1])
    repetidos = sum(1 for d in jogo if d in padrao)
    return (
        5 <= pares <= 10 and
        5 <= primos <= 9 and
        8 <= moldura <= 13 and
        1 <= sequencias <= 4 and
        9 <= repetidos <= 13
    )

# === Interface com abas ===

st.set_page_config(page_title="Lotofácil Avançado", layout="centered")
st.title("🎯 Ferramenta Inteligente - Lotofácil")
aba1, aba2 = st.tabs(["📋 Gerar Jogos", "✅ Conferir Jogos"])

# === Aba 1: Gerar Jogos ===

with aba1:
    st.subheader("📋 Gerador de Jogos com base em padrões matemáticos")
    qtd_cartoes = st.slider("Quantos cartões deseja gerar?", 3, 30, 5)
    
    concursos = capturar_ultimos_resultados(4)
    if not concursos:
        st.error("Erro ao buscar concursos. Verifique sua conexão.")
    else:
        ultimos = [d for (_, _, d) in concursos]
        numeros_frequentes = {}
        for jogo in ultimos:
            for dezena in jogo:
                numeros_frequentes[dezena] = numeros_frequentes.get(dezena, 0) + 1
        base_padroes = sorted(numeros_frequentes, key=numeros_frequentes.get, reverse=True)[:18]

        if st.button("🔍 Gerar Jogos"):
            jogos = []
            for _ in range(qtd_cartoes):
                jogo = gerar_cartao_possivel(base_padroes)
                if jogo:
                    jogos.append(jogo)

            if jogos:
                st.success(f"{len(jogos)} jogos gerados com sucesso!")
                for i, jogo in enumerate(jogos, 1):
                    st.write(f"Cartão {i}: {', '.join(f'{n:02d}' for n in jogo)}")

                texto = "\n".join(",".join(f"{n:02d}" for n in jogo) for jogo in jogos)
                st.download_button("📥 Baixar jogos em .TXT", texto, file_name="jogos_lotofacil.txt")

# === Aba 2: Conferência ===

with aba2:
    st.subheader("✅ Conferência de Jogos com Último Sorteio")
    jogos_txt = st.text_area("Cole aqui os seus jogos (ex: 01, 02, 03...)", height=200)
    if st.button("🔎 Conferir"):
        concursos = capturar_ultimos_resultados(1)
        if concursos:
            _, _, dezenas_oficiais = concursos[-1]
            st.markdown(f"**Último sorteio:** {', '.join(f'{d:02d}' for d in dezenas_oficiais)}")

            linhas = jogos_txt.strip().split("\n")
            for i, linha in enumerate(linhas, 1):
                dezenas = [int(d.strip()) for d in linha.split(",") if d.strip().isdigit()]
                acertos = sorted(set(dezenas) & set(dezenas_oficiais))
                st.write(f"Jogo {i} - {len(acertos)} acertos: {', '.join(f'{d:02d}' for d in acertos)}")

# === Rodapé ===
st.markdown("---")
st.markdown("Desenvolvido por Tio Rock 🔍")
