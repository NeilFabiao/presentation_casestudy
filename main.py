import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Carregar o conjunto de dados telco a partir de um arquivo CSV
telco_data_raw = pd.read_csv('telco.csv')

# Definir as colunas a serem alteradas
cols_to_change = ['Churn Reason', 'Churn Category', 'Internet Type', 'Offer']

# Substituir valores NaN por 'Unknown' (Desconhecido)
df[cols_to_change] = df[cols_to_change].fillna('Unknown')

# Exibir os valores únicos após a substituição
print("Valores únicos em 'Churn Reason':")
print(df['Churn Reason'].unique())

# Contar a ocorrência de cada valor único em 'Churn Reason'
churn_reason_counts = df['Churn Reason'].value_counts()
print("\nContagem de cada valor único em 'Churn Reason':")
print(churn_reason_counts)


# Streamlit UI setup
st.set_page_config(page_title="Análise de Churn de Telco", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.title("Análise de Churn de Telco 📊")
st.write("Este relatorio fornece insights sobre os padrões de churn e estratégias para melhorar a retenção de clientes.")
st.write('---')




# Additional visualizations or analysis can be added below
