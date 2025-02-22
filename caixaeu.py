import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from matplotlib.ticker import FuncFormatter


# Função para formatação dos valores (R$)
def moeda(x, pos):
    return f"R${x:,.2f}"


# Função para calcular o total com base em um detalhamento (caso seja necessário futuramente)
def calc_total(breakdown):
    total = 0
    coin_values = {"R$0.05": 0.05, "R$0.10": 0.10, "R$0.25": 0.25, "R$0.50": 0.50, "R$1.00": 1.00}
    note_values = {"R$2": 2, "R$5": 5, "R$10": 10, "R$20": 20, "R$50": 50, "R$100": 100, "R$200": 200}
    for d, qty in breakdown["moedas"].items():
        total += coin_values[d] * qty
    for d, qty in breakdown["notas"].items():
        total += note_values[d] * qty
    return total


# Função para atualizar o container de saldo (exibe os saldos atuais dos caixas)
def update_balance_container():
    st.markdown("---")
    st.subheader("💡 Saldo Atual dos Caixas")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Caixa Principal:** R${st.session_state['saldo_principal']:,.2f}")
    with col2:
        st.write(f"**Caixa Secundário:** R${st.session_state['saldo_secundario']:,.2f}")


# Configurar a página
st.set_page_config(page_title="Caixa - IA Previsão", layout="wide")

# Inicializar dados na sessão, se ainda não existirem
if 'transactions' not in st.session_state:
    st.session_state['transactions'] = []
if 'saldo_principal' not in st.session_state:
    st.session_state['saldo_principal'] = 0.0
if 'saldo_secundario' not in st.session_state:
    st.session_state['saldo_secundario'] = 0.0
if 'detalhamento_principal' not in st.session_state:
    st.session_state['detalhamento_principal'] = {
        "moedas": {"R$0.05": 0, "R$0.10": 0, "R$0.25": 0, "R$0.50": 0, "R$1.00": 0},
        "notas": {"R$2": 0, "R$5": 0, "R$10": 0, "R$20": 0, "R$50": 0, "R$100": 0, "R$200": 0}
    }
if 'detalhamento_secundario' not in st.session_state:
    st.session_state['detalhamento_secundario'] = {
        "moedas": {"R$0.05": 0, "R$0.10": 0, "R$0.25": 0, "R$0.50": 0, "R$1.00": 0},
        "notas": {"R$2": 0, "R$5": 0, "R$10": 0, "R$20": 0, "R$50": 0, "R$100": 0, "R$200": 0}
    }

# Cabeçalho com imagem e título
header_col1, header_col2 = st.columns([1, 7])
with header_col1:
    st.image("rota66.png", width=150)
with header_col2:
    st.markdown(
        """
        <style>
        h1 { font-size: 50px !important; text-align: center; color: black; }
        </style>
        """, unsafe_allow_html=True)
    st.title("💰 Controle de Caixa - Rota 66 Conveniência")

st.markdown("---")

# Área de Inserção de Contagem (Contagem dos valores em cada caixa)
col1, col2 = st.columns(2)

