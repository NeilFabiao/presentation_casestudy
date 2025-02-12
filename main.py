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
    st.write("In this section we can select the different filters we wish to see.")
    
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
service_churn_percentage = {}

# Calculate churn percentage for each service
for service in service_columns:
    # Raw churn counts: Count churned customers (Churn Label == 1)
    churned_customers = df_clean_[df_clean_[service] == 'Yes']  # Customers who used this service
    churn_count = churned_customers[churned_customers['Churn Label'] == 1].shape[0]  # Count churned customers
    
    # Calculate churn percentage for each service
    total_service_users = df_clean_[df_clean_[service] == 'Yes'].shape[0]
    churn_percentage = (churn_count / total_service_users) * 100 if total_service_users > 0 else 0
    service_churn_percentage[service] = churn_percentage

# Convert the churn percentages to a DataFrame for better visualization
service_churn_percentage_df = pd.DataFrame(service_churn_percentage, index=['Churn Percentage']).T

# Create two columns for displaying the table and the plot
col1, col2 = st.columns(2)

# Column 1: Display raw churn counts for the top 5 services in a cute, styled way
with col1:
    st.markdown("### Top 5 Services")
    top_5_services = service_churn_percentage_df.sort_values(by="Churn Percentage", ascending=False).head(5)
    st.dataframe(top_5_services)  # Display the top 5 services table

# Column 2: Display churn percentage graph
with col2:
    st.markdown("### Churn Percentage Comparison by Service")
    
    # Create the bar chart for churn percentages
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot churn percentage
    service_churn_percentage_df.plot(kind='bar', ax=ax, width=0.8, color='salmon')

    # Add labels and title
    ax.set_xlabel('Service')
    ax.set_ylabel('Churn Percentage (%)')
    ax.set_title('Churn Percentage Comparison by Service')

    # Set X-axis labels and apply rotation
    ax.set_xticks(range(len(service_churn_percentage_df.columns)))  # Set the ticks to match number of services
    ax.set_xticklabels(service_churn_percentage_df.columns, rotation=45, ha='right')  # Rotate labels for better readability

    # Apply tight layout to prevent overlap of labels
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(fig)

