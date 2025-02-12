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

# Service-related columns
service_columns = ['Phone Service', 'Internet Service', 'Multiple Lines',
                   'Streaming TV', 'Streaming Movies', 'Streaming Music',
                   'Online Security', 'Online Backup','Device Protection Plan',
                   'Premium Tech Support','Unlimited Data']

# Calculate churn rate for each service
churn_rates = {}

df_clean_ = df_updated.copy()

# Convert 'Churn Label' to numeric (if not already)
df_clean_['Churn Label'] = df_clean_['Churn Label'].map({'Yes': 1, 'No': 0})

for service in service_columns:
    # Group by the service column and calculate the churn rate (mean of 'Churn' column)
    churn_rate = df_clean_.groupby(service)['Churn Label'].mean() * 100  # Churn rate as percentage
    churn_rates[service] = churn_rate


# Convert the churn rates dictionary to a DataFrame for better visualization
churn_rates_df = pd.DataFrame(churn_rates)

# Plotting churn rates for each service with added legend for better descriptiveness
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the churn rates for "No" and "Yes" categories
churn_data.T.plot(kind='bar', ax=ax, width=0.8, position=0, color=['skyblue', 'salmon'])

# Add labels and title
ax.set_xlabel('Service')
ax.set_ylabel('Churn Rate (%)')
ax.set_title('Churn Rate Comparison by Service')

# Set X-axis labels with rotation
ax.set_xticklabels(churn_data.columns, rotation=45, ha='right')

# Add legend
ax.legend(['No Churn', 'Yes Churn'], loc='upper left')

# Show the plot
plt.tight_layout()
plt.show()


