import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Carregar o conjunto de dados telco a partir de um arquivo CSV
telco_data_raw = pd.read_csv('telco.csv')
df = telco_data_raw.copy()

#Part1:

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
st.write("Este relatorio fornece insights sobre os padrões de churn e estratégias para melhorar a retenção de clientes.")
st.write('---')





# Additional visualizations or analysis can be added below
