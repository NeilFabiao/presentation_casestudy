import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the telco dataset
df = pd.read_csv('telco.csv')

# Clean the dataset (replace NaN with 'Unknown' in certain columns)
cols_to_change = ['Churn Reason', 'Churn Category', 'Internet Type', 'Offer']
df[cols_to_change] = df[cols_to_change].fillna('Unknown')

# Streamlit UI setup
st.set_page_config(page_title="Análise de Churn de Telco", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.title("Análise de Churn de Telco 📊")
st.write("Este relatório fornece insights sobre os padrões de churn e estratégias para melhorar a retenção de clientes.")
st.write('---')

# Sidebar for gender and churn status selection
with st.sidebar:
    st.title("Telco Customer Churn Dashboard")
    st.write("In this section, we can select the different filters we wish to see.")
    
    # Gender selection using radio buttons
    gender_filter = st.radio("Select Gender", options=["All", "Male", "Female"], index=0)
    # Churn selection using radio buttons
    churn_filter = st.radio("Select Churn Status", options=["Yes", "No"], index=0)

# Filter the DataFrame based on selected gender and churn status
if gender_filter != "All":
    df_updated = df[df['Gender'] == gender_filter].copy()
else:
    df_updated = df.copy()

# Apply the churn status filter
if churn_filter == "All":
    df_clean_ = df_updated.copy()  # Do not map 'Churn Label' if "All" is selected
else:
    # Map 'Yes' to 1 and 'No' to 0 based on churn status selection
    df_clean_ = df_updated.copy()
    df_clean_['Churn Label'] = df_clean_['Churn Label'].map({'Yes': 1, 'No': 0}) if churn_filter == "Yes" else df_clean_['Churn Label'].map({'Yes': 0, 'No': 1})

# Part 1: Which services tend to have high churn?
st.write('### Question 1: Which services tend to have high churn?')

# Service-related columns
service_columns = ['Phone Service', 'Internet Service', 'Multiple Lines',
                   'Streaming TV', 'Streaming Movies', 'Streaming Music',
                   'Online Security', 'Online Backup', 'Device Protection Plan',
                   'Premium Tech Support', 'Unlimited Data']

# Initialize dictionaries to store churn counts and percentages
service_counts = {}
service_churn_rates = {}

# Check for unique values in 'Churn Label' to ensure clean data
st.write("Unique values in 'Churn Label':", df_clean_['Churn Label'].unique())

# Calculate raw churn counts and churn percentages for each service
for service in service_columns:
    # Raw churn counts: Count churned customers (Churn Label == 1)
    churned_customers = df_clean_[df_clean_[service] == 'Yes']  # Customers who used this service
    churn_count = churned_customers[churned_customers['Churn Label'] == 1].shape[0]  # Count churned customers
    service_counts[service] = churn_count
    
    # Calculate churn percentage for each service (only for churned customers)
    total_service_users = df_clean_[df_clean_[service] == 'Yes'].shape[0]
    churn_percentage = (churn_count / total_service_users) * 100 if total_service_users > 0 else 0
    service_churn_rates[service] = churn_percentage

# Convert the service counts and churn rates dictionaries to DataFrames for better visualization
service_counts_df = pd.DataFrame(service_counts, index=['Churned Count']).T
service_churn_rates_df = pd.DataFrame(service_churn_rates, index=['Churn Percentage']).T

# Create two columns for displaying the table and the plot
col1, col2 = st.columns(2)

# Column 1: Display raw churn counts table
with col1:
    st.markdown("### Raw Churn Counts by Service")
    st.write(service_counts_df.sort_values(by="Churned Count", ascending=False))

# Column 2: Display churn percentage graph
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
