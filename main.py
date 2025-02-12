import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------
# 1. Data Loading and Preprocessing
# ----------------------------------
@st.cache_data
def load_data(csv_path):
    """Loads the telco dataset and fills specific NaNs with 'Unknown'."""
    df_ = pd.read_csv(csv_path)
    cols_to_change = ['Churn Reason', 'Churn Category', 'Internet Type', 'Offer']
    for col in cols_to_change:
        if col in df_.columns:
            df_[col] = df_[col].fillna('Unknown')
    return df_

# Load the dataset
df = load_data('telco.csv')

# -------------------------------------------------
# 2. Streamlit Page Configuration and Main Heading
# -------------------------------------------------
st.set_page_config(
    page_title="Telco Churn Analysis", 
    page_icon="📊", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.title("📊 Telco Customer Churn Dashboard")
st.write("This dashboard provides insights into churn patterns and strategies for improving customer retention.")
st.write('---')
