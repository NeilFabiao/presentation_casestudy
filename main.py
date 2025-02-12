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
# Section 2: "What would we do to reduce churn?"
# ----------------------------------------------------


st.subheader("Question 2: What would we do to reduce churn?")

# Check if there are any churned customers
if df_filtered.empty:
    st.warning("No churned customers found based on the selected filters. Try adjusting the filters.")
else:
    # --- CHURN REASON ANALYSIS ---
    churned_data_filtered = df_filtered[df_filtered['Churn Reason'] != 'Unknown'].copy()
    top_churn_reasons = churned_data_filtered['Churn Reason'].value_counts().head(5)

    col3, col4 = st.columns(2)  # Unique column names for this section

    with col3:
        st.markdown("### 🏆 Top 5 Churn Reasons")
        df_top_reasons = top_churn_reasons.reset_index()
        df_top_reasons.columns = ['Churn Reason', 'Count']
        st.dataframe(df_top_reasons, hide_index=True)

    with col4:
        st.markdown("### 🌍 Geographical Distribution of Top 5 Churn Reasons")
        if 'Latitude' in df_filtered.columns and 'Longitude' in df_filtered.columns:
            top_reason_data = df_filtered[df_filtered['Churn Reason'].isin(top_churn_reasons.index)]
            if not top_reason_data.empty:
                lat_center = top_reason_data['Latitude'].mean()
                lon_center = top_reason_data['Longitude'].mean()

                fig_map = px.scatter_mapbox(
                    top_reason_data, lat="Latitude", lon="Longitude", color="Churn Reason",
                    hover_name="Customer ID", hover_data=["Age", "Contract"],
                    color_discrete_sequence=px.colors.qualitative.Pastel, zoom=3.5
                )
                fig_map.update_layout(mapbox_style="carto-positron", mapbox_center={"lat": lat_center, "lon": lon_center})
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.info("No geographical data available for this selection.")
        else:
            st.info("No geographical data available for mapping.")

    st.write("---")

    # --- CHURN CATEGORY ANALYSIS ---
    top_churn_categories = churned_data_filtered['Churn Category'].value_counts().head(5)

    col5, col6 = st.columns(2)  # Unique column names for this section

    with col5:
        st.markdown("### 🏆 Top 5 Churn Categories")
        df_top_categories = top_churn_categories.reset_index()
        df_top_categories.columns = ['Churn Category', 'Count']
        st.dataframe(df_top_categories, hide_index=True)

    with col6:
        st.markdown("### 🌍 Geographical Distribution of Top 5 Churn Categories")
        if 'Latitude' in df_filtered.columns and 'Longitude' in df_filtered.columns:
            top_category_data = df_filtered[df_filtered['Churn Category'].isin(top_churn_categories.index)]
            if not top_category_data.empty:
                lat_center = top_category_data['Latitude'].mean()
                lon_center = top_category_data['Longitude'].mean()

                fig_map_category = px.scatter_mapbox(
                    top_category_data, lat="Latitude", lon="Longitude", color="Churn Category",
                    hover_name="Customer ID", hover_data=["Age", "Contract"],
                    color_discrete_sequence=px.colors.qualitative.Vivid, zoom=3.5
                )
                fig_map_category.update_layout(mapbox_style="carto-positron", mapbox_center={"lat": lat_center, "lon": lon_center})
                st.plotly_chart(fig_map_category, use_container_width=True)
            else:
                st.info("No geographical data available for this selection.")
        else:
            st.info("No geographical data available for mapping.")


# ----------------------------------------------------
# Section 3: Understanding Churned Customers
# ----------------------------------------------------
st.subheader("Question 3: What should be the strategy to reduce churn?")

if df_filtered.empty:
    st.warning("No churned customers found based on the selected filters. Try adjusting the filters.")
else:
    # --- Churned Customers by Age Group ---
    def age_category(age):
        if age < 30:
            return 'Young Adults'
        elif 30 <= age < 50:
            return 'Middle-Aged Adults'
        else:
            return 'Seniors'

    df_filtered['Age Group'] = df_filtered['Age'].apply(age_category)

    # Pie chart for Age Group distribution
    age_group_counts = df_filtered['Age Group'].value_counts()

    # Pie chart for Contract distribution
    contract_counts = df_filtered['Contract'].value_counts()

    # Create a Streamlit layout with two columns
    col7, col8 = st.columns(2)

    # Pie chart for Age Group distribution
    with col7:
        fig1 = go.Figure(go.Pie(
            labels=age_group_counts.index, 
            values=age_group_counts, 
            marker=dict(colors=['#ff9999','#66b3ff','#99ff99'])
        ))
        fig1.update_layout(title="📊 Churned Customers by Age Group")
        st.plotly_chart(fig1)

    # Pie chart for Contract distribution
    with col8:
        fig2 = go.Figure(go.Pie(
            labels=contract_counts.index, 
            values=contract_counts, 
            marker=dict(colors=['#ffcc99','#ff6666','#66b3ff'])
        ))
        fig2.update_layout(title="📜 Churned Customers by Contract Type")
        st.plotly_chart(fig2)

    st.write('---')

    # --- Strategic Recommendations ---
    st.write('### 📌 What Should Be the Strategy to Reduce Churn?')

    # Expandable section for detailed insights
    with st.expander("💡 Click to View Detailed Strategy Suggestions"):
        st.markdown("## **Recommendation Overview**")

        # Customer Segments
        st.markdown("### **Customer Segments & Targeted Strategies**")

        st.markdown("#### 📌 **Middle-Aged Adults (Two-Year Contract, Male/Female)**")
        st.write("""
        - Offering loyalty rewards or personalized customer service makes sense for this group, as they tend to have higher tenures.
        - Special bundles or family plans align well with Middle-Aged Adults, who may appreciate incentives that appeal to their lifestyle.
        """)

        st.markdown("#### 📌 **Seniors (One-Year Contract, Female)**")
        st.write("""
        - Focus on simplicity and tech assistance, as this group prefers easy-to-understand services and may need extra support with technology.
        - Straightforward billing and clear communication can improve retention among senior customers.
        """)

        st.markdown("#### 📌 **Young Adults (One-Year Contract, Male/Female)**")
        st.write("""
        - Flexible plans and referral incentives align well with Young Adults, who prefer adaptable, low-commitment contracts.
        - Using gaming or gadget-related incentives and social media engagement can appeal to their interests.
        """)

        # Key Churn Factors
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

        st.markdown("#### 🤝 **Customer Service-Related Churn**")
        st.write("""
        - Train customer service teams to handle complaints with empathy and professionalism.
        - Improve response times and customer support channels to enhance customer satisfaction.
        """)

st.write('---')
