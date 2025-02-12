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

# -----------------
# 3. Sidebar Filters
# -----------------
with st.sidebar:
    st.title("🔍 Filters")
    st.write("Use the filters below to explore churn trends.")
    
    # Gender filter
    gender_filter = st.radio(
        "Select Gender", 
        options=["All", "Male", "Female"], 
        index=0
    )
    
    # Churn status filter
    churn_filter = st.radio(
        "Select Churn Status", 
        options=["All", "Yes", "No"], 
        index=0
    )

# -------------------------
# 4. Data Filtering by User
# -------------------------
df_filtered = df.copy()

# Filter by Gender
if gender_filter != "All":
    df_filtered = df_filtered[df_filtered['Gender'] == gender_filter].copy()

# Filter by Churn Status
if churn_filter == "Yes":
    # Map Yes -> 1 and No -> 0, then keep only churned
    df_filtered['Churn Label'] = df_filtered['Churn Label'].map({'Yes': 1, 'No': 0})
    df_filtered = df_filtered[df_filtered['Churn Label'] == 1]
elif churn_filter == "No":
    # Map Yes -> 0 and No -> 1, then keep only non-churned
    df_filtered['Churn Label'] = df_filtered['Churn Label'].map({'Yes': 0, 'No': 1})
    df_filtered = df_filtered[df_filtered['Churn Label'] == 1]
# If "All", do nothing.

# ---------------------------------------------
# 5. Question 1: Which Services Tend to Churn?
# ---------------------------------------------
st.write('### 📌 Question 1: Which Services Tend to Have High Churn?')

# Service-related columns (ensure these match your dataset)
service_columns = [
    'Phone Service', 'Internet Service', 'Multiple Lines',
    'Streaming TV', 'Streaming Movies', 'Streaming Music',
    'Online Security', 'Online Backup', 'Device Protection Plan',
    'Premium Tech Support', 'Unlimited Data'
]

# Calculate the churn percentage for each service
service_churn_pct = {}
for service in service_columns:
    # Customers who have this service
    service_users = df_filtered[df_filtered[service] == 'Yes']
    total_service_users = service_users.shape[0]
    
    # Among those, how many are churned if we are looking at churned data only
    # or total data? This logic depends on whether df_filtered is only churned or not. 
    # If you want the churn rate *within* df_filtered, do:
    if total_service_users > 0:
        # Because we already filtered by churn status above,
        # we can interpret "Churn Label == 1" as churned if needed:
        churn_count = service_users[service_users['Churn Label'] == 1].shape[0]
        service_churn_pct[service] = (churn_count / total_service_users) * 100
    else:
        service_churn_pct[service] = 0

# Convert dict to DataFrame
service_churn_df = pd.DataFrame(service_churn_pct, index=['Churn Percentage']).T

# Two-column layout for table and bar chart
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏆 Top 5 Services by Churn Rate")
    top_5_services = service_churn_df.sort_values(by="Churn Percentage", ascending=False).head(5)
    st.dataframe(top_5_services)

