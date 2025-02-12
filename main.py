import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Load the telco dataset
df = pd.read_csv('telco.csv')

# Calculate the number of missing values in each column
missing_values_count = df.isnull().sum()

# Calculate the percentage of missing values in each column
missing_values_percentage = (missing_values_count / len(df)) * 100

# Create a DataFrame to display the results
missing_values_df = pd.DataFrame({
    'Column Name': missing_values_count.index,
    'Missing Values': missing_values_count,
    'Percentage Missing': missing_values_percentage
})

# Filter the DataFrame to show only rows with more than 5% missing values
filtered_missing_df = missing_values_df[missing_values_df['Percentage Missing'] > 5]

# Sort the DataFrame by 'Percentage Missing' in descending order
sorted_missing_df = filtered_missing_df.sort_values(by='Percentage Missing', ascending=False)

# Streamlit UI setup
st.set_page_config(page_title="Análise de Churn de Telco", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.title("Análise de Churn de Telco 📊")
st.write("Este relatório fornece insights sobre os padrões de churn e estratégias para melhorar a retenção de clientes.")
st.write('---')

# Create three columns for different content sections
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Análise de Valores Faltantes")
    # Display missing values data in markdown if there are any
    if not sorted_missing_df.empty:
        st.write(sorted_missing_df)
    else:
        st.write("Não há colunas com mais de 5% de valores ausentes.")
    st.write("""
    Como mais de 50% da proporção de dados estão ausentes nestas colunas, é melhor manter os dados para realizar algumas análises. 
    Excluir esses dados não traria os melhores resultados. Existem mais valores desconhecidos nessas 3 colunas, 
    então estamos mudando-os para 'Desconhecido' onde os dados do cliente não foram registrados.
    """)

with col2:
    st.markdown("### Outra Seção de Informações")
    st.write("Aqui você pode adicionar outra seção de conteúdo que pode ser útil. Por exemplo, informações adicionais sobre o churn, a importância dos dados de clientes, etc.")
    
    # You can replace the text above with any additional analysis or insight related to the data.
    
with col3:
    st.markdown("### Referencias")
st.write("""
**Citação e Referência do Conjunto de Dados**

O **Telco Customer Churn Dataset** da IBM contém dados sobre clientes de telecomunicações, 
utilizados para prever a probabilidade de cancelamento de serviços e analisar fatores que influenciam o churn. 
Disponível em :
- [Kaggle - Telco Customer Churn Dataset](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
- [Kaggle - Telco Customer Churn Dataset (Outro Link)](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)

**Referência:** IBM, 2021.
""")
""")

