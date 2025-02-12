import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans

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
    st.markdown("### Churn Percentage Comparison by Service")

    # Get the maximum and minimum churn percentages for dynamic y-axis range
    min_churn_percentage = service_churn_percentage_df["Churn Percentage"].min()
    max_churn_percentage = service_churn_percentage_df["Churn Percentage"].max()

    # Create the bar chart using Plotly
    fig = px.bar(
        service_churn_percentage_df,
        x=service_churn_percentage_df.index,
        y="Churn Percentage",
        color="Churn Percentage",  # Color bars by churn percentage
        color_continuous_scale="viridis", # Use a nice color scale
        title=None  # Hide the title directly here
    )

    fig.update_layout(
        xaxis_title="Service",
        yaxis_title="Churn Percentage (%)",
        xaxis_tickangle=-45,  # Rotate x-axis labels
        yaxis_range=[min_churn_percentage - 5, max_churn_percentage + 5],  # Dynamic range based on data
        margin=dict(l=10, r=10, t=40, b=50),  # Set margins to ensure no clipping
        xaxis=dict(showgrid=True),  # Show gridlines on x-axis for better readability
        yaxis=dict(showgrid=True),  # Show gridlines on y-axis
        coloraxis_showscale=False  # Hide the color bar (right bar)
    )
    
    st.plotly_chart(fig)

st.write('---')

# Part 2: What would we do to reduce churn?
st.write('### Question 2: What would we do to reduce churn?')

# --- CHURN Reason SECTION ---

churned_data = df_clean_[df_clean_['Churn Label'] == 1]

# Remove 'Unknown' churn reasons from analysis to avoid skewed data
churned_data_filtered = churned_data[churned_data['Churn Reason'] != 'Unknown']

# Part 1: Identify the top 5 churn reasons (excluding 'Unknown')
top_churn_reasons = churned_data_filtered['Churn Reason'].value_counts().head(5)

# Create two columns for displaying top churn reasons and their geographical distribution
col1, col2 = st.columns(2)

# Column 1: Display the top 5 churn reasons (Formatted DataFrame)
with col1:
    st.markdown("### 🏆 Top 5 Churn Reasons")
    
    # Convert Series to DataFrame and properly rename columns
    df_top_reasons = top_churn_reasons.reset_index()
    df_top_reasons.columns = ['Churn Reason', 'Count']  # Correct column renaming
    
    # Display clean DataFrame without index column
    st.dataframe(df_top_reasons, hide_index=True)

# Column 2: Display the geographical distribution of churned customers for the top 5 churn reasons
with col2:
    st.markdown("### 🌍 Geographical Distribution of Top 5 Churn Reasons")
    
    if 'Latitude' in churned_data.columns and 'Longitude' in churned_data.columns:
        # Filter churned data for only the top 5 churn reasons
        top_reason_data = churned_data[churned_data['Churn Reason'].isin(top_churn_reasons.index)]

        # Calculate center of the map dynamically
        lat_center = top_reason_data['Latitude'].mean()
        lon_center = top_reason_data['Longitude'].mean()

        # Create the interactive map
        fig_map = px.scatter_mapbox(
            top_reason_data,
            lat="Latitude",
            lon="Longitude",
            color="Churn Reason",
            hover_name="Customer ID",
            hover_data=["Age", "Contract"],
            color_discrete_sequence=px.colors.qualitative.Pastel,
            zoom=3.5
            #title="Geographical Distribution of Churned Customers by Top Reasons"
        )

        fig_map.update_layout(mapbox_style="carto-positron", mapbox_center={"lat": lat_center, "lon": lon_center})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.write("ℹ️ No geographical data available for mapping.")

# --- ADD CHURN CATEGORY SECTION ---

st.write('---')

# Filter the churned data based on the churn_filter
churned_data = df_clean_[df_clean_['Churn Label'] == 1]

# Part 2: Identify the top 5 churn categories
top_churn_categories = churned_data_filtered['Churn Category'].value_counts().head(5)

# Create two columns for displaying churn categories and their geographical distribution
col1, col2 = st.columns(2)

# Column 1: Display the top 5 churn categories (Formatted DataFrame)
with col1:
    st.markdown("### 🏆 Top 5 Churn Categories")
    
    # Convert Series to DataFrame and properly rename columns
    df_top_categories = top_churn_categories.reset_index()
    df_top_categories.columns = ['Churn Category', 'Count']  # Correct column renaming
    
    # Display clean DataFrame without index column
    st.dataframe(df_top_categories, hide_index=True)

