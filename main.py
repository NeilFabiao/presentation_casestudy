import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the telco dataset
df = pd.read_csv('telco.csv')

# Clean the dataset (replace NaN with 'Unknown' in certain columns)
cols_to_change = ['Churn Reason', 'Churn Category', 'Internet Type', 'Offer']
df[cols_to_change] = df[cols_to_change].fillna('Unknown')

# Streamlit UI setup
st.set_page_config(page_title="Telco Churn Analysis", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.title("📊 Telco Customer Churn Dashboard")
st.write("This dashboard provides insights into churn patterns and strategies for improving customer retention.")
st.write('---')

# Sidebar Filters
with st.sidebar:
    st.title("🔍 Filters")
    st.write("Use the filters below to explore churn trends.")

    # Gender filter
    gender_filter = st.radio("Select Gender", options=["All", "Male", "Female"], index=0)

    # Churn status filter
    churn_filter = st.radio("Select Churn Status", options=["Yes", "No"], index=0)

# Filter the DataFrame based on selected gender
df_updated = df if gender_filter == "All" else df[df['Gender'] == gender_filter].copy()

# Apply the churn status filter
if churn_filter == "Yes":
    df_clean_ = df_updated.copy()
    df_clean_['Churn Label'] = df_clean_['Churn Label'].map({'Yes': 1, 'No': 0})
    df_clean_ = df_clean_[df_clean_['Churn Label'] == 1]  # Keep only churned customers
else:
    df_clean_ = df_updated.copy()
    df_clean_['Churn Label'] = df_clean_['Churn Label'].map({'Yes': 0, 'No': 1})

st.write('### 📌 Question 1: Which Services Tend to Have High Churn?')

# Service-related columns
service_columns = ['Phone Service', 'Internet Service', 'Multiple Lines',
                   'Streaming TV', 'Streaming Movies', 'Streaming Music',
                   'Online Security', 'Online Backup', 'Device Protection Plan',
                   'Premium Tech Support', 'Unlimited Data']

# Calculate churn percentage for each service
service_churn_percentage = {}
for service in service_columns:
    churned_customers = df_clean_[df_clean_[service] == 'Yes']
    churn_count = churned_customers[churned_customers['Churn Label'] == 1].shape[0]
    total_service_users = df_clean_[df_clean_[service] == 'Yes'].shape[0]
    churn_percentage = (churn_count / total_service_users) * 100 if total_service_users > 0 else 0
    service_churn_percentage[service] = churn_percentage

# Convert the churn percentages to a DataFrame
service_churn_percentage_df = pd.DataFrame(service_churn_percentage, index=['Churn Percentage']).T

# Create two columns for displaying the table and the plot
col1, col2 = st.columns(2)

# Column 1: Display top 5 services
with col1:
    st.markdown("### 🏆 Top 5 Services by Churn Rate")
    top_5_services = service_churn_percentage_df.sort_values(by="Churn Percentage", ascending=False).head(5)
    st.dataframe(top_5_services)  # Display the top 5 services table

# Column 2: Display churn percentage graph
with col2:
    st.markdown("### 📊 Churn Percentage by Service")
    fig = px.bar(
        service_churn_percentage_df,
        x=service_churn_percentage_df.index,
        y="Churn Percentage",
        color="Churn Percentage",
        color_continuous_scale="viridis",
        title=None
    )
    fig.update_layout(
        xaxis_title="Service",
        yaxis_title="Churn Percentage (%)",
        xaxis_tickangle=-45,
        margin=dict(l=10, r=10, t=40, b=50),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig)

st.write('---')

# 📌 Question 2: Why Do Customers Churn?
st.write('### 📌 Question 2: What Would We Do to Reduce Churn?')

# Identify the top 5 churn reasons
top_churn_reasons = df_clean_['Churn Reason'].value_counts().head(5)

# Create two columns for displaying churn reasons and their geographical distribution
col1, col2 = st.columns(2)

# Column 1: Display the top 5 churn reasons
with col1:
    st.markdown("### 🏆 Top 5 Churn Reasons")
    df_top_reasons = top_churn_reasons.reset_index()
    df_top_reasons.columns = ['Churn Reason', 'Count']
    st.dataframe(df_top_reasons.set_index("Churn Reason"))

# Column 2: Geographical distribution of churned customers
with col2:
    st.markdown("### 🌍 Geographical Distribution of Top 5 Churn Reasons")
    if 'Latitude' in df_clean_.columns and 'Longitude' in df_clean_.columns:
        top_reason_data = df_clean_[df_clean_['Churn Reason'].isin(top_churn_reasons.index)]
        fig_map = px.scatter_mapbox(
            top_reason_data,
            lat="Latitude",
            lon="Longitude",
            color="Churn Reason",
            hover_name="Customer ID",
            zoom=4
        )
        fig_map.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig_map, use_container_width=True)

