import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

    # ----------------------------------------------------
    # Insights from the Geographical Churn Distribution Map
    # ----------------------------------------------------
    with st.expander("🌍 Click to View Insights from the Geographical Churn Distribution Map"):
        
        # High Churn Clusters in Urban Areas
        st.subheader("📍 High Churn Clusters in Urban Areas")
        st.write("**Observation:** The majority of churn points are concentrated in highly populated cities, such as Los Angeles, San Francisco, and San Diego.")
        st.write("**Strategy:** Implement location-based retention offers, competitive pricing, and better network optimization in these high-churn cities.")
    
        # Competitor Influence Across Regions
        st.subheader("🏆 Competitor Influence is a Key Factor Across Regions")
        st.write("**Observation:** The most frequent churn category is 'Competitor', as seen by the high density of orange dots across regions.")
        st.write("**Strategy:** Strengthen loyalty programs, price-matching offers, and exclusive deals to retain these customers.")
    
        # Dissatisfaction & Customer Service Issues
        st.subheader("📞 Dissatisfaction and Customer Service Issues Vary by Location")
        st.write("**Observation:** Purple (Attitude) and Blue (Dissatisfaction) dots are spread throughout the map, indicating customer service quality issues in multiple locations.")
        st.write("**Strategy:** Focus on service training improvements, better support response times, and localized service enhancements in these areas.")
    
        # Pricing Concerns
        st.subheader("💰 Pricing Concerns Are More Evenly Distributed")
        st.write("**Observation:** Green dots (Price) are widely spread across the map, meaning price sensitivity exists across multiple regions, not just in major cities.")
        st.write("**Strategy:** Introduce tiered pricing plans, flexible contracts, and budget-friendly options for different income segments.")
    
    # ----------------------------------------------------
    # Click-to-View Churn Insights Section
    # ----------------------------------------------------
    with st.expander("💡 Click to View Gender-Based Churn Insights"):
    
        # Female Churn Summary
        st.subheader("📌 Female Churn")
        st.write("**Takeaway:** Women primarily leave due to competitor pricing and device quality, with customer service also playing a role.")
        st.write("**Strategy:** Improve pricing competitiveness, device upgrade programs, and customer service interactions.")
    
        # Male Churn Summary
        st.subheader("📌 Male Churn")
        st.write("**Takeaway:** Device quality is the biggest concern for male customers, followed by pricing and service experience.")
        st.write("**Strategy:** Introduce early device access, trade-in programs, price-matching, and tech-oriented customer support.")
    
        # Overall Churn Summary
        st.subheader("📌 Overall Churn")
        st.write("**Takeaway:** Device quality and pricing are the biggest churn drivers, with customer service dissatisfaction as a secondary factor.")
        st.write("**Strategy:** Implement device-focused retention bundles, better pricing models, and enhanced customer service.")
    
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
    # Click-to-View Churn Category Insights Section
    # ----------------------------------------------------
    with st.expander("💡 Click to View Churn Category Insights"):
        
        # Overall Churn Summary
        st.subheader("📌 Overall Churn Trends")
        st.write("**Takeaway:** Competitor influence is the primary churn category, followed by customer service attitude, dissatisfaction, and pricing.")
        st.write("**Strategy:** Strengthen **competitive pricing, improve service quality, and enhance customer experience** to reduce churn.")
    
        # Male Churn Summary
        st.subheader("📌 Male Churn Trends")
        st.write("**Takeaway:** Male customers churn mainly due to **competitor influence and dissatisfaction**, with **customer service attitude** also playing a key role.")
        st.write("**Strategy:** Offer **early access to better devices, loyalty rewards, and proactive service support** for better retention.")
    
        # Female Churn Summary
        st.subheader("📌 Female Churn Trends")
        st.write("**Takeaway:** Female customers are more likely to churn due to **competitor influence and pricing**, with **attitude of support representatives** being a major concern.")
        st.write("**Strategy:** **Improve personalized customer interactions, introduce pricing incentives, and offer better support training** to retain female customers.")
    

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

        # Churn by Age Group
        st.subheader("📌 Churn Insights by Age Group")
        st.write("**Takeaway:** Seniors have the highest churn rate, followed by middle-aged adults and young adults.")
        st.write("**Strategy:**")
        st.markdown("- **Seniors:** Focus on **clear communication, easy billing, and tech assistance** to reduce churn.")
        st.markdown("- **Middle-Aged Adults:** Offer **family plans, personalized rewards, and long-term incentives**.")
        st.markdown("- **Young Adults:** Use **flexible contracts, referral programs, and digital engagement** strategies.")
    
        # Churn by Contract Type
        st.subheader("📌 Churn Insights by Contract Type")
        st.write("**Takeaway:** The majority of churned customers are on **month-to-month contracts**, with minimal churn from long-term contracts.")
        st.write("**Strategy:**")
        st.markdown("- Introduce **discounted long-term plans and upgrade incentives** to retain customers.")
        st.markdown("- Provide **loyalty benefits for month-to-month users** to encourage retention.")

        # Key Churn Factors
        st.markdown("### **Key Churn Factors & Strategies to Address Them**")

        st.markdown("#### ✔️ **Competitor-Driven Churn**")
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
