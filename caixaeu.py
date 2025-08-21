import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from matplotlib.ticker import FuncFormatter

# ---------------- Funções ----------------
def moeda(x, pos):
    return f"R${x:,.2f}"

# Função para atualizar o saldo
def update_balance_container():
    st.markdown("---")
    st.subheader("💡 Saldo Atual")
    st.write(f"**Caixa Secundário:** R${st.session_state['saldo_secundario']:,.2f}")

# ---------------- Configuração ----------------
st.set_page_config(page_title="Caixa - IA Previsão", layout="wide")

# Cabeçalho com imagem e título
header_col1, header_col2 = st.columns([1, 7])
with header_col1:
    st.image("rota66.png", width=150)  # ajuste o caminho se necessário
with header_col2:
    st.markdown(
        """
        <style>
        h1 { font-size: 45px !important; text-align: left; color: white; }
        </style>
        """, unsafe_allow_html=True)
    st.markdown(
        "<h1 style='text-align: center;'>💰 Controle de Caixa - Rota 66 Conveniência</h1>",
        unsafe_allow_html=True
    )

if 'transactions' not in st.session_state:
    st.session_state['transactions'] = []
if 'saldo_secundario' not in st.session_state:
    st.session_state['saldo_secundario'] = 0.0
if 'detalhamento_secundario' not in st.session_state:
    st.session_state['detalhamento_secundario'] = {
        "moedas": {"R$0.05": 0, "R$0.10": 0, "R$0.25": 0, "R$0.50": 0, "R$1.00": 0},
        "notas": {"R$2": 0, "R$5": 0, "R$10": 0, "R$20": 0, "R$50": 0, "R$100": 0, "R$200": 0}
    }


# ---------------- Inputs Caixa Secundário ----------------
st.markdown(
    "<h3 style='text-align: center;'>📌 Caixa Secundário (Contagem)</h3>",
    unsafe_allow_html=True)

# Inputs moedas
ms1 = st.number_input("Moedas de R$0.05", min_value=0, step=1, key="ms1")
ms2 = st.number_input("Moedas de R$0.10", min_value=0, step=1, key="ms2")
ms3 = st.number_input("Moedas de R$0.25", min_value=0, step=1, key="ms3")
ms4 = st.number_input("Moedas de R$0.50", min_value=0, step=1, key="ms4")
ms5 = st.number_input("Moedas de R$1.00", min_value=0, step=1, key="ms5")
moedas_secundario = [ms1, ms2, ms3, ms4, ms5]

# Inputs cédulas
ns1 = st.number_input("Notas de R$2", min_value=0, step=1, key="ns1")
ns2 = st.number_input("Notas de R$5", min_value=0, step=1, key="ns2")
ns3 = st.number_input("Notas de R$10", min_value=0, step=1, key="ns3")
ns4 = st.number_input("Notas de R$20", min_value=0, step=1, key="ns4")
ns5 = st.number_input("Notas de R$50", min_value=0, step=1, key="ns5")
ns6 = st.number_input("Notas de R$100", min_value=0, step=1, key="ns6")
ns7 = st.number_input("Notas de R$200", min_value=0, step=1, key="ns7")
notas_secundario = [ns1, ns2, ns3, ns4, ns5, ns6, ns7]

# Cálculo total
total_secundario = (ms1 * 0.05 + ms2 * 0.10 + ms3 * 0.25 + ms4 * 0.50 + ms5 * 1.00) + (
    ns1 * 2 + ns2 * 5 + ns3 * 10 + ns4 * 20 + ns5 * 50 + ns6 * 100 + ns7 * 200
)

# ---------------- Exibir tabelas ----------------
df_moedas = pd.DataFrame({
    "Denominação": ["R$0.05", "R$0.10", "R$0.25", "R$0.50", "R$1.00"],
    "Quantidade": moedas_secundario
})
df_moedas["Valor Total"] = [0.05, 0.10, 0.25, 0.50, 1.00] * df_moedas["Quantidade"]

df_notas = pd.DataFrame({
    "Denominação": ["R$2", "R$5", "R$10", "R$20", "R$50", "R$100", "R$200"],
    "Quantidade": notas_secundario
})
valores_notas = [2, 5, 10, 20, 50, 100, 200]
df_notas["Valor Total"] = df_notas["Quantidade"] * valores_notas
df_notas["Valor Total"] = df_notas["Valor Total"].apply(lambda x: f"R${x:,.2f}")

st.markdown("**Detalhamento - Moedas**")
st.dataframe(df_moedas, use_container_width=True)

st.markdown("**Detalhamento - Cédulas**")
st.dataframe(df_notas, use_container_width=True)

st.write(f"🪙 **Total Caixa Secundário:** R${total_secundario:,.2f}")

# ---------------- Registro de movimentação ----------------
st.markdown("---")
st.subheader("✍ Registro de Movimentação")

nome = st.text_input("Digite o nome do responsável:")
acao = st.selectbox("Selecione a ação:", ["Inserção", "Retirada"])

if st.button("💾 Salvar Registro"):
    if nome.strip():
        st.session_state['detalhamento_secundario'] = {
            "moedas": {"R$0.05": ms1, "R$0.10": ms2, "R$0.25": ms3, "R$0.50": ms4, "R$1.00": ms5},
            "notas": {"R$2": ns1, "R$5": ns2, "R$10": ns3, "R$20": ns4, "R$50": ns5, "R$100": ns6, "R$200": ns7}
        }
        st.session_state['saldo_secundario'] = total_secundario

        transacao = {
            'Data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Responsável': nome,
            'Tipo': acao,
            'Total': total_secundario,
            'Observação': 'Contagem realizada'
        }
        st.session_state['transactions'].append(transacao)

        st.success(f"✅ {acao} registrada por **{nome}** com sucesso!")
        update_balance_container()
    else:
        st.warning("Por favor, insira o nome antes de registrar.")

# ---------------- Histórico ----------------
st.markdown("---")
st.subheader("📜 Histórico de Movimentações")

if st.session_state['transactions']:
    df_hist = pd.DataFrame(st.session_state['transactions'])
    st.dataframe(df_hist, use_container_width=True)
else:
    st.info("Nenhum registro encontrado.")