# Column 2: Display the geographical distribution of churned customers for the top 5 churn categories
with col2:
    st.markdown("### 🌍 Geographical Distribution of Top 5 Churn Categories")
    
    if 'Latitude' in churned_data.columns and 'Longitude' in churned_data.columns:
        # Filter churned data for only the top 5 churn categories
        top_category_data = churned_data[churned_data['Churn Category'].isin(top_churn_categories.index)]

        # Calculate center of the map dynamically
        lat_center = top_category_data['Latitude'].mean()
        lon_center = top_category_data['Longitude'].mean()

        # Create the interactive map
        fig_map_category = px.scatter_mapbox(
            top_category_data,
            lat="Latitude",
            lon="Longitude",
            color="Churn Category",
            hover_name="Customer ID",
            hover_data=["Age", "Contract"],
            color_discrete_sequence=px.colors.qualitative.Vivid,
            zoom=3.5
        )

        fig_map_category.update_layout(mapbox_style="carto-positron", mapbox_center={"lat": lat_center, "lon": lon_center})
        st.plotly_chart(fig_map_category, use_container_width=True)
    else:
        st.write("ℹ️ No geographical data available for mapping.")

st.write('---')

# Filter the churned data based on the churn_filter
churned_data = df_clean_[df_clean_['Churn Label'] == 1]

# Create age categories for churned customers
def age_category(age):
    if age < 30:
        return 'Young Adults'
    elif 30 <= age < 50:
        return 'Middle-Aged Adults'
    else:
        return 'Seniors'

churned_data['AgeGroup'] = churned_data['Age'].apply(age_category)

# Pie chart for Age Group distribution of churned customers
age_group_counts = churned_data['AgeGroup'].value_counts()

# Pie chart for Contract distribution of churned customers
contract_counts = churned_data['Contract'].value_counts()

# Create a Streamlit layout with two columns
col1, col2 = st.columns(2)

# Pie chart for Age Group distribution in the first column
with col1:
    fig1 = go.Figure(go.Pie(labels=age_group_counts.index, values=age_group_counts, 
                            marker=dict(colors=['#ff9999','#66b3ff','#99ff99'])))
    fig1.update_layout(title='Churned Customers by Age Group')
    st.plotly_chart(fig1)

# Pie chart for Contract distribution in the second column
with col2:
    fig2 = go.Figure(go.Pie(labels=contract_counts.index, values=contract_counts, 
                            marker=dict(colors=['#ffcc99','#ff6666','#66b3ff'])))
    fig2.update_layout(title='Churned Customers by Contract Type')
    st.plotly_chart(fig2)
    
st.write('---')

# Part 3: What should be the strategy to employ to reduce churn in the future?
st.write('### 📌 Question 3: What Should Be the Strategy to Reduce Churn in the Future?')

# Create an expandable section to improve readability
with st.expander("💡 Click to View Detailed Strategy Suggestions"):
    st.markdown("## **Suggestion**")

    # Part 1: Customer Segments & Targeted Strategies
    st.markdown("### **Customer Segments & Targeted Strategies**")
    
    st.markdown("#### 📌 **Middle-Aged Adults (Two-Year Contract, Female/Male)**")
    st.write("""
    - Offering loyalty rewards or personalized customer service makes sense for this group, as they tend to have higher tenures.
    - Special bundles or family plans align well with Middle-Aged Adults, who may appreciate incentives that appeal to their lifestyle.
    """)

    st.markdown("#### 📌 **Seniors (One-Year Contract, Female)**")
    st.write("""
    - Focus on simplicity and tech assistance, as this group prefers easy-to-understand services and may need extra support with technology.
    - Straightforward billing and clear communication can improve retention among senior customers.
    """)

    st.markdown("#### 📌 **Young Adults (One-Year Contract, Female/Male)**")
    st.write("""
    - Flexible plans and referral incentives align well with Young Adults, who prefer adaptable, low-commitment contracts.
    - Using gaming or gadget-related incentives and social media engagement can appeal to their interests.
    """)

    # Part 2: Addressing Key Churn Factors
    st.markdown("### **Key Churn Factors & Strategies to Address Them**")

    st.markdown("#### 🔥 **Competitor-Driven Churn**")
    st.write("""
    - Continuously monitor and analyze competitors’ pricing, services, and customer feedback.
    - Implement a loyalty rewards program to retain customers and offer exclusive benefits.
    """)

    st.markdown("#### 📉 **Dissatisfaction-Driven Churn**")
    st.write("""
    - Improve service quality, network coverage, and call/data reliability.
    - Conduct customer satisfaction surveys to pinpoint and address problem areas.
    - Offer personalized deals and retention incentives to make customers feel valued.
    """)

    st.markdown("#### 🤝 **Customer Service-Related Churn (Attitude)**")
    st.write("""
    - Train customer service teams to handle complaints with empathy and professionalism.
    - Improve response times and customer support channels to enhance customer satisfaction.
    """)

st.write('---')



