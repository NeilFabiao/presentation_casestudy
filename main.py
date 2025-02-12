import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

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

# Column 1: Display raw churn counts for the top 5 services
with col1:
    st.markdown("### Top 5 Services")
    top_5_services = service_churn_percentage_df.sort_values(by="Churn Percentage", ascending=False).head(5)
    st.dataframe(top_5_services)  # Display the top 5 services table

# Column 2: Display churn percentage graph (using Plotly)
with col2:
    st.markdown("### Churn Percentage Comparison by Service (Plotly)")

    # Get the maximum and minimum churn percentages for dynamic y-axis range
    min_churn_percentage = service_churn_percentage_df["Churn Percentage"].min()
    max_churn_percentage = service_churn_percentage_df["Churn Percentage"].max()

    # Create the bar chart using Plotly
    fig = px.bar(
        service_churn_percentage_df,
        x=service_churn_percentage_df.index,
        y="Churn Percentage",
        title="Churn Percentage Comparison by Service",
        color="Churn Percentage",  # Color bars by churn percentage
        color_continuous_scale="viridis" # Use a nice color scale
    )

    fig.update_layout(
        xaxis_title="Service",
        yaxis_title="Churn Percentage (%)",
        xaxis_tickangle=-45,  # Rotate x-axis labels
        yaxis_range=[min_churn_percentage - 5, max_churn_percentage + 5],  # Dynamic range based on data
        margin=dict(l=10, r=10, t=40, b=50),  # Set margins to ensure no clipping
        title_x=0.5,  # Center the title
        title_font=dict(size=16),  # Title font size
        xaxis=dict(showgrid=True),  # Show gridlines on x-axis for better readability
        yaxis=dict(showgrid=True)   # Show gridlines on y-axis
    )
    
    st.plotly_chart(fig)

st.write('---')

# Part 2: What would we do to reduce churn?
st.write('### Question 2: What would we do to reduce churn?')

# Step 1: Filter churned data and create age categories
churned_data = df_clean_[df_clean_['Churn Label'] == 1]  # Filter churned customers

# Create age categories
def age_category(age):
    if age < 30:
        return 'Young Adults'
    elif 30 <= age < 50:
        return 'Middle-Aged Adults'
    else:
        return 'Seniors'

churned_data['AgeGroup'] = churned_data['Age'].apply(age_category)

# Group churned data by AgeGroup, Contract, Gender, and Customer Status
grouped_churn_data = churned_data.groupby(['AgeGroup', 'Contract', 'Gender', 'Customer Status']).agg(
    AvgTenure=('Tenure in Months', 'mean'),
    AvgMonthlyCharge=('Monthly Charge', 'mean')
).reset_index()

# Round the results to 2 decimal places
grouped_churn_data['AvgTenure'] = grouped_churn_data['AvgTenure'].round(2)
grouped_churn_data['AvgMonthlyCharge'] = grouped_churn_data['AvgMonthlyCharge'].round(2)

# Part 3: Show pie charts for Age Group, Contract, and Gender
st.write('### Churn Distribution by Age Group, Contract Type, and Gender')

# Pie chart for Age Group distribution of churned customers
age_group_counts = churned_data['AgeGroup'].value_counts()
fig_age = px.pie(values=age_group_counts, names=age_group_counts.index, title="Churned Customers by Age Group", color_discrete_sequence=px.colors.pastel)
st.plotly_chart(fig_age)

# Pie chart for Contract distribution of churned customers
contract_counts = churned_data['Contract'].value_counts()
fig_contract = px.pie(values=contract_counts, names=contract_counts.index, title="Churned Customers by Contract Type", color_discrete_sequence=px.colors.pastel)
st.plotly_chart(fig_contract)

# Pie chart for Gender distribution of churned customers
gender_counts = churned_data['Gender'].value_counts()
fig_gender = px.pie(values=gender_counts, names=gender_counts.index, title="Churned Customers by Gender", color_discrete_sequence=px.colors.pastel)
st.plotly_chart(fig_gender)

# Here you can insert your suggestions or strategies, e.g.:
st.markdown("""
**Middle-Aged Adults (Two-Year Contract, Female/Male):**
- Offering loyalty rewards or personalized customer service for long-term contract holders.
- Special bundles or family plans that align well with their lifestyle.
  
**Seniors (One-Year Contract, Female):**
- Focus on simplicity and tech assistance.
- Easy-to-understand services and straightforward support.

**Young Adults (One-Year Contract, Female/Male):**
- Flexible plans with referral incentives for social networks.
- Use of gaming or gadget-related incentives.""")

st.write('---')


# Part 3: What should be the strategy to employ to reduce churn in the future?
st.write('### Question 3: What should be the strategy to employ to reduce churn in the future')

# Provide a strategic suggestion here
st.markdown("""
**Competitor Analysis:**
- Continuously monitor competitors’ offerings and pricing structures.
- Use customer loyalty rewards programs to create a competitive edge.

**Dissatisfaction:**
- Survey customers regularly to pinpoint areas for improvement.
- Personalized deals and exclusive offers for dissatisfied customers.

**Attitude:**
- Train customer service representatives to address issues empathetically and improve service quality.
""")




