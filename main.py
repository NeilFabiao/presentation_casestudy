import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Carregar o conjunto de dados telco a partir de um arquivo CSV
telco_data_raw = pd.read_csv('telco.csv')
df = telco_data_raw.copy()

# Definir as colunas a serem alteradas (estas colunas foram identificadas no jupyter notebook desta repo)
cols_to_change = ['Churn Reason', 'Churn Category', 'Internet Type', 'Offer']

# Substituir valores NaN por 'Unknown' (Desconhecido)
df[cols_to_change] = df[cols_to_change].fillna('Unknown')

# Exibir os valores únicos após a substituição
st.write("Valores únicos em 'Churn Reason':")
st.write(df['Churn Reason'].unique())


# Streamlit UI setup
st.set_page_config(page_title="Análise de Churn de Telco", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.title("Análise de Churn de Telco 📊")
st.write("Este relatorio fornece insights sobre os padrões de churn e estratégias para melhorar a retenção de clientes.")
st.write('---')




# Additional visualizations or analysis can be added below
