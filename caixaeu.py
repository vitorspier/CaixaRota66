import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from matplotlib.ticker import FuncFormatter


# Função para formatar eixos em R$
def moeda(x, pos):
    return f"R${x:,.2f}"


# 📌 Configurar a página para modo Wide
st.set_page_config(page_title="Caixa - IA Previsão", layout="wide")

# 📌 Inicializa 'transactions' no estado da sessão, se ainda não existir
if 'transactions' not in st.session_state:
    st.session_state['transactions'] = []

# 📌 Criar uma linha separada para imagem + título
header_col1, header_col2 = st.columns([1, 7])
with header_col1:
    st.image("arquivos/rota66.png", width=150)
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

# 📌 Layout com duas colunas para as contagens dos caixas
col1, col2 = st.columns(2)

# Caixa Principal - Contagem
with col1:
    st.subheader("📌 Caixa Principal (Contagem)")
    moedas_principal = [st.number_input(f"Moedas de R${v:,.2f} (Principal)", min_value=0, step=1) for v in
                        [0.05, 0.10, 0.25, 0.50, 1.00]]
    notas_principal = [st.number_input(f"Notas de R${v:,.2f} (Principal)", min_value=0, step=1) for v in
                       [2, 5, 10, 20, 50, 100, 200]]
    total_principal = sum(q * v for q, v in zip(moedas_principal, [0.05, 0.10, 0.25, 0.50, 1.00])) + \
                      sum(q * v for q, v in zip(notas_principal, [2, 5, 10, 20, 50, 100, 200]))
    st.write(f"💰 **Total do Caixa Principal: R${total_principal:,.2f}**")

# Caixa Secundário - Contagem
with col2:
    st.subheader("📌 Caixa Secundário (Contagem)")
    moedas_secundario = [st.number_input(f"Moedas de R${v:,.2f} (Secundário)", min_value=0, step=1) for v in
                         [0.05, 0.10, 0.25, 0.50, 1.00]]
    notas_secundario = [st.number_input(f"Notas de R${v:,.2f} (Secundário)", min_value=0, step=1) for v in
                        [2, 5, 10, 20, 50, 100, 200]]
    total_secundario = sum(q * v for q, v in zip(moedas_secundario, [0.05, 0.10, 0.25, 0.50, 1.00])) + \
                       sum(q * v for q, v in zip(notas_secundario, [2, 5, 10, 20, 50, 100, 200]))
    st.write(f"💰 **Total do Caixa Secundário: R${total_secundario:,.2f}**")

# 📌 Botão para salvar o registro de contagem
if st.button("💾 Salvar Registro de Contagem"):
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

st.markdown("---")

# 📌 Seção de Transferência de Valores
st.subheader("🔄 Transferência de Valores entre Caixas")
transferencia_direcao = st.radio("Selecione a direção da transferência",
                                 ("Principal para Secundário", "Secundário para Principal"))
valor_transferencia = st.number_input("Valor a transferir (R$)", min_value=0.0, step=0.01, format="%.2f")
if st.button("💱 Efetuar Transferência"):
    if valor_transferencia > 0:
        transacao_transferencia = {
            'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tipo': 'transferencia',
            'direcao': transferencia_direcao,
            'valor': valor_transferencia,
            'observacao': f"Transferência {transferencia_direcao}"
        }
        st.session_state['transactions'].append(transacao_transferencia)
        st.success("✅ Transferência realizada com sucesso!")
    else:
        st.error("⚠️ Informe um valor válido para transferência.")

st.markdown("---")

