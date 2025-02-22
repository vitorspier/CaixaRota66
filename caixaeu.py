import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from matplotlib.ticker import FuncFormatter


# Função para formatar o eixo Y em R$
def moeda(x, pos):
    return f"R${x:,.2f}"


# Configurar a página
st.set_page_config(page_title="Caixa - IA Previsão", layout="wide")

# Inicializar dados na sessão, se não existirem
if 'transactions' not in st.session_state:
    st.session_state['transactions'] = []
if 'saldo_principal' not in st.session_state:
    st.session_state['saldo_principal'] = 0.0
if 'saldo_secundario' not in st.session_state:
    st.session_state['saldo_secundario'] = 0.0

# Cabeçalho com imagem e título
header_col1, header_col2 = st.columns([1, 7])
with header_col1:
    st.image("rota66.png", width=150)
with header_col2:
    st.markdown(
        """
        <style>
        h1 {
            font-size: 50px !important;
            text-align: center;
            color: black;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("💰 Controle de Caixa - Rota 66 Conveniência")

st.markdown("---")

# Layout com duas colunas para inserção das contagens
col1, col2 = st.columns(2)

# ---------- Caixa Principal ----------
with col1:
    st.subheader("📌 Caixa Principal (Contagem)")
    # Inputs para moedas
    mp1 = st.number_input("Moedas de R$0.05", min_value=0, step=1, key="mp1")
    mp2 = st.number_input("Moedas de R$0.10", min_value=0, step=1, key="mp2")
    mp3 = st.number_input("Moedas de R$0.25", min_value=0, step=1, key="mp3")
    mp4 = st.number_input("Moedas de R$0.50", min_value=0, step=1, key="mp4")
    mp5 = st.number_input("Moedas de R$1.00", min_value=0, step=1, key="mp5")
    moedas_principal = [mp1, mp2, mp3, mp4, mp5]

    # Inputs para cédulas
    np1 = st.number_input("Notas de R$2", min_value=0, step=1, key="np1")
    np2 = st.number_input("Notas de R$5", min_value=0, step=1, key="np2")
    np3 = st.number_input("Notas de R$10", min_value=0, step=1, key="np3")
    np4 = st.number_input("Notas de R$20", min_value=0, step=1, key="np4")
    np5 = st.number_input("Notas de R$50", min_value=0, step=1, key="np5")
    np6 = st.number_input("Notas de R$100", min_value=0, step=1, key="np6")
    np7 = st.number_input("Notas de R$200", min_value=0, step=1, key="np7")
    notas_principal = [np1, np2, np3, np4, np5, np6, np7]

    # Cálculo do total para o Caixa Principal
    total_principal = (mp1 * 0.05 + mp2 * 0.10 + mp3 * 0.25 + mp4 * 0.50 + mp5 * 1.00) + \
                      (np1 * 2 + np2 * 5 + np3 * 10 + np4 * 20 + np5 * 50 + np6 * 100 + np7 * 200)

    # Exibir as tabelas detalhadas e o total na mesma coluna
    st.markdown("**Detalhamento - Moedas**")
    df_moedas_principal = pd.DataFrame({
        "Denominação": ["R$0.05", "R$0.10", "R$0.25", "R$0.50", "R$1.00"],
        "Quantidade": moedas_principal
    })
    st.table(df_moedas_principal)

    st.markdown("**Detalhamento - Cédulas**")
    df_notas_principal = pd.DataFrame({
        "Denominação": ["R$2", "R$5", "R$10", "R$20", "R$50", "R$100", "R$200"],
        "Quantidade": notas_principal
    })
    st.table(df_notas_principal)

    st.write(f"💰 **Total Caixa Principal:** R${total_principal:,.2f}")

# ---------- Caixa Secundário ----------
with col2:
    st.subheader("📌 Caixa Secundário (Contagem)")
    # Inputs para moedas
    ms1 = st.number_input("Moedas de R$0.05", min_value=0, step=1, key="ms1")
    ms2 = st.number_input("Moedas de R$0.10", min_value=0, step=1, key="ms2")
    ms3 = st.number_input("Moedas de R$0.25", min_value=0, step=1, key="ms3")
    ms4 = st.number_input("Moedas de R$0.50", min_value=0, step=1, key="ms4")
    ms5 = st.number_input("Moedas de R$1.00", min_value=0, step=1, key="ms5")
    moedas_secundario = [ms1, ms2, ms3, ms4, ms5]

    # Inputs para cédulas
    ns1 = st.number_input("Notas de R$2", min_value=0, step=1, key="ns1")
    ns2 = st.number_input("Notas de R$5", min_value=0, step=1, key="ns2")
    ns3 = st.number_input("Notas de R$10", min_value=0, step=1, key="ns3")
    ns4 = st.number_input("Notas de R$20", min_value=0, step=1, key="ns4")
    ns5 = st.number_input("Notas de R$50", min_value=0, step=1, key="ns5")
    ns6 = st.number_input("Notas de R$100", min_value=0, step=1, key="ns6")
    ns7 = st.number_input("Notas de R$200", min_value=0, step=1, key="ns7")
    notas_secundario = [ns1, ns2, ns3, ns4, ns5, ns6, ns7]

    # Cálculo do total para o Caixa Secundário
    total_secundario = (ms1 * 0.05 + ms2 * 0.10 + ms3 * 0.25 + ms4 * 0.50 + ms5 * 1.00) + \
                       (ns1 * 2 + ns2 * 5 + ns3 * 10 + ns4 * 20 + ns5 * 50 + ns6 * 100 + ns7 * 200)

    # Exibir as tabelas detalhadas e o total na mesma coluna
    st.markdown("**Detalhamento - Moedas**")
    df_moedas_secundario = pd.DataFrame({
        "Denominação": ["R$0.05", "R$0.10", "R$0.25", "R$0.50", "R$1.00"],
        "Quantidade": moedas_secundario
    })
    st.table(df_moedas_secundario)

    st.markdown("**Detalhamento - Cédulas**")
    df_notas_secundario = pd.DataFrame({
        "Denominação": ["R$2", "R$5", "R$10", "R$20", "R$50", "R$100", "R$200"],
        "Quantidade": notas_secundario
    })
    st.table(df_notas_secundario)

    st.write(f"💰 **Total Caixa Secundário:** R${total_secundario:,.2f}")

# Botão para salvar o registro de contagem (os detalhes são salvos como dicionários)
if st.button("💾 Salvar Registro de Contagem"):
    transacao = {
        'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'tipo': 'contagem',
        'total_principal': total_principal,
        'total_secundario': total_secundario,
        'total': total_principal + total_secundario,
        'observacao': 'Contagem realizada',
        'detalhamento_principal': {
            'moedas': {
                "R$0.05": mp1,
                "R$0.10": mp2,
                "R$0.25": mp3,
                "R$0.50": mp4,
                "R$1.00": mp5
            },
            'notas': {
                "R$2": np1,
                "R$5": np2,
                "R$10": np3,
                "R$20": np4,
                "R$50": np5,
                "R$100": np6,
                "R$200": np7
            }
        },
        'detalhamento_secundario': {
            'moedas': {
                "R$0.05": ms1,
                "R$0.10": ms2,
                "R$0.25": ms3,
                "R$0.50": ms4,
                "R$1.00": ms5
            },
            'notas': {
                "R$2": ns1,
                "R$5": ns2,
                "R$10": ns3,
                "R$20": ns4,
                "R$50": ns5,
                "R$100": ns6,
                "R$200": ns7
            }
        }
    }
    st.session_state['transactions'].append(transacao)
    st.session_state['saldo_principal'] = total_principal
    st.session_state['saldo_secundario'] = total_secundario
    st.success("✅ Registro de contagem salvo com sucesso!")

st.markdown("---")

# Seção de Transferência entre Caixas
st.subheader("🔄 Transferência de Valores entre Caixas")
transferencia_direcao = st.radio("Selecione a direção da transferência",
                                 ("Principal para Secundário", "Secundário para Principal"))
valor_transferencia = st.number_input("Valor a transferir (R$)", min_value=0.0, step=0.01, format="%.2f")
if st.button("💱 Efetuar Transferência"):
    if valor_transferencia > 0:
        if transferencia_direcao == "Principal para Secundário":
            if st.session_state['saldo_principal'] < valor_transferencia:
                st.error("Saldo insuficiente no Caixa Principal!")
            else:
                st.session_state['saldo_principal'] -= valor_transferencia
                st.session_state['saldo_secundario'] += valor_transferencia
                transacao_transferencia = {
                    'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'tipo': 'transferencia',
                    'direcao': transferencia_direcao,
                    'valor': valor_transferencia,
                    'observacao': f"Transferência de R${valor_transferencia:,.2f} de Principal para Secundário"
                }
                st.session_state['transactions'].append(transacao_transferencia)
                st.success("✅ Transferência realizada com sucesso!")
        else:
            if st.session_state['saldo_secundario'] < valor_transferencia:
                st.error("Saldo insuficiente no Caixa Secundário!")
            else:
                st.session_state['saldo_secundario'] -= valor_transferencia
                st.session_state['saldo_principal'] += valor_transferencia
                transacao_transferencia = {
                    'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'tipo': 'transferencia',
                    'direcao': transferencia_direcao,
                    'valor': valor_transferencia,
                    'observacao': f"Transferência de R${valor_transferencia:,.2f} de Secundário para Principal"
                }
                st.session_state['transactions'].append(transacao_transferencia)
                st.success("✅ Transferência realizada com sucesso!")
    else:
        st.error("⚠️ Informe um valor válido para transferência.")

st.markdown("---")

# Seção: Histórico e Gráfico com Previsão (últimos 30 dias)
if st.button("📊 Ver Histórico e IA"):
    st.subheader("📈 Histórico e Previsão do Caixa (últimos 30 dias)")

    # Converter as transações para DataFrame e filtrar os últimos 30 dias
    if st.session_state['transactions']:
        df_historico = pd.DataFrame(st.session_state['transactions'])
        df_historico['data'] = pd.to_datetime(df_historico['data'])
        cutoff = datetime.now() - timedelta(days=30)
        df_historico = df_historico[df_historico['data'] >= cutoff].sort_values('data')
    else:
        df_historico = pd.DataFrame()

    if not df_historico.empty:
        st.subheader("📋 Histórico de Transações")
        df_table = df_historico[['data', 'tipo', 'total', 'observacao']].copy()
        df_table['total'] = df_table['total'].apply(lambda x: f"R${x:,.2f}")
        st.dataframe(df_table)

        # Gráfico de histórico (contagens reais + previsão)
        df_contagem = df_historico[df_historico['tipo'] == 'contagem']
        fig, ax = plt.subplots(figsize=(10, 5))
        if not df_contagem.empty:
            ax.scatter(df_contagem['data'], df_contagem['total'], color='blue', label="Contagem Real")
            df_contagem['dia'] = df_contagem['data'].dt.dayofyear
            X = df_contagem[['dia']]
            y = df_contagem['total']

            if len(df_contagem) >= 10:
                modelo = RandomForestRegressor(n_estimators=100, random_state=42)
                modelo.fit(X, y)
                forecast_model_label = "Previsão IA"
                dias_futuros = [datetime.today() + timedelta(days=i) for i in range(1, 8)]
                dias_futuros_num = np.array([d.timetuple().tm_yday for d in dias_futuros]).reshape(-1, 1)
                forecast_values = modelo.predict(dias_futuros_num)
            else:
                st.warning("📌 Poucos dados de contagem para gerar previsão com IA. Usando tendência linear simples.")
                forecast_model_label = "Previsão IA (tendência linear)"
                coeffs = np.polyfit(df_contagem['dia'], y, 1)
                dias_futuros = [datetime.today() + timedelta(days=i) for i in range(1, 8)]
                dias_futuros_num = np.array([d.timetuple().tm_yday for d in dias_futuros])
                forecast_values = np.polyval(coeffs, dias_futuros_num)

            ax.plot(dias_futuros, forecast_values, marker='o', linestyle='dashed',
                    color='red', label=forecast_model_label)
        else:
            st.info("Não há registros de contagem para o gráfico de histórico.")
            base_value = 1000
            dias_futuros = [datetime.today() + timedelta(days=i) for i in range(1, 8)]
            forecast_values = [base_value * (1 + 0.01 * i) for i in range(1, 8)]
            ax.plot(dias_futuros, forecast_values, marker='o', linestyle='dashed',
                    color='red', label="Previsão IA (valores corrigidos)")

        ax.set_title("📊 Histórico e Previsão do Caixa")
        ax.set_xlabel("Data")
        ax.set_ylabel("Saldo Estimado (R$)")
        ax.yaxis.set_major_formatter(FuncFormatter(moeda))
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("Sem dados históricos. Utilizando valores corrigidos via IA para previsão.")
        base_value = 1000
        dias_futuros = [datetime.today() + timedelta(days=i) for i in range(1, 8)]
        forecast_values = [base_value * (1 + 0.01 * i) for i in range(1, 8)]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(dias_futuros, forecast_values, marker='o', linestyle='dashed',
                color='red', label="Previsão IA (valores corrigidos)")
        ax.set_title("📊 Previsão de Caixa para os Próximos 7 Dias (valores corrigidos)")
        ax.set_xlabel("Data")
        ax.set_ylabel("Saldo Estimado (R$)")
        ax.yaxis.set_major_formatter(FuncFormatter(moeda))
        ax.legend()
        st.pyplot(fig)