# Caixa Principal (Contagem)
with col1:
    st.subheader("📌 Caixa Principal (Contagem)")
    mp1 = st.number_input("Moedas de R$0.05", min_value=0, step=1, key="mp1")
    mp2 = st.number_input("Moedas de R$0.10", min_value=0, step=1, key="mp2")
    mp3 = st.number_input("Moedas de R$0.25", min_value=0, step=1, key="mp3")
    mp4 = st.number_input("Moedas de R$0.50", min_value=0, step=1, key="mp4")
    mp5 = st.number_input("Moedas de R$1.00", min_value=0, step=1, key="mp5")
    moedas_principal = [mp1, mp2, mp3, mp4, mp5]
    np1 = st.number_input("Notas de R$2", min_value=0, step=1, key="np1")
    np2 = st.number_input("Notas de R$5", min_value=0, step=1, key="np2")
    np3 = st.number_input("Notas de R$10", min_value=0, step=1, key="np3")
    np4 = st.number_input("Notas de R$20", min_value=0, step=1, key="np4")
    np5 = st.number_input("Notas de R$50", min_value=0, step=1, key="np5")
    np6 = st.number_input("Notas de R$100", min_value=0, step=1, key="np6")
    np7 = st.number_input("Notas de R$200", min_value=0, step=1, key="np7")
    notas_principal = [np1, np2, np3, np4, np5, np6, np7]
    total_principal = (mp1 * 0.05 + mp2 * 0.10 + mp3 * 0.25 + mp4 * 0.50 + mp5 * 1.00) + (
            np1 * 2 + np2 * 5 + np3 * 10 + np4 * 20 + np5 * 50 + np6 * 100 + np7 * 200)
    st.markdown("**Detalhamento - Moedas**")
    st.table(pd.DataFrame({"Denominação": ["R$0.05", "R$0.10", "R$0.25", "R$0.50", "R$1.00"],
                           "Quantidade": moedas_principal}))
    st.markdown("**Detalhamento - Cédulas**")
    st.table(pd.DataFrame({"Denominação": ["R$2", "R$5", "R$10", "R$20", "R$50", "R$100", "R$200"],
                           "Quantidade": notas_principal}))
    st.write(f"💰 **Total Caixa Principal:** R${total_principal:,.2f}")

# Caixa Secundário (Contagem)
with col2:
    st.subheader("📌 Caixa Secundário (Contagem)")
    ms1 = st.number_input("Moedas de R$0.05", min_value=0, step=1, key="ms1")
    ms2 = st.number_input("Moedas de R$0.10", min_value=0, step=1, key="ms2")
    ms3 = st.number_input("Moedas de R$0.25", min_value=0, step=1, key="ms3")
    ms4 = st.number_input("Moedas de R$0.50", min_value=0, step=1, key="ms4")
    ms5 = st.number_input("Moedas de R$1.00", min_value=0, step=1, key="ms5")
    moedas_secundario = [ms1, ms2, ms3, ms4, ms5]
    ns1 = st.number_input("Notas de R$2", min_value=0, step=1, key="ns1")
    ns2 = st.number_input("Notas de R$5", min_value=0, step=1, key="ns2")
    ns3 = st.number_input("Notas de R$10", min_value=0, step=1, key="ns3")
    ns4 = st.number_input("Notas de R$20", min_value=0, step=1, key="ns4")
    ns5 = st.number_input("Notas de R$50", min_value=0, step=1, key="ns5")
    ns6 = st.number_input("Notas de R$100", min_value=0, step=1, key="ns6")
    ns7 = st.number_input("Notas de R$200", min_value=0, step=1, key="ns7")
    notas_secundario = [ns1, ns2, ns3, ns4, ns5, ns6, ns7]
    total_secundario = (ms1 * 0.05 + ms2 * 0.10 + ms3 * 0.25 + ms4 * 0.50 + ms5 * 1.00) + (
            ns1 * 2 + ns2 * 5 + ns3 * 10 + ns4 * 20 + ns5 * 50 + ns6 * 100 + ns7 * 200)
    st.markdown("**Detalhamento - Moedas**")
    st.table(pd.DataFrame({"Denominação": ["R$0.05", "R$0.10", "R$0.25", "R$0.50", "R$1.00"],
                           "Quantidade": moedas_secundario}))
    st.markdown("**Detalhamento - Cédulas**")
    st.table(pd.DataFrame({"Denominação": ["R$2", "R$5", "R$10", "R$20", "R$50", "R$100", "R$200"],
                           "Quantidade": notas_secundario}))
    st.write(f"💰 **Total Caixa Secundário:** R${total_secundario:,.2f}")

