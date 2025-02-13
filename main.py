import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from fpdf import FPDF
import base64
from tempfile import NamedTemporaryFile

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

df = load_data('telco.csv')

# ----------------------------------------------------
# 3. Main Title and Description
# ----------------------------------------------------
st.title("Telco Churn Analysis 📊")

st.write(
    "Welcome to the **Telco Churn Analysis Dashboard!** 🚀 "
    "This interactive report explores key insights into customer churn, helping us "
    "understand trends, challenges, and strategies for improving retention."
)

st.markdown(
    "### 🔍 Key Findings:\n"
    "- **High-Churn Services**: Internet Service, Unlimited Data, and Streaming Services have the highest churn rates.\n"
    "- **Demographic Trends**: Seniors and month-to-month contract customers are the most likely to churn.\n"
    "- **Retention Strategies**: Loyalty programs, competitive pricing, and customer engagement can help reduce churn."
)

st.write("---")

# ----------------------------------------------------
# 4. Sidebar Filters (Gender & Churn Status)
# ----------------------------------------------------
with st.sidebar:
    st.header("Select Filters")
    st.write("🔍 **Filter the data to explore churn trends by gender and churn status.** "
             "Adjust the options below to analyze specific customer groups.")
    
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
# 6. Visualizing Churn by Services
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
    st.markdown("### Top Services by Churn Rate")
    top_services = service_churn_df.sort_values(by="Churn Percentage", ascending=False).head(10)
    st.dataframe(top_services)

with col2:
    st.markdown("### Churn Percentage by Service")
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
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# 7. Generating & Downloading the Full Report as a PDF
# ----------------------------------------------------
def create_download_link(val, filename):
    """Encodes PDF data as a base64 link for download."""
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">📥 Download Full Report</a>'

st.write("### 📄 Download the Full Churn Report")

st.write(
    "Click the button below to generate and download a **detailed PDF report** "
    "including churn trends, visualizations, and key findings."
)

# Store generated figures
figs = []

# Generate sample visualizations (Add relevant charts)
for col in df.columns[:5]:  # Adjust for relevant columns
    fig, ax = plt.subplots()
    ax.hist(df[col].dropna(), bins=10, alpha=0.7)
    ax.set_title(f"Distribution of {col}")
    st.pyplot(fig)
    figs.append(fig)

export_as_pdf = st.button("📄 Generate Full Dashboard Report")

if export_as_pdf:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title Page
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Telco Churn Analysis Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "This report provides insights into customer churn trends, key findings, and recommendations.")

    # Add Charts to PDF
    for fig in figs:
        pdf.add_page()
        with NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.savefig(tmpfile.name, format='png', bbox_inches="tight")
            pdf.image(tmpfile.name, x=10, y=30, w=180)

    # Create Download Link
    html = create_download_link(pdf.output(dest="S").encode("latin-1"), "Telco_Churn_Report")
    st.markdown(html, unsafe_allow_html=True)
