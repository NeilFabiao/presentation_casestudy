import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------
# 1. Set Page Configuration (Must Be First Streamlit Command)
# ----------------------------------------------------
st.set_page_config(
    page_title="Telco Churn - Interactive Report",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
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

    # Create the figure
    fig = px.line(
        cltv_by_tenure,
        x="Tenure Group",
        y="CLTV",
        markers=True,
        title="📈 CLTV Trend by Tenure Group",
        labels={"CLTV": "Average CLTV", "Tenure Group": "Tenure Group"}
    )
    fig.update_traces(line=dict(color="gold", width=3))
    fig.update_xaxes(tickangle=-45)

    # Use two columns: one for the chart, one for the legend
    col_chart, col_legend = st.columns([6, 1])  # Adjusts width ratio 

    with col_chart:
        st.plotly_chart(fig, use_container_width=True)

    with col_legend:
        st.markdown(
            """
            **Tenure Group Legend**  
            - 0-6 months = ~0-0.5 yr  
            - 7-12 months = ~0.5-1 yr  
            - 13-24 months = 1-2 yrs  
            - 25-36 months = 2-3 yrs  
            - 37-48 months = 3-4 yrs  
            - 49-60 months = 4-5 yrs  
            - 61+ months = 5+ yrs
            """
        )


# Load Data
df = load_data('telco.csv')

# ----------------------------------------------------
# 3. Main Title and Description
# ----------------------------------------------------
st.title("Telco Churn Analysis 📊")

st.write(
    "Welcome to the **Telecommunications Churn Analysis Dashboard!** 🚀 "
    "This interactive report explores key insights about customer churn, "
    "helping us understand trends, challenges, and strategies to improve retention. "
    "(To filter the data, click on the option on the left.)"
)

st.markdown(
    """
    ### 🔍 Key Insights:
    - **High Churn Services**: Internet services, unlimited data, and streaming have the highest cancellation rates.  
    - **Demographic Trends**: Customers over 50 and those with monthly contracts are more likely to cancel.  
    - **Loyalty Programs**: Competitive pricing based on location and effective customer communication can help reduce churn.  
    """
)

st.write("---")

# ----------------------------------------------------
# 4. Sidebar Filters (Gender & Churn Status)
# ----------------------------------------------------
with st.sidebar:
    st.header("Select Filters")
    st.write(
        "🔍 **Filter the data to explore churn trends by gender and churn status.** "
        "Adjust the options below to analyze specific customer segments."
    )
    
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
st.subheader("Question 1: Which services tend to have a high churn rate?")

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
    st.markdown("### Top 10 Services by Churn Rate")
    top_5_services = service_churn_df.sort_values(by="Churn Percentage", ascending=False).head(10)
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

# Expander for insights
with st.expander("💡 Click to view information on churn by service"):
    st.subheader("📌 General Churn Trends")
    st.write("**Conclusion:** The services with the highest cancellation rates are Internet, Unlimited Data, and Streaming Services.")

    st.subheader("📌 Internet and Data Churn")
    st.write("**Conclusion:** Customers using Internet services (31.83%) and Unlimited Data (31.65%) have the highest cancellation rates.")

    st.subheader("📌 Streaming Services Churn")
    st.write("**Conclusion:** TV Streaming (30.07%), Film Streaming (29.94%), and Music Streaming (29.26%) also show high cancellation rates.")

st.write("---")

# ----------------------------------------------------
# Section 2: What would we do to reduce churn?
# ----------------------------------------------------
st.subheader("Question 2: What would we do to reduce churn?")

if df_filtered.empty:
    st.warning("No churned customers found based on the selected filters. Try adjusting the filters.")
else:
    churned_data_filtered = df_filtered[df_filtered['Churn Reason'] != 'Unknown'].copy()
    
    top_churn_reasons = churned_data_filtered['Churn Reason'].value_counts().head(10)
    # Top Churn Categories
    top_churn_categories = churned_data_filtered['Churn Category'].value_counts().head(5)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### 🏆 Top 5 Churn Categories")
        df_top_categories = top_churn_categories.reset_index()
        df_top_categories.columns = ['Churn Category', 'Count']
        st.dataframe(df_top_categories, hide_index=True)

    with col4:
        st.markdown("### 🌍 Geographic Distribution of the Top 5 Churn Categories")
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

with st.expander("💡 Click to view insights on churn categories"):
    st.subheader("📌 General Churn Trends")
    st.write("**Conclusion:** Competitor influence is the main reason for cancellations.")

    st.subheader("📌 Churn Trends Among Men")
    st.write("**Conclusion:** Male customers primarily cancel due to competitor influence and dissatisfaction with services.")

    st.subheader("📌 Churn Trends Among Women")
    st.write("**Conclusion:** Female customers are more likely to cancel due to competitor influence and pricing.")

with st.expander("🌍 Click to view insights from the Geographic Churn Distribution Map"):

    st.subheader("📍 High Concentration of Cancellations in Urban Areas")
    st.write("**Observation:** Most cancellations are concentrated in highly populated cities (San Francisco, Los Angeles, and San Diego), "
             "indicating that urban customers are more likely to switch providers due to increased competition.")

    st.subheader("🏆 Competitor Influence is a Key Factor Across All Regions")
    st.write("**Observation:** The most frequent churn category is 'Competition' (orange points), suggesting "
             "that many customers are switching to other service providers.")

    st.subheader("📞 Dissatisfaction and Customer Service Issues Vary by Location")
    st.write("**Observation:** Purple points (Attitude) and blue points (Dissatisfaction) are spread across various regions, "
             "indicating that **service quality and customer interactions vary by location**.")

    st.subheader("💰 Price Concerns Are More Evenly Distributed")
    st.write("**Observation:** Green points (Price) are evenly distributed on the map, "
             "indicating that **price sensitivity is not restricted to a specific location**.")

col5, col6 = st.columns(2)

with col5:
    st.markdown("### 🏆 Top 10 Reasons for Churn")
    df_top_reasons = top_churn_reasons.reset_index()
    df_top_reasons.columns = ['Churn Reason', 'Count']
    st.dataframe(df_top_reasons, hide_index=True)

with col6:
    st.markdown("### 🌍 Geographic Distribution of the Top 5 Reasons for Churn")
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

with st.expander("💡 Click to view insights on churn by gender"):
    st.subheader("📌 Churn Among Women")
    st.write("**Conclusion:** Women primarily cancel due to competitor pricing and device quality.")

    st.subheader("📌 Churn Among Men")
    st.write("**Conclusion:** Device quality is the main concern for male customers.")

with st.expander("🌍 Click to view insights from the Geographic Churn Distribution Map"):
    st.subheader("📍 High Concentration of Cancellations in Urban Areas")
    st.write("**Observation:** Most cancellations are concentrated in highly populated cities (San Francisco, Los Angeles, and San Diego).")

    st.subheader("🏆 Competitor Influence is a Key Factor Across All Regions")
    st.write("**Observation:** The most frequent churn category is 'Competition'.")

    st.subheader("📞 Dissatisfaction and Customer Service Issues Vary by Location")
    st.write("**Observation:** Purple points (Attitude) and blue points (Dissatisfaction) are spread across different regions.")

    st.subheader("💰 Price Concerns Are More Evenly Distributed")
    st.write("**Observation:** Green points (Price) are widely distributed across the map.")

st.write("---")

# ----------------------------------------------------
# Section 3: What should be the strategy to reduce churn?
# ----------------------------------------------------
st.subheader("Question 3: What should be the strategy to reduce churn?")

if not df_filtered.empty:
    # Categorizing Age Groups (First approach)
    def age_category(age):
        if age < 30:
            return '(Under 30 years)'
        elif 30 <= age < 50:
            return '(30-50 years)'
        else:
            return '(Over 50 years)'

    df_filtered['Age Group'] = df_filtered['Age'].apply(age_category)

    # Count churned customers per Age Group
    churn_counts_by_age = df_filtered['Age Group'].value_counts().reset_index()
    churn_counts_by_age.columns = ['Age Group', 'Churn Count']

    # Calculate total churned customers (based on current filter)
    total_churned = df_filtered.shape[0]

    # Calculate churn percentage for each Age Group
    churn_counts_by_age['Churn Percentage'] = (churn_counts_by_age['Churn Count'] / total_churned) * 100

    # Create a single-line summary with percentages side by side
    churn_summary = " | ".join(
        [f"✅ **{row['Age Group']}**: {row['Churn Percentage']:.2f}%" for _, row in churn_counts_by_age.iterrows()]
    )

    # Display the summary in a single line
    st.subheader("📊 Churn Rate by Age Group")
    st.markdown(f"**{churn_summary}**")

else:
    st.warning("No churned customers found based on the selected filters. Try adjusting the filters.")
    
# Creating Pie Charts by Age Group
age_groups = df_filtered['Age Group'].unique()
cols = st.columns(len(age_groups))

for i, age_group in enumerate(age_groups):
    churn_reasons = df_filtered[df_filtered['Age Group'] == age_group]['Churn Category'].value_counts()
    
    if not churn_reasons.empty:
        fig = go.Figure(
            go.Pie(
                labels=churn_reasons.index,
                values=churn_reasons.values,
                hole=0.4,  # Donut-style
                marker=dict(colors=["#E63946", "#457B9D", "#F4A261", "#2A9D8F", "#8D99AE"]),
            )
        )
        fig.update_layout(title=f"Churn Reasons - {age_group}")

        with cols[i]:
            st.plotly_chart(fig, use_container_width=True)

# Expander Section for Insights
with st.expander("💡 Click to view insights on churn by age and reason"):
    st.subheader("📌 General Churn Trends")
    st.write(
        "**Conclusion:** Most customers who cancel are in the **Over 50** age group (~50%), "
        "with the main reason being **Competition**, followed by **Price** and **Dissatisfaction**."
    )

    st.subheader("📊 Churn by Age Group")
    st.markdown("""
    - **(Over 50 years)**: They have the highest churn rate. Main reasons include:
        - More attractive offers from competitors.
        - Dissatisfaction with the service experience.

    - **(30-50 years)**: Represent around 25% of cancellations, mainly due to:
        - High prices and seeking cheaper plans.
        - Service quality and customer support influencing decisions to switch.

    - **(Under 30 years)**: Although the lowest churn rate, they still:
        - Tend to switch providers more frequently.
        - Prefer flexible plans with no long-term commitment.
    """)

st.write('---')

# Categorizing Age Groups (Second approach for competition analysis)
def age_category_competition(age):
    if age < 30:
        return "Under 30"
    elif 30 <= age < 50:
        return "30-50"
    else:
        return "50+"

df_filtered['Age Group'] = df_filtered['Age'].apply(age_category_competition)

# Filter churn cases where the reason is "Competition"
df_competition = df_filtered[df_filtered["Churn Reason"].str.contains("Competitor", na=False)].copy()

# Define fixed color mapping for churn reasons
unique_reasons = df_competition["Churn Reason"].unique()
fixed_colors = px.colors.qualitative.Set1  # Choose a consistent color scheme
color_mapping = {reason: fixed_colors[i % len(fixed_colors)] for i, reason in enumerate(unique_reasons)}

# --- Layout for Tables ---
st.subheader("📊 Churn Reasons by Age Group")
col7, col8, col9 = st.columns(3)

for col, age_group in zip([col7, col8, col9], ["Under 30", "30-50", "50+"]):
    df_group = df_competition[df_competition["Age Group"] == age_group]
    
    with col:
        st.markdown(f"### 🏆 {age_group}")
        if not df_group.empty:
            df_table = df_group["Churn Reason"].value_counts().head(5).reset_index()
            df_table.columns = ["Churn Reason", "Count"]
            st.dataframe(df_table, hide_index=True)
        else:
            st.info(f"No data available for {age_group}")

st.write("---")

# --- Layout for Maps ---
st.subheader("🌍 Geographic Distribution of Churn by Age Group")
col10, col11, col12 = st.columns(3)

for i, (col, age_group) in enumerate(zip([col10, col11, col12], ["Under 30", "30-50", "50+"])):
    df_group = df_competition[df_competition["Age Group"] == age_group]
    
    with col:
        st.markdown(f"### 🌍 {age_group}")
        if not df_group.empty:
            lat_center = df_group["Latitude"].mean()
            lon_center = df_group["Longitude"].mean()

            fig_map = px.scatter_mapbox(
                df_group,
                lat="Latitude", lon="Longitude",
                color="Churn Reason",
                hover_name="Customer ID",
                hover_data=["Age", "Contract"],
                color_discrete_map=color_mapping,  # Apply fixed colors
                zoom=5
            )
            
            fig_map.update_layout(
                mapbox_style="carto-positron",
                mapbox_center={"lat": lat_center, "lon": lon_center},
                legend=dict(
                    orientation="h",  # Horizontal legend
                    y=-0.2,           # Move legend below the map
                    x=0.5,            # Center the legend
                    xanchor="center",
                )
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info(f"No geographical data available for {age_group}")

st.write("---")

# Preprocess data for Tenure Group
df_filtered = preprocess_data(df_filtered)

# Ensure 'Contract' column exists before processing
if 'Contract' in df_filtered.columns:
    # Count churned customers per Contract Type
    churn_counts_by_contract = df_filtered['Contract'].value_counts().reset_index()
    churn_counts_by_contract.columns = ['Contract Type', 'Churn Count']

    # Since we defined total_churned earlier, ensure it exists
    # (If the user changes filters midway, re-calculate as needed.)
    total_churned = len(df_filtered)
    if total_churned > 0:
        churn_counts_by_contract['Churn Percentage'] = (
            churn_counts_by_contract['Churn Count'] / total_churned
        ) * 100

        churn_summary_contract = " | ".join(
            [f"📜 **{row['Contract Type']}**: {row['Churn Percentage']:.2f}%" for _, row in churn_counts_by_contract.iterrows()]
        )
        st.markdown(f"📞 **Churn Rate by Contract Type:** {churn_summary_contract}")
    else:
        st.info("No churned customers to calculate Contract Type percentages.")

# Display the gold line chart
plot_cltv_trend(df_filtered)

# Add an expander with additional insights on CLTV by tenure group
with st.expander("🔍 Click to view insights on CLTV by tenure group"):

    st.subheader("⚡ CLTV for Short-Term Customers (0–6 months)")
    st.write("**Observation:** Newly acquired customers (0–6 months) tend to have a lower CLTV—"
             "this may reflect short billing cycles, introductory offers, or limited usage.")

    st.subheader("📈 CLTV for Medium-Term Customers (7–36 months)")
    st.write("**Observation:** CLTV gradually increases between 7 and 36 months as customers "
             "adopt more services or bundled options.")

    st.subheader("🏆 CLTV for Long-Term Customers (49–60 months)")
    st.write("**Observation:** There is often a peak in the 49–60 month range, indicating that "
             "long-term customers perceive more value and spend more.")

    st.subheader("🔄 Stabilization or Slight Decline After 61+ Months")
    st.write("**Observation:** Some older customers may stabilize or slightly reduce their spending—"
             "they may no longer need additional services or could be exploring alternatives.")

st.write('### 📌 What should be the strategy to reduce churn?')

with st.expander("💡 Click to view detailed strategy suggestions"):

    st.markdown("## **Overview of Recommendations**")

    # Insights on churn by age group
    st.subheader("📌 Insights on Churn by Age Group")
    st.write("**Strategy:** Consider **special offer campaigns for seniors/families** or **long-term discounted bundles** to retain high-value customers.")

    # Insights on churn by contract type
    st.subheader("📌 Insights on Churn by Contract Type")
    st.write("**Strategy:** Provide **effective onboarding experiences and initial incentives** for monthly contracts, promoting loyalty early on.")
    st.write("**Strategy:** Encourage **cross-selling of additional services**, mid-contract upgrades, or loyalty rewards to increase customer value.")

    # Key churn factors and strategies
    st.markdown("### **Key Churn Factors and Strategies to Mitigate Them**")

    # Churn due to competition
    st.markdown("#### ✔️ **Competition**")
    st.write("**Strategy:** Strengthen **loyalty programs** and offer **competitive bundles** to retain customers.")

    # Churn due to dissatisfaction
    st.markdown("#### 📉 **Dissatisfaction**")
    st.write("**Strategy:** Improve **service quality, network coverage, and customer experience** to reduce churn caused by dissatisfaction.")

    # Churn due to customer service
    st.markdown("#### 🤝 **Customer Service**")
    st.write("**Strategy:** Invest in **regional training for support teams** and **optimize customer service** processes.")

    # Churn based on location
    st.markdown("#### 🌍 **Location-Based Churn**")
    st.write("**Strategy:** Implement **location-specific retention offers**, focusing on urban areas with higher churn rates.")

    # Price concerns
    st.markdown("#### 💰 **Price and Perceived Value**")
    st.write("**Strategy:** Offer **tiered pricing plans** and **regional discounts** to improve affordability and retention.")

    # Retaining high-value customers
    st.markdown("#### 🏆 **Retaining High-Value & Long-Term Customers**")
    st.write("**Strategy:** Provide **loyalty benefits, VIP support lines, or device upgrades** to reward and retain these valuable customers.")

    # Final observations
    st.subheader("🔍 Final Observations")
    st.write("**Senior and middle-aged customers** are the most likely to cancel due to competitor offers and dissatisfaction with services. "
             "Meanwhile, **younger customers** seek greater flexibility, often preferring short-term contracts.")

st.write('---')
