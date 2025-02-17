import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# 📌 Configurar a página para modo Wide
st.set_page_config(page_title="Caixa - IA Previsão", layout="wide")

# 📌 Inicializa 'transactions' no estado da sessão, se ainda não existir
if 'transactions' not in st.session_state:
    st.session_state['transactions'] = []

# 📌 Criar uma linha separada para imagem + título
header_col1, header_col2 = st.columns([1, 7])  # Define a largura das colunas do cabeçalho

# 📌 Insere a imagem no head1 (coluna 1)
with header_col1:
    st.image("arquivos/rota66.png", width=150)  # Substitua pelo nome correto da imagem

# 📌 Insere o título no head2 (coluna 2)
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

# 📌 Linha divisória para separar cabeçalho do conteúdo principal
st.markdown("---")

# 📌 Layout com duas colunas para os caixas
col1, col2 = st.columns(2)

# 📌 Caixa Principal
with col1:
    st.subheader("📌 Caixa Principal")
    moedas_principal = [st.number_input(f"Moedas de R${v:,.2f} (Principal)", min_value=0, step=1) for v in [0.05, 0.10, 0.25, 0.50, 1.00]]
    notas_principal = [st.number_input(f"Notas de R${v:,.2f} (Principal)", min_value=0, step=1) for v in [2, 5, 10, 20, 50, 100, 200]]

    total_principal = sum(q * v for q, v in zip(moedas_principal, [0.05, 0.10, 0.25, 0.50, 1.00])) + \
                      sum(q * v for q, v in zip(notas_principal, [2, 5, 10, 20, 50, 100, 200]))

    st.write(f"💰 **Total do Caixa Principal: R${total_principal:,.2f}**")

# 📌 Caixa Secundário
with col2:
    st.subheader("📌 Caixa Secundário")
    moedas_secundario = [st.number_input(f"Moedas de R${v:,.2f} (Secundário)", min_value=0, step=1) for v in [0.05, 0.10, 0.25, 0.50, 1.00]]
    notas_secundario = [st.number_input(f"Notas de R${v:,.2f} (Secundário)", min_value=0, step=1) for v in [2, 5, 10, 20, 50, 100, 200]]

    total_secundario = sum(q * v for q, v in zip(moedas_secundario, [0.05, 0.10, 0.25, 0.50, 1.00])) + \
                       sum(q * v for q, v in zip(notas_secundario, [2, 5, 10, 20, 50, 100, 200]))

    st.write(f"💰 **Total do Caixa Secundário: R${total_secundario:,.2f}**")

# 📌 Botão para salvar transação
if st.button("💾 Salvar Registro"):
    transacao = {
        'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_principal': total_principal,
        'total_secundario': total_secundario,
        'total': total_principal + total_secundario
    }
    st.session_state['transactions'].append(transacao)
    st.success("✅ Registro salvo com sucesso!")

# 📌 Criar DataFrame do histórico de transações
if st.session_state['transactions']:
    df_historico = pd.DataFrame(st.session_state['transactions'])
else:
    df_historico = pd.DataFrame(columns=['data', 'total_principal', 'total_secundario', 'total'])

# 📌 Exibir Histórico em Tabela e Gráfico
if st.button("📊 Ver Histórico e IA"):
    st.subheader("📈 📡 Histórico e Previsão do Caixa")

    if not df_historico.empty:
        df_historico['data'] = pd.to_datetime(df_historico['data'])
        df_historico = df_historico.set_index('data')

        # 📌 Exibir a Tabela do Histórico
        st.subheader("📋 Histórico de Transações")
        st.dataframe(df_historico)

        # 📌 Criar o gráfico de movimentação financeira
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(df_historico.index, df_historico['total'], color='blue', label="Histórico Real")
        ax.set_title("📊 Histórico do Caixa")
        ax.set_xlabel("Data")
        ax.set_ylabel("Saldo Estimado (R$)")
        ax.legend()
        st.pyplot(fig)

        # 📌 Criar previsão se houver mais de 10 registros
        if len(df_historico) >= 10:
            df_historico['dia'] = df_historico.index.dayofyear
            X = df_historico[['dia']]
            y = df_historico['total']

            modelo = RandomForestRegressor(n_estimators=100, random_state=42)
            modelo.fit(X, y)

            dias_futuros = [datetime.today() + timedelta(days=i) for i in range(1, 8)]
            dias_futuros_num = np.array([d.timetuple().tm_yday for d in dias_futuros]).reshape(-1, 1)
            previsao_local = modelo.predict(dias_futuros_num)

            df_previsao = pd.DataFrame({'Data': dias_futuros, 'Previsão Total': previsao_local})

            # 📌 Exibir gráfico com previsão IA
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df_previsao['Data'], df_previsao['Previsão Total'], marker='o', linestyle='dashed', color='red', label="Previsão IA")
            ax.set_title("📊 Previsão de Caixa para os Próximos 7 Dias")
            ax.set_xlabel("Data")
            ax.set_ylabel("Saldo Estimado (R$)")
            ax.legend()
            st.pyplot(fig)
        else:
            st.warning("📌 Poucos dados para gerar previsão.")

    else:
        st.warning("📌 Nenhuma transação registrada ainda.")
