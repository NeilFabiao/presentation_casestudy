import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------
# 1. Set Page Configuration (Must Be First Streamlit Command)
# ----------------------------------------------------
st.set_page_config(
    page_title="Telco Churn Analysis - Section 1",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 2. Load and Clean the Dataset
# ----------------------------------------------------
@st.cache_data  # Use st.cache_data for caching (ensure Streamlit version supports this)
def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads the telco dataset from a CSV file and fills specified columns' NaN with 'Unknown'.
    """
    df_ = pd.read_csv(file_path)
    
    # Replace NaN with 'Unknown' in certain categorical columns
    cols_to_change = ['Churn Reason', 'Churn Category', 'Internet Type', 'Offer']
    df_[cols_to_change] = df_[cols_to_change].fillna('Unknown')

    return df_

df = load_data('telco.csv')  # Adjust path if needed

# ----------------------------------------------------
# 3. Main Title and Description
# ----------------------------------------------------
st.title("Telco Churn Analysis (Section 1 Only) 📊")
st.write("**Focus**: Which services tend to have high churn?")
st.write("---")

# ----------------------------------------------------
# 4. Sidebar Filters (Gender & Churn Status)
# ----------------------------------------------------
with st.sidebar:
    st.header("Select Filters")
    
    # Gender filter
    gender_filter = st.radio("Select Gender", options=["All", "Male", "Female"], index=0)
    
    # Churn status filter (Only 'Yes' or 'No')
    churn_filter = st.radio("Select Churn Status", options=["Yes", "No"], index=0)

# ----------------------------------------------------
# 5. Filter the Data Based on Sidebar Selections
# ----------------------------------------------------

# 5.1 Filter by Gender
df_filtered = df.copy()  # Work with a copy to avoid modifying the original dataset

if gender_filter != "All":
    df_filtered = df_filtered[df_filtered["Gender"] == gender_filter].copy()

# 5.2 Filter by Churn Status
df_filtered = df_filtered[df_filtered["Churn Label"] == churn_filter].copy()

# ----------------------------------------------------
# 6. Section 1: Which Services Tend to Have High Churn?
# ----------------------------------------------------
st.subheader("Question 1: Which Services Tend to Have High Churn?")

# List of service-related columns
service_columns = [
    "Phone Service", "Internet Service", "Multiple Lines",
    "Streaming TV", "Streaming Movies", "Streaming Music",
    "Online Security", "Online Backup", "Device Protection Plan",
    "Premium Tech Support", "Unlimited Data"
]

# Dictionary to store calculated churn percentages
service_churn_dict = {}

# Calculate churn % for each service among the filtered data
for service in service_columns:
    # Subset of customers who have the service = 'Yes'
    service_users = df_filtered[df_filtered[service] == 'Yes']
    
    # Among those service users, count how many are churned
    churn_count = service_users.shape[0]  # Since df_filtered is already filtered by churn = "Yes"
    total_users = df[df[service] == 'Yes'].shape[0]  # Get the total users for the service
    
    # Compute percentage (avoid division by zero)
    churn_percentage = (churn_count / total_users * 100) if total_users > 0 else 0
    service_churn_dict[service] = churn_percentage

# Convert dictionary to DataFrame for easy display
service_churn_df = pd.DataFrame(service_churn_dict, index=["Churn Percentage"]).T  # Transpose for better layout

# ----------------------------------------------------
# 7. Display the Results (Top 5 Table and Bar Chart)
# ----------------------------------------------------
col1, col2 = st.columns(2)

# 7.1 Table of Top 5 Services by Churn Rate
with col1:
    st.markdown("### Top 5 Services by Churn Rate")
    top_5_services = service_churn_df.sort_values(by="Churn Percentage", ascending=False).head(5)
    st.dataframe(top_5_services)

# 7.2 Bar Chart for All Services
with col2:
    st.markdown("### Churn Percentage by Service")
    
    if not service_churn_df.empty:
        # Get min and max churn percentage for better y-axis scaling
        min_churn_percentage = service_churn_df["Churn Percentage"].min()
        max_churn_percentage = service_churn_df["Churn Percentage"].max()

        fig = px.bar(
            service_churn_df,
            x=service_churn_df.index,
            y="Churn Percentage",
            color="Churn Percentage",
            color_continuous_scale="viridis",
            labels={"x": "Service", "Churn Percentage": "Churn %"},
        )
        fig.update_layout(
            xaxis_title="Service",
            yaxis_title="Churn Percentage (%)",
            xaxis_tickangle=-45,
            yaxis_range=[min_churn_percentage - 5, max_churn_percentage + 5],  # Dynamic range
            margin=dict(l=10, r=10, t=40, b=50),
            coloraxis_showscale=False  # Hide the color bar
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available to plot. Try changing your filters.")

# Final divider
st.write("---")

# ----------------------------------------------------
# 8. Section 2: What would we do to reduce churn?
# ----------------------------------------------------
st.subheader("Question 2: What would we do to reduce churn?")

# --- CHURN REASON ANALYSIS ---
# Filter churned customers
churned_data = df_filtered[df_filtered['Churn Label'] == "Yes"].copy()

# Remove 'Unknown' churn reasons for better insights
churned_data_filtered = churned_data[churned_data['Churn Reason'] != 'Unknown'].copy()

# Identify the top 5 churn reasons (excluding 'Unknown')
top_churn_reasons = churned_data_filtered['Churn Reason'].value_counts().head(5)

# Create two columns: One for top churn reasons, one for geographical mapping
col1, col2 = st.columns(2)

# Column 1: Display top churn reasons
with col1:
    st.markdown("### 🏆 Top 5 Churn Reasons")
    
    # Convert Series to DataFrame and rename columns
    df_top_reasons = top_churn_reasons.reset_index()
    df_top_reasons.columns = ['Churn Reason', 'Count']
    
    # Display clean DataFrame
    st.dataframe(df_top_reasons, hide_index=True)

# Column 2: Display geographical distribution of churn reasons
with col2:
    st.markdown("### 🌍 Geographical Distribution of Top 5 Churn Reasons")
    
    if 'Latitude' in churned_data.columns and 'Longitude' in churned_data.columns:
        # Filter churned data for top 5 churn reasons
        top_reason_data = churned_data[churned_data['Churn Reason'].isin(top_churn_reasons.index)]

        # Compute dynamic map center
        lat_center = top_reason_data['Latitude'].mean()
        lon_center = top_reason_data['Longitude'].mean()

        # Create an interactive map
        fig_map = px.scatter_mapbox(
            top_reason_data,
            lat="Latitude",
            lon="Longitude",
            color="Churn Reason",
            hover_name="Customer ID",
            hover_data=["Age", "Contract"],
            color_discrete_sequence=px.colors.qualitative.Pastel,
            zoom=3.5
        )

        fig_map.update_layout(mapbox_style="carto-positron", mapbox_center={"lat": lat_center, "lon": lon_center})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.write("ℹ️ No geographical data available for mapping.")

st.write("---")

# --- CHURN CATEGORY ANALYSIS ---
# Identify the top 5 churn categories
top_churn_categories = churned_data_filtered['Churn Category'].value_counts().head(5)

# Create two columns: One for top churn categories, one for geographical mapping
col1, col2 = st.columns(2)

# Column 1: Display top churn categories
with col1:
    st.markdown("### 🏆 Top 5 Churn Categories")
    
    # Convert Series to DataFrame and rename columns
    df_top_categories = top_churn_categories.reset_index()
    df_top_categories.columns = ['Churn Category', 'Count']
    
    # Display clean DataFrame
    st.dataframe(df_top_categories, hide_index=True)

# Column 2: Display geographical distribution of churn categories
with col2:
    st.markdown("### 🌍 Geographical Distribution of Top 5 Churn Categories")
    
    if 'Latitude' in churned_data.columns and 'Longitude' in churned_data.columns:
        # Filter churned data for top 5 churn categories
        top_category_data = churned_data[churned_data['Churn Category'].isin(top_churn_categories.index)]

        # Compute dynamic map center
        lat_center = top_category_data['Latitude'].mean()
        lon_center = top_category_data['Longitude'].mean()

        # Create an interactive map
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

