import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Load the telco dataset from a CSV file
telco_data = pd.read_csv('telco.csv')

# Streamlit UI setup
st.set_page_config(page_title="Análise de Churn de Telco", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.title("Análise de Churn de Telco 📊")
st.write("Este relatorio fornece insights sobre os padrões de churn e estratégias para melhorar a retenção de clientes.")
st.write('---')

# Add a new section for NaN replacement and counting unique values
with st.expander("Análise de Valores em Falta"):
    st.write("Nesta secção, lidamos com os valores em falta e analisamos a distribuição na base de dados")
    
    # Define the columns to change
    cols_to_change = ['Churn Reason', 'Churn Category', 'Internet Type', 'Offer']
    
    # Replace NaN values with 'Unknown'
    telco_data[cols_to_change] = telco_data[cols_to_change].fillna('Unknown')
    
    # Display unique values in 'Churn Reason' after replacement
    st.write("Valores únicos em 'Churn Reason' após substituição de NaN:")
    st.write(telco_data['Churn Reason'].unique())
    
    # Count the occurrences of each unique value in 'Churn Reason'
    churn_reason_counts = telco_data['Churn Reason'].value_counts()
    st.write("\nContagem de cada valor único em 'Churn Reason':")
    st.write(churn_reason_counts)



# Additional visualizations or analysis can be added below
