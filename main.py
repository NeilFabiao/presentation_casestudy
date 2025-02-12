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

# Initialize an empty dictionary to store raw counts of churned customers
service_counts = {}
service_percentages = {}

df_clean_ = df.copy()

# Convert 'Churn Label' to numeric (if not already)
df_clean_['Churn Label'] = df_clean_['Churn Label'].map({'Yes': 1, 'No': 0})

# Calculate churn rates for each service
for service in service_columns:
    churn_rate = df_clean_[df_clean_[service] == 'Yes']['Churn Label'].mean()  # Churn rate as proportion
    service_churn_rates[service] = churn_rate

# Convert churn rates to percentages
service_churn_rates = {service: churn_rate * 100 for service, churn_rate in service_churn_rates.items()}

# Get top 5 services with highest churn rates
top_5_churn_services = sorted(service_churn_rates.items(), key=lambda x: x[1], reverse=True)[:5]

# Show the top 5 services with highest churn rates in Streamlit
st.markdown("### Top 5 Services with Highest Churn Rates")
top_5_churn_services_df = pd.DataFrame(top_5_churn_services, columns=['Service', 'Churn Rate (%)'])
st.write(top_5_churn_services_df)

# Column layout for visualization (raw churn counts and churn rates)
col1, col2 = st.columns(2)

# Column 1: Raw churn counts table
with col1:
    st.markdown("### Raw Churn Counts by Service")
    # Raw churn counts: Counting the number of churned customers for each service
    service_counts = {}
    for service in service_columns:
        churned_customers = df_clean_[df_clean_[service] == 'Yes']  # Customers who used the service and churned
        churn_count = churned_customers[churned_customers['Churn Label'] == 1].shape[0]  # Count churned customers
        service_counts[service] = churn_count
    
    # Display churn counts in a table
    service_counts_df = pd.DataFrame(service_counts, index=['Churned Count']).T
    st.write(service_counts_df.sort_values(by="Churned Count", ascending=False))

# Column 2: Churn rate as percentages visualized in a bar chart
with col2:
    st.markdown("### Churn Rate Percentage Comparison")
    # Plotting churn percentage for each service
    fig, ax = plt.subplots(figsize=(10, 6))
    service_churn_rates_df = pd.DataFrame(service_churn_rates, index=['Churn Percentage']).T
    service_churn_rates_df.T.plot(kind='bar', ax=ax, width=0.8, color='salmon')

    # Add labels and title
    ax.set_xlabel('Service')
    ax.set_ylabel('Churn Percentage (%)')
    ax.set_title('Churn Percentage Comparison by Service')

    # Set X-axis labels with rotation
    ax.set_xticklabels(service_churn_rates_df.columns, rotation=45, ha='right')

    # Display the plot in Streamlit
    st.pyplot(fig)

