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
@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads the telco dataset from a CSV file and fills specified columns' NaN with 'Unknown'.
    """
    df_ = pd.read_csv(file_path)
    cols_to_change = ['Churn Reason', 'Churn Category', 'Internet Type', 'Offer']
    df_[cols_to_change] = df_[cols_to_change].fillna('Unknown')
    return df_

# ----------------------------------------------------
# Tenure Bin Definitions
# ----------------------------------------------------
TENURE_BINS = [0, 6, 12, 24, 36, 48, 60, float('inf')]
TENURE_LABELS = [
    "0-6 months",
    "7-12 months",
    "13-24 months",
    "25-36 months",
    "37-48 months",
    "49-60 months",
    "61+ months"
]

def preprocess_data(df):
    df["Tenure Group"] = pd.cut(
        df["Tenure in Months"],
        bins=TENURE_BINS,
        labels=TENURE_LABELS,
        right=True
    )
    return df

# ----------------------------------------------------
# CLTV Trend Plot (Line Color Changed to Gold)
# ----------------------------------------------------
def plot_cltv_trend(df):
    # Ensure Tenure Group is in the correct (ordered) categorical format
    df["Tenure Group"] = pd.Categorical(
        df["Tenure Group"],
        categories=TENURE_LABELS,
        ordered=True
    )
    cltv_by_tenure = df.groupby("Tenure Group")["CLTV"].mean().reset_index()

    fig = px.line(
        cltv_by_tenure, 
        x="Tenure Group", 
        y="CLTV", 
        markers=True, 
        title="📈 CLTV Trend by Tenure Group",
        labels={"CLTV": "Average CLTV", "Tenure Group": "Tenure Group"}
    )
    # --- Set the line to gold, make it 3px wide ---
    fig.update_traces(line=dict(color="gold", width=3))
    fig.update_xaxes(tickangle=-45)
    
    st.plotly_chart(fig, use_container_width=True)


# Load Data
df = load_data('telco.csv')

# ----------------------------------------------------
# 3. Main Title and Description
# ----------------------------------------------------
st.title("Telco Churn Analysis 📊")
st.write("**Focus**: Which services tend to have high churn?")
st.write("---")

# ----------------------------------------------------
# 4. Sidebar Filters (Gender & Churn Status)
# ----------------------------------------------------
with st.sidebar:
    st.header("Select Filters")
    gender_filter = st.radio("Select Gender", options=["All", "Male", "Female"], index=0)
    churn_filter = st.radio("Select Churn Status", options=["Yes", "No"], index=0)

# ----------------------------------------------------
# 5. Filter the Data Based on Sidebar Selections
# ----------------------------------------------------
df_filtered = df.copy()

if gender_filter != "All":
    df_filtered = df_filtered[df_filtered["Gender"] == gender_filter].copy()

df_filtered = df_filtered[df_filtered["Churn Label"] == churn_filter].copy()

# ----------------------------------------------------
# 6. Section 1: Which Services Tend to Have High Churn?
# ----------------------------------------------------
st.subheader("Question 1: Which Services Tend to Have High Churn?")

service_columns = [
    "Phone Service", "Internet Service", "Multiple Lines",
    "Streaming TV", "Streaming Movies", "Streaming Music",
    "Online Security", "Online Backup", "Device Protection Plan",
    "Premium Tech Support", "Unlimited Data"
]

service_churn_dict = {}
for service in service_columns:
    service_users = df_filtered[df_filtered[service] == 'Yes']
    churn_count = service_users.shape[0]  # Already filtered to churn = Yes
    total_users = df[df[service] == 'Yes'].shape[0]
    churn_percentage = (churn_count / total_users * 100) if total_users > 0 else 0
    service_churn_dict[service] = churn_percentage

service_churn_df = pd.DataFrame(service_churn_dict, index=["Churn Percentage"]).T

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Top 5 Services by Churn Rate")
    top_5_services = service_churn_df.sort_values(by="Churn Percentage", ascending=False).head(5)
    st.dataframe(top_5_services)

with col2:
    st.markdown("### Churn Percentage by Service")
    
    if not service_churn_df.empty:
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
            yaxis_range=[min_churn_percentage - 5, max_churn_percentage + 5],
            margin=dict(l=10, r=10, t=40, b=50),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available to plot. Try changing your filters.")

st.write("---")

# ----------------------------------------------------
# Section 2: "What would we do to reduce churn?"
# ----------------------------------------------------
st.subheader("Question 2: What would we do to reduce churn?")

if df_filtered.empty:
    st.warning("No churned customers found based on the selected filters. Try adjusting the filters.")
else:
    churned_data_filtered = df_filtered[df_filtered['Churn Reason'] != 'Unknown'].copy()
    top_churn_reasons = churned_data_filtered['Churn Reason'].value_counts().head(5)

    col3, col4 = st.columns(2)

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
                    top_reason_data,
                    lat="Latitude", lon="Longitude",
                    color="Churn Reason",
                    hover_name="Customer ID",
                    hover_data=["Age", "Contract"],
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    zoom=3.5
                )
                fig_map.update_layout(
                    mapbox_style="carto-positron",
                    mapbox_center={"lat": lat_center, "lon": lon_center}
                )
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.info("No geographical data available for this selection.")
        else:
            st.info("No geographical data available for mapping.")

    with st.expander("🌍 Click to View Insights from the Geographical Churn Distribution Map"):
        st.subheader("📍 High Churn Clusters in Urban Areas")
        st.write("**Observation:** The majority of churn points are concentrated in highly populated cities...")
        st.write("**Strategy:** Implement location-based retention offers...")

        st.subheader("🏆 Competitor Influence is a Key Factor Across Regions")
        st.write("**Observation:** The most frequent churn category is 'Competitor'...")
        st.write("**Strategy:** Strengthen loyalty programs...")

        st.subheader("📞 Dissatisfaction and Customer Service Issues Vary by Location")
        st.write("**Observation:** Purple (Attitude) and Blue (Dissatisfaction) dots are spread throughout...")
        st.write("**Strategy:** Focus on service training improvements...")

        st.subheader("💰 Pricing Concerns Are More Evenly Distributed")
        st.write("**Observation:** Green dots (Price) are widely spread across the map...")
        st.write("**Strategy:** Introduce tiered pricing plans...")

    with st.expander("💡 Click to View Gender-Based Churn Insights"):
        st.subheader("📌 Female Churn")
        st.write("**Takeaway:** Women primarily leave due to competitor pricing and device quality...")

        st.subheader("📌 Male Churn")
        st.write("**Takeaway:** Device quality is the biggest concern for male customers...")

        st.subheader("📌 Overall Churn")
        st.write("**Takeaway:** Device quality and pricing are the biggest churn drivers...")

    # Top Churn Categories
    top_churn_categories = churned_data_filtered['Churn Category'].value_counts().head(5)

    col5, col6 = st.columns(2)

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
                    top_category_data,
                    lat="Latitude", lon="Longitude",
                    color="Churn Category",
                    hover_name="Customer ID",
                    hover_data=["Age", "Contract"],
                    color_discrete_sequence=px.colors.qualitative.Vivid,
                    zoom=3.5
                )
                fig_map_category.update_layout(
                    mapbox_style="carto-positron",
                    mapbox_center={"lat": lat_center, "lon": lon_center}
                )
                st.plotly_chart(fig_map_category, use_container_width=True)
            else:
                st.info("No geographical data available for this selection.")
        else:
            st.info("No geographical data available for mapping.")

    with st.expander("💡 Click to View Churn Category Insights"):
        st.subheader("📌 Overall Churn Trends")
        st.write("**Takeaway:** Competitor influence is the primary churn category...")

        st.subheader("📌 Male Churn Trends")
        st.write("**Takeaway:** Male customers churn mainly due to competitor influence and dissatisfaction...")

        st.subheader("📌 Female Churn Trends")
        st.write("**Takeaway:** Female customers are more likely to churn due to competitor influence and pricing...")

# ----------------------------------------------------
# Section 3: Understanding Churned Customers
# ----------------------------------------------------
st.subheader("Question 3: What should be the strategy to reduce churn?")

if df_filtered.empty:
    st.warning("No churned customers found based on the selected filters. Try adjusting the filters.")
else:
    def age_category(age):
        if age < 30:
            return 'Young Adults'
        elif 30 <= age < 50:
            return 'Middle-Aged Adults'
        else:
            return 'Seniors'

    df_filtered['Age Group'] = df_filtered['Age'].apply(age_category)

    # Pie charts
    age_group_counts = df_filtered['Age Group'].value_counts()
    contract_counts = df_filtered['Contract'].value_counts()

    col7, col8 = st.columns(2)

    with col7:
        fig1 = go.Figure(go.Pie(
            labels=age_group_counts.index, 
            values=age_group_counts,
            marker=dict(colors=['#ff9999','#66b3ff','#99ff99'])
        ))
        fig1.update_layout(title="📊 Churned Customers by Age Group")
        st.plotly_chart(fig1)

    with col8:
        fig2 = go.Figure(go.Pie(
            labels=contract_counts.index, 
            values=contract_counts,
            marker=dict(colors=['#ffcc99','#ff6666','#66b3ff'])
        ))
        fig2.update_layout(title="📜 Churned Customers by Contract Type")
        st.plotly_chart(fig2)

    # Preprocess data for Tenure Group
    df_filtered = preprocess_data(df_filtered)

    # Display the gold line chart
    col9, _ = st.columns([1, 0.2])
    with col9:
        plot_cltv_trend(df_filtered)

    # Add an expander with additional insights for CLTV by Tenure Group
    with st.expander("🔍 Click to View Insights on CLTV by Tenure Group"):
        st.subheader("⚡ Early Tenure CLTV (0–6 months)")
        st.write(
            "**Observation:** Newly joined customers (0–6 months) often have lower CLTV—"
            "this can reflect short billing cycles, introductory offers, or limited usage."
        )
        st.write(
            "**Strategy:** Provide strong onboarding experiences and early engagement offers. "
            "Consider quick-win promotions to build brand loyalty from Day 1."
        )

        st.subheader("📈 Mid-Tenure CLTV (7–36 months)")
        st.write(
            "**Observation:** CLTV tends to gradually increase through 7–36 months as customers "
            "adopt more services or bundling options."
        )
        st.write(
            "**Strategy:** Encourage cross-selling of additional services, offer mid-contract "
            "upgrades or loyalty rewards to further increase customer value."
        )

        st.subheader("🏆 Late Tenure CLTV (49–60 months)")
        st.write(
            "**Observation:** There is often a spike in the 49–60 months bracket, indicating "
            "long-term customers who remain see higher value and spend more."
        )
        st.write(
            "**Strategy:** Provide loyalty perks, VIP support lines, or device upgrades to reward "
            "and retain these valuable customers."
        )

        st.subheader("🔄 61+ Months Plateau or Slight Dip")
        st.write(
            "**Observation:** Some seasoned customers might plateau or slightly reduce spend—"
            "they may no longer need add-on services or could be exploring alternatives."
        )
        st.write(
            "**Strategy:** Consider re-engagement campaigns, special senior/family offers, or "
            "long-term discount bundles to maintain high-value customers."
        )

    st.write('### 📌 What Should Be the Strategy to Reduce Churn?')

    with st.expander("💡 Click to View Detailed Strategy Suggestions"):
        st.markdown("## **Recommendation Overview**")

        st.subheader("📌 Churn Insights by Age Group")
        st.write("**Takeaway:** Seniors have the highest churn rate...")

        st.subheader("📌 Churn Insights by Contract Type")
        st.write("**Takeaway:** The majority of churned customers are on month-to-month contracts...")

        st.markdown("### **Key Churn Factors & Strategies to Address Them**")

        st.markdown("#### ✔️ **Competitor-Driven Churn**")
        st.write("- Monitor and analyze competitors’ pricing...")

        st.markdown("#### 📉 **Dissatisfaction-Driven Churn**")
        st.write("- Improve service quality, network coverage...")

        st.markdown("#### 🤝 **Customer Service-Related Churn**")
        st.write("- Train customer service teams to handle complaints with empathy...")

st.write('---')