# Botão para salvar o registro de contagem e atualizar os saldos
if st.button("💾 Salvar Registro de Contagem"):
    st.session_state['detalhamento_principal'] = {
        "moedas": {"R$0.05": mp1, "R$0.10": mp2, "R$0.25": mp3, "R$0.50": mp4, "R$1.00": mp5},
        "notas": {"R$2": np1, "R$5": np2, "R$10": np3, "R$20": np4, "R$50": np5, "R$100": np6, "R$200": np7}
    }
    st.session_state['detalhamento_secundario'] = {
        "moedas": {"R$0.05": ms1, "R$0.10": ms2, "R$0.25": ms3, "R$0.50": ms4, "R$1.00": ms5},
        "notas": {"R$2": ns1, "R$5": ns2, "R$10": ns3, "R$20": ns4, "R$50": ns5, "R$100": ns6, "R$200": ns7}
    }
    st.session_state['saldo_principal'] = total_principal
    st.session_state['saldo_secundario'] = total_secundario

    # Adiciona um registro no histórico
    transacao = {
        'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'tipo': 'contagem',
        'total_principal': total_principal,
        'total_secundario': total_secundario,
        'total': total_principal + total_secundario,
        'observacao': 'Contagem realizada'
    }
    st.session_state['transactions'].append(transacao)

    st.success("✅ Registro de contagem salvo com sucesso!")
    update_balance_container()

st.markdown("---")

# Seção: Histórico Resumido e Gráfico (últimos 30 dias) com tendência de IA
if st.button("📊 Ver Histórico e IA"):
    st.subheader("📈 Histórico e Previsão do Caixa (últimos 30 dias)")

    if st.session_state['transactions']:
        df_hist = pd.DataFrame(st.session_state['transactions'])
        df_hist['data'] = pd.to_datetime(df_hist['data'])
        cutoff = datetime.now() - timedelta(days=30)
        df_hist = df_hist[df_hist['data'] >= cutoff].sort_values('data')
    else:
        df_hist = pd.DataFrame()

    if not df_hist.empty:
        st.subheader("📋 Histórico de Transações")
        # Formatação do total para exibição
        df_hist['total_formatado'] = df_hist.apply(
            lambda row: f"R${row['total']:,.2f}" if row['tipo'] == 'contagem' else f"R${row.get('valor', 0):,.2f}",
            axis=1)
        df_resumo = df_hist[['data', 'tipo', 'total_formatado', 'observacao']].copy()
        st.dataframe(df_resumo)

        # Geração do gráfico
        df_cont = df_hist[df_hist['tipo'] == 'contagem']
        fig, ax = plt.subplots(figsize=(10, 5))
        if not df_cont.empty:
            # Converter a coluna 'total' para float
            totals = df_cont['total'].astype(float)
            ax.scatter(df_cont['data'], totals, color='blue', label="Contagem Real")
            df_cont['dia'] = df_cont['data'].dt.dayofyear
            X = df_cont[['dia']]
            y = totals
            # Se houver dados suficientes, usa RandomForest; caso contrário, usa tendência linear
            if len(df_cont) >= 10:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X, y)
                label_forecast = "Previsão IA"
                dias_fut = [datetime.today() + timedelta(days=i) for i in range(1, 8)]
                dias_fut_num = np.array([d.timetuple().tm_yday for d in dias_fut]).reshape(-1, 1)
                forecast = model.predict(dias_fut_num)
            else:
                st.warning("📌 Poucos dados para previsão com IA. Usando tendência linear.")
                label_forecast = "Previsão IA (tendência linear)"
                coeffs = np.polyfit(df_cont['dia'], y, 1)
                dias_fut = [datetime.today() + timedelta(days=i) for i in range(1, 8)]
                dias_fut_num = np.array([d.timetuple().tm_yday for d in dias_fut])
                forecast = np.polyval(coeffs, dias_fut_num)
            ax.plot(dias_fut, forecast, marker='o', linestyle='dashed', color='red', label=label_forecast)
        else:
            st.info("Sem registros de contagem para o gráfico.")
            base_val = 1000
            dias_fut = [datetime.today() + timedelta(days=i) for i in range(1, 8)]
            forecast = [base_val * (1 + 0.01 * i) for i in range(1, 8)]
            ax.plot(dias_fut, forecast, marker='o', linestyle='dashed', color='red',
                    label="Previsão IA (valores corrigidos)")

        ax.set_title("📊 Histórico e Previsão do Caixa")
        ax.set_xlabel("Data")
        ax.set_ylabel("Saldo Estimado (R$)")
        ax.yaxis.set_major_formatter(FuncFormatter(moeda))
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("Sem dados históricos para exibição.")
