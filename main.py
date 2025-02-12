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
@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads the telco dataset from a CSV file and fills specified columns' NaN with 'Unknown'.
    """
    df_ = pd.read_csv(file_path)
    
    # Replace NaN with 'Unknown' in certain categorical columns
    cols_to_change = ['Churn Reason', 'Churn Category', 'Internet Type', 'Offer']
    for col in cols_to_change:
        if col in df_.columns:
            df_[col] = df_[col].fillna('Unknown')
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
    gender_filter = st.radio(
        "Select Gender",
        options=["All", "Male", "Female"],
        index=0
    )
    
    # Churn status filter (now includes "All")
    churn_filter = st.radio(
        "Select Churn Status",
        options=["All", "Yes", "No"],  # Provide the "All" option
        index=0
    )

# ----------------------------------------------------
# 5. Filter the Data Based on Sidebar Selections
# ----------------------------------------------------
df_filtered = df.copy()

# 5.1 Filter by Gender
if gender_filter != "All":
    df_filtered = df_filtered[df_filtered["Gender"] == gender_filter]

# 5.2 Filter by Churn Status
if churn_filter != "All":
    # Keep only rows whose "Churn Label" matches the chosen filter
    df_filtered = df_filtered[df_filtered["Churn Label"] == churn_filter]

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
    # Subset: rows that have this service == 'Yes'
    service_users = df_filtered[df_filtered[service] == 'Yes']
    
    # Among those service users, count how many are churned ("Churn Label" == "Yes")
    churn_count = service_users[service_users['Churn Label'] == "Yes"].shape[0]
    total_users = service_users.shape[0]
    
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
        fig = px.bar(
            service_churn_df,
            x=service_churn_df.index,
            y="Churn Percentage",
            color="Churn Percentage",
            color_continuous_scale="viridis",
            labels={"x": "Service", "Churn Percentage": "Churn %"},
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            margin=dict(l=10, r=10, t=40, b=50),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available to plot. Try changing your filters.")

# Final divider
st.write("---")

# End of Section 1 Only
st.write("End of Section 1. Additional sections will be added later.")
