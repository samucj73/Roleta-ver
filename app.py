import streamlit as st
import random

st.set_page_config(page_title="Lotofácil - Geração Inteligente", layout="centered")

st.title("🎯 Lotofácil - Geração Inteligente de Jogos")

st.markdown("""
Insira os **15 números sorteados no último concurso da Lotofácil** e clique em **Gerar Jogos** para obter 5 sugestões baseadas em padrões estatísticos.
""")

def validar_concurso(concurso):
    if len(concurso) != 15:
        st.error("Você deve informar exatamente 15 dezenas.")
        return False
    if any(n < 1 or n > 25 for n in concurso):
        st.error("As dezenas devem estar entre 1 e 25.")
        return False
    if len(set(concurso)) != 15:
        st.error("As dezenas não podem se repetir.")
        return False
    return True

def aplicar_regras(concurso_anterior):
    todos_numeros = set(range(1, 26))
    jogos_gerados = []

    while len(jogos_gerados) < 5:
        jogo = set()

        qtd_reutilizadas = random.randint(8, 13)
        dezenas_reutilizadas = random.sample(concurso_anterior, qtd_reutilizadas)
        jogo.update(dezenas_reutilizadas)

        restantes = list(todos_numeros - jogo)
        jogo.update(random.sample(restantes, 15 - len(jogo)))

        # Regra: entre 6 e 9 pares
        pares = [n for n in jogo if n % 2 == 0]
        if 6 <= len(pares) <= 9:
            jogos_gerados.append(sorted(jogo))

    return jogos_gerados

numeros_input = st.text_input("Digite os 15 números sorteados separados por espaço (ex: 1 3 5 7 9 11 13 15 17 19 21 23 24 25 2):")

if st.button("🎰 Gerar Jogos"):
    try:
        dezenas = list(map(int, numeros_input.strip().split()))
        if validar_concurso(dezenas):
            jogos = aplicar_regras(dezenas)

            st.success("Jogos gerados com sucesso!")
            for i, jogo in enumerate(jogos, 1):
                st.write(f"Jogo {i}: {', '.join(f'{d:02d}' for d in jogo)}")

            # Exportar para TXT
            if st.button("⬇️ Baixar jogos em .TXT"):
                conteudo = "\n".join([f"Jogo {i+1}: {', '.join(f'{d:02d}' for d in j)}" for i, j in enumerate(jogos)])
                st.download_button("Clique para baixar", data=conteudo, file_name="jogos_lotofacil.txt")

    except ValueError:
        st.error("Entrada inválida. Verifique se digitou corretamente os números.")
        
# Rodapé personalizado
st.markdown("---")
st.markdown("🔢 Desenvolvido com inteligência matemática aplicada à Lotofácil - por SAM ROCK 💡")
