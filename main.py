# Import necessary libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go  # Import graph objects
import seaborn as sns
import matplotlib.pyplot as plt

# Load the telco dataset from a CSV file
telco_data = pd.read_csv('telco.csv')

# Streamlit UI setup
st.set_page_config(page_title="Telco Churn Analysis Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.title("Telco Churn Analysis 📊")
st.write("This dashboard provides insights into customer churn patterns and strategies for improving customer retention.")
st.write('---')

# Define columns layout for the main panel
col1, col2 = st.columns((2, 3, 2), gap="medium")

# Column 1: Visualizing churn rate by service type
with col1:
    st.markdown('### Churn Rate by Service Type')
    churn_by_service = telco_data.groupby('Service')['Churn'].mean().reset_index()
    fig = px.bar(churn_by_service, x='Service', y='Churn', title="Churn Rate by Service Type")
    st.plotly_chart(fig)

# Column 2: Display dataset information and first few rows
with col2:
    st.markdown('### Dataset Overview')
    st.write("""
    The dataset contains customer information from a telecommunications company. It includes features such as service usage, 
    customer demographics, and whether the customer has churned.
    """)
    st.write(telco_data.head())

# Additional Section: Correlation heatmap for features
st.header("Correlation Heatmap")
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(telco_data.corr(), annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig)

# Additional visualizations or analysis can be added below