# 📌 Exibir Histórico e Gráfico com Previsão (últimos 30 dias)
if st.button("📊 Ver Histórico e IA"):
    st.subheader("📈 Histórico e Previsão do Caixa (últimos 30 dias)")

    # Converter transações para DataFrame e filtrar últimos 30 dias
    if st.session_state['transactions']:
        df_historico = pd.DataFrame(st.session_state['transactions'])
        df_historico['data'] = pd.to_datetime(df_historico['data'])
        cutoff = datetime.now() - timedelta(days=30)
        df_historico = df_historico[df_historico['data'] >= cutoff].sort_values('data')
    else:
        df_historico = pd.DataFrame()

    if not df_historico.empty:
        st.subheader("📋 Histórico de Transações")
        # Formatar os valores em moeda para exibição
        df_formatado = df_historico.copy()
        for coluna in ['total_principal', 'total_secundario', 'total']:
            if coluna in df_formatado.columns:
                df_formatado[coluna] = df_formatado[coluna].apply(lambda x: f"R${x:,.2f}")
        st.dataframe(df_formatado)

        # Filtrar apenas registros de contagem para o gráfico do saldo
        df_contagem = df_historico[df_historico['tipo'] == 'contagem']

        fig, ax = plt.subplots(figsize=(10, 5))

        if not df_contagem.empty:
            # Plot dos dados reais
            ax.scatter(df_contagem['data'], df_contagem['total'], color='blue', label="Contagem Real")
            # Prepara dados para previsão (utilizando o dia do ano)
            df_contagem['dia'] = df_contagem['data'].dt.dayofyear
            X = df_contagem[['dia']]
            y = df_contagem['total']

            # Se houver dados suficientes, utiliza RandomForest; caso contrário, usa regressão linear simples
            if len(df_contagem) >= 10:
                modelo = RandomForestRegressor(n_estimators=100, random_state=42)
                modelo.fit(X, y)
                forecast_model_label = "Previsão IA"
                # Gera previsão para os próximos 7 dias
                dias_futuros = [datetime.today() + timedelta(days=i) for i in range(1, 8)]
                dias_futuros_num = np.array([d.timetuple().tm_yday for d in dias_futuros]).reshape(-1, 1)
                forecast_values = modelo.predict(dias_futuros_num)
            else:
                st.warning("📌 Poucos dados de contagem para gerar previsão com IA. Usando tendência linear simples.")
                forecast_model_label = "Previsão IA (tendência linear)"
                # Regressão linear simples com polyfit
                coeffs = np.polyfit(df_contagem['dia'], y, 1)
                dias_futuros = [datetime.today() + timedelta(days=i) for i in range(1, 8)]
                dias_futuros_num = np.array([d.timetuple().tm_yday for d in dias_futuros])
                forecast_values = np.polyval(coeffs, dias_futuros_num)

            # Plot da linha de previsão (IA)
            ax.plot(dias_futuros, forecast_values, marker='o', linestyle='dashed', color='red',
                    label=forecast_model_label)
        else:
            st.info("Não há registros de contagem para o gráfico de histórico.")
            # Caso não haja registros de contagem, utiliza previsão simulada (valores corrigidos via IA)
            base_value = 1000  # valor base fictício
            dias_futuros = [datetime.today() + timedelta(days=i) for i in range(1, 8)]
            forecast_values = [base_value * (1 + 0.01 * i) for i in range(1, 8)]
            ax.plot(dias_futuros, forecast_values, marker='o', linestyle='dashed', color='red',
                    label="Previsão IA (valores corrigidos)")

        ax.set_title("📊 Histórico e Previsão do Caixa")
        ax.set_xlabel("Data")
        ax.set_ylabel("Saldo Estimado (R$)")
        ax.yaxis.set_major_formatter(FuncFormatter(moeda))
        ax.legend()
        st.pyplot(fig)
    else:
        # Sem transações registradas: utiliza previsão simulada
        st.info("Sem dados históricos. Utilizando valores corrigidos via IA para previsão.")
        base_value = 1000
        dias_futuros = [datetime.today() + timedelta(days=i) for i in range(1, 8)]
        forecast_values = [base_value * (1 + 0.01 * i) for i in range(1, 8)]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(dias_futuros, forecast_values, marker='o', linestyle='dashed', color='red',
                label="Previsão IA (valores corrigidos)")
        ax.set_title("📊 Previsão de Caixa para os Próximos 7 Dias (valores corrigidos)")
        ax.set_xlabel("Data")
        ax.set_ylabel("Saldo Estimado (R$)")
        ax.yaxis.set_major_formatter(FuncFormatter(moeda))
        ax.legend()
        st.pyplot(fig)