with col2:
    st.markdown("### 📊 Churn Percentage by Service")
    if not service_churn_df.empty:
        fig = px.bar(
            service_churn_df,
            x=service_churn_df.index,
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
    else:
        st.write("No data available to plot.")

st.write('---')

# -----------------------------------
# 6. Question 2: Why Do Customers Churn?
# -----------------------------------
st.write('### 📌 Question 2: What Would We Do to Reduce Churn?')

# Safeguard: If df_filtered is empty, display a message and stop
if df_filtered.empty:
    st.info("No data available for the current filters. Please adjust your filters to see results.")
    st.stop()

# Count top churn reasons
if 'Churn Reason' in df_filtered.columns:
    top_churn_reasons = df_filtered['Churn Reason'].value_counts().head(5)
else:
    top_churn_reasons = pd.Series()

# Two-column layout for reasons and map
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏆 Top 5 Churn Reasons")
    if not top_churn_reasons.empty:
        df_top_reasons = top_churn_reasons.reset_index()
        df_top_reasons.columns = ['Churn Reason', 'Count']
        st.dataframe(df_top_reasons.set_index("Churn Reason"))
    else:
        st.write("No churn reasons found.")

with col2:
    st.markdown("### 🌍 Geographical Distribution of Top 5 Churn Reasons")
    if 'Latitude' in df_filtered.columns and 'Longitude' in df_filtered.columns and not top_churn_reasons.empty:
        reason_filter_data = df_filtered[df_filtered['Churn Reason'].isin(top_churn_reasons.index)]
        if not reason_filter_data.empty:
            fig_map = px.scatter_mapbox(
                reason_filter_data,
                lat="Latitude",
                lon="Longitude",
                color="Churn Reason",
                hover_name="Customer ID",
                zoom=4
            )
            fig_map.update_layout(mapbox_style="carto-positron", height=450)
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.write("No geographical data available for the top reasons.")
    else:
        st.write("Latitude/Longitude columns not found or no data to display.")

st.write('---')

# ---------------------------------------------
# 7. Additional: Churn Categories Exploration
# ---------------------------------------------
st.write('### 📌 Churn Categories Exploration')

# Count top churn categories
if 'Churn Category' in df_filtered.columns:
    top_churn_categories = df_filtered['Churn Category'].value_counts().head(5)
else:
    top_churn_categories = pd.Series()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏆 Top 5 Churn Categories")
    if not top_churn_categories.empty:
        df_top_categories = top_churn_categories.reset_index()
        df_top_categories.columns = ['Churn Category', 'Count']
        st.dataframe(df_top_categories.set_index("Churn Category"))
    else:
        st.write("No churn categories found.")

with col2:
    st.markdown("### 🌍 Geographical Distribution of Top 5 Churn Categories")
    if 'Latitude' in df_filtered.columns and 'Longitude' in df_filtered.columns and not top_churn_categories.empty:
        category_filter_data = df_filtered[df_filtered['Churn Category'].isin(top_churn_categories.index)]
        if not category_filter_data.empty:
            fig_map_cat = px.scatter_mapbox(
                category_filter_data,
                lat="Latitude",
                lon="Longitude",
                color="Churn Category",
                hover_name="Customer ID",
                zoom=4
            )
            fig_map_cat.update_layout(mapbox_style="carto-positron", height=450)
            st.plotly_chart(fig_map_cat, use_container_width=True)
        else:
            st.write("No geographical data available for the top categories.")
    else:
        st.write("Latitude/Longitude columns not found or no data to display.")

st.write('---')

# -------------------------------------------------
# 8. Pie Charts: Customer Demographics & Contracts
# -------------------------------------------------
st.write('### 📊 Customer Demographics & Contract Type Distribution')

# Create a helper to categorize age
def get_age_category(age):
    if age < 30:
        return 'Young Adults'
    elif 30 <= age < 50:
        return 'Middle-Aged Adults'
    else:
        return 'Seniors'

if 'Age' in df_filtered.columns:
    df_filtered['AgeGroup'] = df_filtered['Age'].apply(get_age_category)
else:
    df_filtered['AgeGroup'] = 'Unknown'

age_group_counts = df_filtered['AgeGroup'].value_counts() if 'AgeGroup' in df_filtered.columns else pd.Series()
contract_counts = df_filtered['Contract'].value_counts() if 'Contract' in df_filtered.columns else pd.Series()

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Customer Distribution by Age Group")
    if not age_group_counts.empty:
        fig1 = go.Figure(go.Pie(labels=age_group_counts.index, values=age_group_counts.values))
        fig1.update_layout(title='Age Group Distribution')
        st.plotly_chart(fig1)
    else:
        st.write("ℹ️ No data available for Age Group distribution.")

with col2:
    st.markdown("#### Customer Distribution by Contract Type")
    if not contract_counts.empty:
        fig2 = go.Figure(go.Pie(labels=contract_counts.index, values=contract_counts.values))
        fig2.update_layout(title='Contract Type Distribution')
        st.plotly_chart(fig2)
    else:
        st.write("ℹ️ No data available for Contract distribution.")

st.write('---')

# ------------------------------------------------------
# 9. Question 3: Strategy to Reduce Churn in the Future
# ------------------------------------------------------
st.write('### 📌 Question 3: What Should Be the Strategy to Reduce Churn in the Future?')

with st.expander("💡 Click to View Strategy Suggestions"):
    st.markdown("## **Strategy Recommendations**")
    st.markdown("#### 📌 **Customer Segments & Solutions**")
    st.write("- **Middle-Aged Adults**: Loyalty rewards and personalized service.")
    st.write("- **Seniors**: Simple plans and technical assistance.")
    st.write("- **Young Adults**: Flexible plans and referral programs.")

    st.markdown("#### 🔥 **Key Churn Factors & Fixes**")
    st.write("- **Competitor Churn**: Loyalty programs & competitive pricing.")
    st.write("- **Service Dissatisfaction**: Improve network & personalized offers.")
    st.write("- **Customer Support Issues**: Train representatives for better customer experience.")

st.write('---')
st.write("### End of Dashboard")
