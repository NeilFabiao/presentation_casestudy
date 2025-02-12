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

# Sidebar for gender selection
with st.sidebar:
    st.title("Telco customer churn dashboard")
    st.write("In this section we can select the different filters we wish to see")
    
    # Gender selection using radio buttons
    gender_filter = st.radio("Select Gender", options=["All", "Male", "Female"], index=0)
    # Churn selection using radio buttons
    churn_filter = st.radio("Select Churn Status", options=["All", "Yes", "No"], index=0)


if gender_filter != "All":
    df_updated = df[df['Gender'] == gender_filter].copy()
else:
    df_updated = df.copy()

if churn_filter != "All":
    df_updated = df_updated[df_updated['Churn Label'] == churn_filter].copy()
else:
    df_updated = df_updated.copy()

#Main panel this is where we start answering the questions


#Part 1: Which services tend to have high churn?
st.write('Question 1:  Which services tend to have high churn')

# Service-related columns
service_columns = ['Phone Service', 'Internet Service', 'Multiple Lines',
                   'Streaming TV', 'Streaming Movies', 'Streaming Music',
                   'Online Security', 'Online Backup','Device Protection Plan',
                   'Premium Tech Support','Unlimited Data']

#control point for dataset
df_clean_ = df_updated.copy()

# Initialize dictionaries to store churn counts and percentages
service_counts = {}
service_churn_rates = {}

# Convert 'Churn Label' to numeric (if not already)
df_clean_['Churn Label'] = df_clean_['Churn Label'].map({'Yes': 1, 'No': 0})

# Calculate raw churn counts and churn rates for each service
for service in service_columns:
    churned_customers = df_clean_[df_clean_[service] == 'Yes']  # Customers who used this service and churned
    churn_count = churned_customers[churned_customers['Churn Label'] == 1].shape[0]  # Count churned customers
    service_counts[service] = churn_count
    
    # Calculate churn percentage for each service
    total_service_users = df_clean_[df_clean_[service] == 'Yes'].shape[0]
    churn_percentage = (churn_count / total_service_users) * 100 if total_service_users > 0 else 0
    service_churn_rates[service] = churn_percentage

# Convert the service counts and churn rates dictionaries to DataFrames for better visualization
service_counts_df = pd.DataFrame(service_counts, index=['Churned Count']).T
service_churn_rates_df = pd.DataFrame(service_churn_rates, index=['Churn Percentage']).T

# Display the churn counts in a table and churn percentage graph
col1, col2 = st.columns(2)

# Column 1: Raw churn counts table
with col1:
    st.markdown("### Raw Churn Counts by Service")
    st.write(service_counts_df.sort_values(by="Churned Count", ascending=False))

# Column 2: Churn percentage as bar chart
with col2:
    st.markdown("### Churn Percentage Comparison")
    fig, ax = plt.subplots(figsize=(10, 6))
    service_churn_rates_df.T.plot(kind='bar', ax=ax, width=0.8, color='salmon')

    # Add labels and title
    ax.set_xlabel('Service')
    ax.set_ylabel('Churn Percentage (%)')
    ax.set_title('Churn Percentage Comparison by Service')

    # Set X-axis labels with rotation
    ax.set_xticklabels(service_churn_rates_df.columns, rotation=45, ha='right')

    # Display the plot in Streamlit
    st.pyplot(fig)


