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

st.title("Churn Analysis by Service")

# Column layout
col1, col2, col3 = st.columns([1, 2, 1])  # Adjust column widths as needed

# --- Column 1: Counts Table ---
with col1:
    st.subheader("Churn Counts")

    churned_customers = df_clean_[df_clean_['Churn Label'] == 1]
    service_counts = {}
    for service in service_columns:
        churn_yes = churned_customers[churned_customers[service] == 'Yes'].shape[0]
        service_counts[service] = churn_yes

    service_counts_df = pd.DataFrame(service_counts, index=['Count']).T
    st.dataframe(service_counts_df)  # Display as a Streamlit DataFrame

# --- Column 2: Percentage Visualization ---
with col2:
    st.subheader("Churn Percentage Visualization")

    total_churned = churned_customers.shape[0]
    service_percentages = {}

    for service, count in service_counts.items():
        percentage = (count / total_churned) * 100 if total_churned > 0 else 0
        service_percentages[service] = percentage

    service_percentages_df = pd.DataFrame(service_percentages, index=['Percentage']).T

    #Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    service_percentages_df.sort_values(by="Percentage", ascending=False).plot(kind='bar', ax=ax, color='skyblue')
    ax.set_ylabel('Percentage of Churned Customers')
    ax.set_title('Service Association with Churn')
    ax.set_xticklabels(service_percentages_df.sort_values(by="Percentage", ascending=False).index, rotation=45, ha='right')

    st.pyplot(fig)


# --- Column 3: Explanation ---
with col3:
    st.subheader("Interpretation")
    st.write("This analysis shows the relationship between different services and customer churn.")
    st.write("The table on the left shows the raw counts of churned customers who used each service.")
    st.write("The bar chart visualizes the *percentage* of churned customers associated with each service, sorted from highest to lowest.")
    st.write("A high percentage on the chart indicates that a service is strongly associated with churn, even if the raw count is not very high.  Focus on these services for further investigation.")
    st.write("For Example: If 'Online Security' has a high percentage, it means customers with 'Online Security' are more likely to churn.")
