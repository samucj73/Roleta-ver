import streamlit as st
import random
from collections import Counter
from datetime import datetime
import requests

# === Dezenas da moldura e dezenas primas ===
MOLDURA = {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25}
PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}

# === Captura dos concursos ===
def capturar_ultimos_resultados(qtd=4):
    url_base = "https://loteriascaixa-api.herokuapp.com/api/lotofacil/"
    concursos = []
    try:
        resp = requests.get(url_base)
        if resp.status_code != 200:
            st.error("Erro ao buscar o último concurso.")
            return []
        dados = resp.json()
        ultimo = dados[0] if isinstance(dados, list) else dados
        numero_atual = int(ultimo.get("concurso"))
        for i in range(qtd):
            concurso_numero = numero_atual - i
            resp = requests.get(f"{url_base}{concurso_numero}")
            if resp.status_code == 200:
                dados = resp.json()
                data = dados[0] if isinstance(dados, list) else dados
                numero = int(data.get("concurso"))
                dezenas = sorted([int(d) for d in data.get("dezenas")])
                data_concurso = data.get("data")
                concursos.append((numero, data_concurso, dezenas))
    except Exception as e:
        st.error(f"Erro ao acessar API: {e}")
    return concursos[::-1]

# === Estatísticas dos concursos ===
def extrair_padroes(concursos):
    ultimos = concursos[-1][2]
    todas = [d for _, _, dezenas in concursos for d in dezenas]
    freq = Counter(todas)
    mais_frequentes = [item[0] for item in freq.most_common()]
    return {
        'freq': freq,
        'mais_frequentes': mais_frequentes,
        'ultimo_jogo': ultimos
    }

def contar_padroes(jogo):
    pares = sum(1 for d in jogo if d % 2 == 0)
    impares = 15 - pares
    linhas = [0]*5
    colunas = [0]*5
    moldura = sum(1 for d in jogo if d in MOLDURA)
    primos = sum(1 for d in jogo if d in PRIMOS)
    seq = 0
    max_seq = 0

    for d in jogo:
        l = (d - 1) // 5
        c = (d - 1) % 5
        linhas[l] += 1
        colunas[c] += 1

    jogo.sort()
    for i in range(1, len(jogo)):
        if jogo[i] == jogo[i - 1] + 1:
            seq += 1
            max_seq = max(max_seq, seq)
        else:
            seq = 0

    return {
        'pares': pares,
        'impares': impares,
        'linhas': linhas,
        'colunas': colunas,
        'moldura': moldura,
        'primos': primos,
        'sequencia': max_seq + 1 if max_seq else 0,
    }

# === Geração inteligente de jogos ===
def gerar_jogos_com_padroes(padroes, qtd_jogos=5):
    jogos = []
    numeros_possiveis = list(range(1, 26))
    ultimo_jogo = set(padroes['ultimo_jogo'])

    while len(jogos) < qtd_jogos:
        jogo = set()
        jogo.update(random.sample(padroes['mais_frequentes'][:20], 10))
        restantes = list(set(numeros_possiveis) - jogo)
        jogo.update(random.sample(restantes, 15 - len(jogo)))
        jogo = sorted(jogo)

        p = contar_padroes(jogo)

        if (
            6 <= p['pares'] <= 9 and
            8 <= p['moldura'] <= 12 and
            3 <= p['primos'] <= 7 and
            2 <= p['sequencia'] <= 5 and
            len(set(jogo) & ultimo_jogo) >= 5
        ):
            jogos.append(jogo)

    return jogos

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

# === Interface ===
st.set_page_config(page_title="Lotofácil Avançado", layout="centered")
st.title("🎯 Gerador Inteligente de Jogos - Lotofácil")

st.markdown("Este gerador usa **análise matemática completa** dos últimos 4 concursos da Lotofácil.")

qtd_cartoes = st.slider("Quantos cartões deseja gerar?", min_value=3, max_value=30, value=5)

if st.button("🔍 Gerar Jogos"):
    concursos = capturar_ultimos_resultados(4)
    if concursos:
        st.subheader("📅 Concursos utilizados:")
        for numero, data, dezenas in concursos:
            data_formatada = formatar_data(data)
            st.write(f"Concurso {numero} - {data_formatada}: {', '.join(f'{d:02d}' for d in dezenas)}")

        padroes = extrair_padroes(concursos)
        jogos = gerar_jogos_com_padroes(padroes, qtd_cartoes)

        st.subheader("🧠 Jogos gerados:")
        for i, jogo in enumerate(jogos, 1):
            st.write(f"Jogo {i}: {', '.join(f'{d:02d}' for d in jogo)}")

        txt = "\n".join([f"Jogo {i+1}: {', '.join(f'{d:02d}' for d in jogo)}" for i, jogo in enumerate(jogos)])
        st.download_button("📄 Baixar jogos em TXT", txt, file_name="jogos_lotofacil_avancado.txt")

st.markdown("---")
st.markdown("📊 Estatísticas reais aplicadas automaticamente - por **SAM ROCK** 🚀")
