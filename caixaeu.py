import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# 📌 Configurar a página para modo Wide
st.set_page_config(page_title="Caixa - IA Previsão", layout="wide")

# 📌 Carregar variáveis do ambiente
load_dotenv()
GOOGLE_CLOUD_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")
MODEL_ENDPOINT = "https://us-central1-YOUR-PROJECT.cloudfunctions.net/seu_modelo"

# 📌 Inicialização do histórico de transações
if 'transactions' not in st.session_state:
    st.session_state['transactions'] = []

# 📌 Exibir campos para entrada de valores
st.subheader("Controle de Caixa Rota 66 Conveniência")

# 📌 Layout com duas colunas para os caixas
col1, col2 = st.columns(2)

# 📌 Caixa Principal
with col1:
    st.subheader("📌 Caixa Principal")
    moedas_principal = [st.number_input(f"Moedas de R${v:,.2f} (Principal)", min_value=0, step=1) for v in
                        [0.05, 0.10, 0.25, 0.50, 1.00]]
    notas_principal = [st.number_input(f"Notas de R${v:,.2f} (Principal)", min_value=0, step=1) for v in
                       [2, 5, 10, 20, 50, 100, 200]]

    total_principal = sum(q * v for q, v in zip(moedas_principal, [0.05, 0.10, 0.25, 0.50, 1.00])) + \
                      sum(q * v for q, v in zip(notas_principal, [2, 5, 10, 20, 50, 100, 200]))

    st.write(f"💰 **Total do Caixa Principal: R${total_principal:,.2f}**")

# 📌 Caixa Secundário
with col2:
    st.subheader("📌 Caixa Secundário")
    moedas_secundario = [st.number_input(f"Moedas de R${v:,.2f} (Secundário)", min_value=0, step=1) for v in
                         [0.05, 0.10, 0.25, 0.50, 1.00]]
    notas_secundario = [st.number_input(f"Notas de R${v:,.2f} (Secundário)", min_value=0, step=1) for v in
                        [2, 5, 10, 20, 50, 100, 200]]

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
df_historico = pd.DataFrame(st.session_state['transactions'])

# 📌 Criar gráfico de movimentação financeira baseado no histórico
if st.button("📊 Ver Histórico e IA"):
    st.subheader("📈 📡 Histórico e Previsão do Caixa")

    if not df_historico.empty:
        df_historico['data'] = pd.to_datetime(df_historico['data'])
        df_historico = df_historico.set_index('data')

        # 📌 Criar previsão usando IA ou modelo local
        df_previsao = None
        if 'total' in df_historico.columns:
            if len(df_historico) >= 10:
                df_historico['dia'] = df_historico.index.dayofyear
                X = df_historico[['dia']]
                y = df_historico['total']

                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                modelo = RandomForestRegressor(n_estimators=100, random_state=42)
                modelo.fit(X_train, y_train)

                dias_futuros = [datetime.today() + timedelta(days=i) for i in range(1, 8)]
                dias_futuros_num = np.array([d.timetuple().tm_yday for d in dias_futuros]).reshape(-1, 1)
                previsao_local = modelo.predict(dias_futuros_num)

                df_previsao = pd.DataFrame({'Data': dias_futuros, 'Previsão Total': previsao_local})
            else:
                headers = {"Authorization": f"Bearer {GOOGLE_CLOUD_API_KEY}", "Content-Type": "application/json"}

                # 📌 Conversão correta de datas para string para evitar erro JSON
                df_historico_resetado = df_historico.reset_index()
                df_historico_resetado['data'] = df_historico_resetado['data'].dt.strftime('%Y-%m-%d %H:%M:%S')
                historico_json = df_historico_resetado.to_dict(orient="records")

                payload = json.dumps({"historico": historico_json})  # 🔥 Corrigido!

                response = requests.post(MODEL_ENDPOINT, data=payload, headers=headers)

                if response.status_code == 200:
                    df_previsao = pd.DataFrame(response.json())
                else:
                    st.error(f"❌ Erro ao conectar com a IA: {response.status_code}")

        # 📌 Exibir gráfico
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(df_historico.index, df_historico['total'], color='blue', label="Histórico Real (Caixa)", alpha=0.7)

        if df_previsao is not None:
            ax.plot(df_previsao['Data'], df_previsao['Previsão Total'], marker='o', linestyle='dashed', color='red',
                    label="Previsão da IA")

        ax.set_title("📊 Histórico e Previsão do Caixa")
        ax.set_xlabel("Data")
        ax.set_ylabel("Saldo Estimado (R$)")
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning("📌 Nenhuma transação registrada ainda.")