# Identify the top 5 churn Category
top_churn_category = df_clean_['Churn Category'].value_counts().head(5)

# Create two columns for displaying churn reasons and their geographical distribution
col1, col2 = st.columns(2)

# Column 1: Display the top 5 category reasons
with col1:
    st.markdown("### 🏆 Top 5 Churn Category")
    df_top_reasons = top_churn_reasons.reset_index()
    df_top_reasons.columns = ['Churn Reason', 'Count']
    st.dataframe(df_top_reasons.set_index("Churn Category"))

# Column 2: Geographical distribution of churned customers
with col2:
    st.markdown("### 🌍 Geographical Distribution of Top 5 Churn Category")
    if 'Latitude' in df_clean_.columns and 'Longitude' in df_clean_.columns:
        top_reason_data = df_clean_[df_clean_['Churn Category'].isin(top_churn_reasons.index)]
        fig_map = px.scatter_mapbox(
            top_reason_data,
            lat="Latitude",
            lon="Longitude",
            color="Churn Reason",
            hover_name="Customer ID",
            zoom=4
        )
        fig_map.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig_map, use_container_width=True)

st.write('---')

# 📌 Pie Charts: Customer Demographics & Contracts
st.write('### 📊 Customer Demographics & Contract Type Distribution')

# Apply proper filtering
churned_data = df_clean_.copy()

# Create age categories
def age_category(age):
    if age < 30:
        return 'Young Adults'
    elif 30 <= age < 50:
        return 'Middle-Aged Adults'
    else:
        return 'Seniors'

churned_data['AgeGroup'] = churned_data['Age'].apply(age_category)

# Pie chart for Age Group distribution
age_group_counts = churned_data['AgeGroup'].value_counts()
contract_counts = churned_data['Contract'].value_counts()

# Create a layout with two pie charts
col1, col2 = st.columns(2)

# Column 1: Pie chart for Age Group distribution
with col1:
    if not age_group_counts.empty:
        fig1 = go.Figure(go.Pie(labels=age_group_counts.index, values=age_group_counts))
        fig1.update_layout(title='Customer Distribution by Age Group')
        st.plotly_chart(fig1)
    else:
        st.write("ℹ️ No data available for Age Group distribution.")

# Column 2: Pie chart for Contract distribution
with col2:
    if not contract_counts.empty:
        fig2 = go.Figure(go.Pie(labels=contract_counts.index, values=contract_counts))
        fig2.update_layout(title='Customer Distribution by Contract Type')
        st.plotly_chart(fig2)
    else:
        st.write("ℹ️ No data available for Contract distribution.")

st.write('---')

# 📌 Question 3: Strategies to Reduce Churn
st.write('### 📌 Question 3: What Should Be the Strategy to Reduce Churn in the Future?')

with st.expander("💡 Click to View Strategy Suggestions"):
    st.markdown("## **Strategy Recommendations**")
    st.markdown("#### 📌 **Customer Segments & Solutions**")
    st.write("- Middle-Aged Adults: Loyalty rewards and personalized service.")
    st.write("- Seniors: Simple plans and technical assistance.")
    st.write("- Young Adults: Flexible plans and referral programs.")
    
    st.markdown("#### 🔥 **Key Churn Factors & Fixes**")
    st.write("- **Competitor Churn:** Loyalty programs & competitive pricing.")
    st.write("- **Service Dissatisfaction:** Improve network & personalized offers.")
    st.write("- **Customer Support Issues:** Train representatives for better experience.")

st.write('---')
