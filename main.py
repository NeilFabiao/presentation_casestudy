import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Load the telco dataset
df = pd.read_csv('telco.csv')

# Definir as colunas a serem alteradas (estas colunas foram identificadas no jupyter notebook desta repo)
cols_to_change = ['Churn Reason', 'Churn Category', 'Internet Type', 'Offer']

# Substituir valores NaN por 'Unknown' (Desconhecido)
df[cols_to_change] = df[cols_to_change].fillna('Unknown')

# Streamlit UI setup Part 1
st.set_page_config(page_title="Análise de Churn de Telco", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.title("Análise de Churn de Telco 📊")
st.write("Este relatório fornece insights sobre os padrões de churn e estratégias para melhorar a retenção de clientes.")
st.write('---')

# Sidebar for user inputs
with st.sidebar:
    st.title("Input Filters")
    
    # Gender selection using radio buttons
    gender_filter = st.radio("Select Gender", options=["All", "Male", "Female"], index=0)
    
    # Churn selection using radio buttons
    churn_filter = st.radio("Select Churn Status", options=["All", "Yes", "No"], index=0)

# Filter the DataFrame based on selections
if gender_filter != "All":
    df = df[df['Gender'] == gender_filter]

if churn_filter != "All":
    df = df[df['Churn'] == churn_filter]

# Check if the filtered DataFrame is empty
if df.empty:
    st.write("No data available for the selected filters.")
else:
    # Display the filtered data
    st.markdown(f"### Filtered Data: Gender = {gender_filter}, Churn = {churn_filter}")
    st.write(df)

    # Streamlit UI setup Part 2
    # Add additional summary metrics like average tenure and monthly charges
    average_tenure = df['tenure'].mean()
    average_monthly_charges = df['MonthlyCharges'].mean()
    gender_counts = df['Gender'].value_counts()
    male_to_female_ratio = f"{gender_counts.get('Male', 0)}:{gender_counts.get('Female', 0)}"
    
    # Display summary metrics
    st.markdown("### Summary Metrics")
    st.write({
        "Average Tenure": round(average_tenure, 2),
        "Average Monthly Charges": round(average_monthly_charges, 2),
        "Male to Female Ratio": male_to_female_ratio
    })
