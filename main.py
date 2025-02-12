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




# Additional visualizations or analysis can be added below
