import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------
# 1. Set Page Configuration (Must Be First Streamlit Command)
# ----------------------------------------------------
st.set_page_config(
    page_title="Telco Churn - Entrevista Vodacom",
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
    col_chart, col_legend = st.columns([6, 1])  # To Adjust width ratio 

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
    "Bem-vindo ao **Dashboard de Análise Churn (Rotatividade) de Telecomunicações!** 🚀 "
    
 "Este relatório interativo explora importantes insights sobre a rotatividade de clientes, ajudando-nos"
 "compreender as tendências, desafios e estratégias para melhorar a retenção."
)

st.markdown(
    "### 🔍 Principais descobertas:\n"
 "- **Serviços de alta rotatividade**: Os serviços de Internet, dados ilimitados e streaming apresentam as taxas de cancelamento mais elevadas. \n"
 "- **Tendências demográficas**: Os idosos e os clientes com contratos mensais são os mais propensos a cancelar o serviço. \n"
 "- ** Programas de lealdade, preços competitivos com base na localização e uma comunicação eficaz com o cliente podem ajudar a reduzir a rotatividade."
)

st.write("---")

# ----------------------------------------------------
# 4. Sidebar Filters (Gender & Churn Status)
# ----------------------------------------------------
with st.sidebar:
    st.header("Select Filters")
    st.write("🔍 **Filtre os dados para explorar as tendências de rotatividade por género e o estado de rotatividade.** " 
             "Ajuste as opções abaixo para analisar grupos específicos de clientes.")
    
    gender_filter = st.radio("Seleccionar género", options=["All", "Male", "Female"], index=0)
    churn_filter = st.radio("Seleccionar estado de rotatividade", options=["Yes", "No"], index=0)

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
st.subheader("Questão 1: Que serviços tendem a ter uma elevada rotatividade?")

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
    st.markdown("### Top 10 Servicos por Churn Rate")
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

# Expansor para insights
with st.expander("💡 Clique para ver informação sobre a rotatividade por serviço"):
    st.subheader("📌 Tendências gerais de cancelamento")
    st.write("**Conclusão:** Os serviços com as maiores taxas de cancelamento são Internet, Dados Ilimitados e Serviços de Streaming.")

    st.subheader("📌 Cancelamento de Internet e Dados")
    st.write("**Conclusão:** Os clientes que utilizam o serviço de Internet (31,83%) e Dados Ilimitados (31,65%) apresentam as taxas de cancelamento mais elevadas.")

    st.subheader("📌 Cancelamento de Serviços de Streaming")
    st.write("**Conclusão:** Streaming de TV (30,07%), Streaming de Filmes (29,94%) e Streaming de Música (29,26%) registam altas taxas de cancelamento.")

st.write("---")

# ----------------------------------------------------
# Section 2: "What would we do to reduce churn?"
# ----------------------------------------------------
st.subheader("Questão 2: O que faríamos para reduzir a churn?")

if df_filtered.empty:
    st.warning("No churned customers found based on the selected filters. Try adjusting the filters.")
else:
    churned_data_filtered = df_filtered[df_filtered['Churn Reason'] != 'Unknown'].copy()
    
    top_churn_reasons = churned_data_filtered['Churn Reason'].value_counts().head(10)
    # Top Churn Categories
    top_churn_categories = churned_data_filtered['Churn Category'].value_counts().head(5)

    col5, col6 = st.columns(2)

    with col5:
        st.markdown("### 🏆 5 principais categorias de churn")
        df_top_categories = top_churn_categories.reset_index()
        df_top_categories.columns = ['Churn Category', 'Count']
        st.dataframe(df_top_categories, hide_index=True)

    with col6:
        st.markdown("### 🌍 Distribuição geográfica das 5 principais categorias de churn")
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

    with st.expander("💡 Clique para ver insights sobre categorias de churn"):
        st.subheader("📌 Tendências gerais de churn")
        st.write("**Conclusão:** A influência da concorrência é a principal razão para o cancelamento.")
    
        st.subheader("📌 Tendências de cancelamento entre homens")
        st.write("**Conclusão:** Os clientes do sexo masculino cancelam principalmente devido à influência da concorrência e insatisfação dos serviços.")
    
        st.subheader("📌 Tendências de cancelamento entre mulheres")
        st.write("**Conclusão:** As clientes do sexo feminino têm maior probabilidade de cancelar devido à influência da concorrência e aos preços.")


    with st.expander("🌍 Clique para ver insights do Mapa de Distribuição Geográfica do Cancelamento"):

        st.subheader("📍 Concentração elevada de cancelamentos em áreas urbanas")
        st.write("**Observação:** A maioria dos cancelamentos está concentrada em cidades altamente povoadas ((San francisco, Los angeles e San Diego)), "
            "indicando que os clientes urbanos têm maior probabilidade de mudar de fornecedor devido ao aumento da concorrência.")
        
        st.subheader("🏆 Influência da concorrência é um fator-chave em todas as regiões")
        st.write("**Observação:** A categoria de cancelamento mais frequente é '**Concorrência**' (pontos laranja), sugerindo "
            "que muitos clientes estão a mudar para outros fornecedores de serviço.")
        
        st.subheader("📞 Insatisfação e problemas com o atendimento ao cliente variam por localização")
        st.write("**Observação:** Os pontos roxos (Atitude) e azuis (Insatisfação) estão distribuídos por várias regiões, "
            "indicando que **a qualidade do serviço e as interações com os clientes variam conforme a localização**.")
        
        st.subheader("💰 Preocupações com preços estão mais uniformemente distribuídas")
        st.write("**Observação:** Os pontos verdes (Preço) estão distribuídos de forma homogénea no mapa, "
            "indicando que **a sensibilidade ao preço não está restrita a uma localização específica**.")


col3, col4 = st.columns(2)

with col3:
    st.markdown("### 🏆 10 principais motivos de churn")
    df_top_reasons = top_churn_reasons.reset_index()
    df_top_reasons.columns = ['Churn Reason', 'Count']
    st.dataframe(df_top_reasons, hide_index=True)

with col4:
    st.markdown("### 🌍 Distribuição geográfica das 5 principais motivos de churn")
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

with st.expander("💡 Clique para ver insights sobre cancelamento por género"):
    st.subheader("📌 Cancelamento entre mulheres")
    st.write("**Conclusão:** As mulheres cancelam principalmente devido aos preços da concorrência e à qualidade dos dispositivos.")

    st.subheader("📌 Cancelamento entre homens")
    st.write("**Conclusão:** A qualidade dos dispositivos é a principal preocupação dos clientes do sexo masculino.")

with st.expander("🌍 Clique para ver insights do Mapa de Distribuição Geográfica do Cancelamento"):
    st.subheader("📍 Concentração elevada de cancelamentos em áreas urbanas")
    st.write("**Observação:** A maioria dos cancelamentos está concentrada em cidades altamente povoadas (San francisco, Los angeles e San Diego).")

    st.subheader("🏆 Influência da concorrência é um fator-chave em todas as regiões")
    st.write("**Observação:** A categoria de cancelamento mais frequente é 'Concorrência'.")

    st.subheader("📞 Insatisfação e problemas com o atendimento ao cliente variam por localização")
    st.write("**Observação:** Os pontos roxos (Atitude) e azuis (Insatisfação) estão espalhados por diferentes regiões.")

    st.subheader("💰 Preocupações com preços estão mais uniformemente distribuídas")
    st.write("**Observação:** Os pontos verdes (Preço) estão amplamente distribuídos no mapa.")


st.write("---")

# ----------------------------------------------------
# Section 3: Understanding Churned Customers
# ----------------------------------------------------
st.subheader("Questão 3: Qual deve ser a estratégia para reduzir o cancelamento?")

if not df_filtered.empty:
    # Categorizing Age Groups
    def age_category(age):
        if age < 30:
            return 'Jovens (Menores que 30 anos)'
        elif 30 <= age < 50:
            return 'Adultos (Entre 30-50 anos)'
        else:
            return 'Seniors(Maiores de 50 anos)'

    df_filtered['Age Group'] = df_filtered['Age'].apply(age_category)

    # Count churned customers per Age Group
    churn_counts_by_age = df_filtered['Age Group'].value_counts().reset_index()
    churn_counts_by_age.columns = ['Age Group', 'Churn Count']

    # Calculate total churned customers
    total_churned = df_filtered.shape[0]

    # Calculate churn percentage for each Age Group
    churn_counts_by_age['Churn Percentage'] = (churn_counts_by_age['Churn Count'] / total_churned) * 100

    # Create a single-line summary with percentages side by side
    churn_summary = " | ".join(
        [f"✅ **{row['Age Group']}**: {row['Churn Percentage']:.2f}%" for _, row in churn_counts_by_age.iterrows()]
    )

    # Display the summary in a single line
    st.subheader("📊 Taxa de churn por faixa etária")
    st.markdown(f"**{churn_summary}**")

else:
    st.warning("No churned customers found based on the selected filters. Try adjusting the filters.")
    
# Creating Pie Charts
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
with st.expander("💡 Clique para ver insights sobre cancelamento por idade e motivo"):

    # **Tendências gerais de cancelamento**
    st.subheader("📌 Tendências gerais de cancelamento")
    st.write(
        "**Conclusão:** A maioria dos clientes que cancelam pertencem ao grupo etário **Seniores (~50%)**, "
        "com o principal motivo sendo **Concorrência**, seguido por **Preço** e **Insatisfação**."
    )

    # **Cancelamento por faixa etária**
    st.subheader("📊 Cancelamento por Faixa Etária")

    st.markdown("""
    - **Seniores (50+ anos)**: Apresentam a maior taxa de cancelamento (~50%). Os principais motivos incluem:
        - Influência da concorrência com ofertas mais atrativas.
        - Insatisfação com a experiência do serviço.

    - **Adultos (30-50 anos)**: Representam cerca de **33%** dos cancelamentos, sendo mais sensíveis a:
        - Preços elevados e busca por planos mais baratos.
        - Qualidade do serviço e atendimento impactando a decisão de troca.

    - **Jovens (<30 anos)**: São os que menos cancelam (~16%), mas ainda assim enfrentam:
        - Maior propensão a trocar de provedor frequentemente.
        - Preferência por planos flexíveis e sem fidelização.
    """)

st.write('---')
    
# Preprocess data for Tenure Group
df_filtered = preprocess_data(df_filtered)

# Ensure 'Contract' column exists before processing
if 'Contract' in df_filtered.columns:
    # Count churned customers per Contract Type
    churn_counts_by_contract = df_filtered['Contract'].value_counts().reset_index()
    churn_counts_by_contract.columns = ['Contract Type', 'Churn Count']

    # Calculate churn percentage for each Contract Type
    churn_counts_by_contract['Churn Percentage'] = (churn_counts_by_contract['Churn Count'] / total_churned) * 100

    # Create a single-line summary for Contract Types
    churn_summary_contract = " | ".join(
        [f"📜 **{row['Contract Type']}**: {row['Churn Percentage']:.2f}%" for _, row in churn_counts_by_contract.iterrows()]
    )

    # Display the combined summary
    st.markdown(f"📜 **By Contract Type:** {churn_summary_contract}")
    
# Display the gold line chart
plot_cltv_trend(df_filtered)

# Adicionar um expansor com insights adicionais sobre CLTV por grupo de tempo de permanência
with st.expander("🔍 Clique para ver insights sobre CLTV por grupo de permanência"):

    st.subheader("⚡ CLTV de curta permanência (0–6 meses)")
    st.write("**Observação:** Clientes recém-chegados (0–6 meses) tendem a ter um CLTV mais baixo—"
        "isto pode refletir ciclos de faturação curtos, ofertas introdutórias ou utilização limitada.")

    st.subheader("📈 CLTV de média permanência (7–36 meses)")
    st.write("**Observação:** O CLTV tende a aumentar gradualmente entre os 7 e 36 meses, à medida que os clientes "
        "adotam mais serviços ou opções de pacotes.")

    st.subheader("🏆 CLTV de longa permanência (49–60 meses)")
    st.write("**Observação:** Há frequentemente um pico na faixa dos 49–60 meses, indicando que "
        "os clientes de longa duração veem mais valor e gastam mais.")

    st.subheader("🔄 Estabilização ou ligeira queda após 61+ meses")
    st.write("**Observação:** Alguns clientes mais antigos podem estabilizar ou reduzir ligeiramente os gastos—"
        "podem já não precisar de serviços adicionais ou estar a explorar alternativas.")

st.write('### 📌 Qual deve ser a estratégia para reduzir o cancelamento?')

with st.expander("💡 Clique para ver sugestões detalhadas de estratégia"):

    st.markdown("## **Visão geral das recomendações**")

    # Insights sobre cancelamento por faixa etária
    st.subheader("📌 Insights sobre cancelamento por faixa etária")
    st.write("**Estratégia:** Considere **campanhas de ofertas especiais para seniores/famílias ou pacotes com descontos de longo prazo** para manter clientes de alto valor.")

    # Insights sobre cancelamento por tipo de contrato
    st.subheader("📌 Insights sobre cancelamento por tipo de contrato")
    st.write("**Estratégia:** Ofereça **experiências de onboarding eficazes e incentivos iniciais** para clientes com contratos mensais, promovendo a lealdade desde o início.")
    st.write("**Estratégia:** Incentive **a venda cruzada de serviços adicionais, upgrades a meio do contrato ou recompensas de lealdade** para aumentar o valor do cliente.")

    # Fatores-chave do cancelamento e estratégias
    st.markdown("### **Fatores-chave do cancelamento e estratégias para os mitigar**")

    # Cancelamento motivado pela concorrência
    st.markdown("#### ✔️ **Cancelamento devido à concorrência**")
    st.write("**Estratégia:** Reforce **os programas de lealdade** e ofereça **pacotes competitivos** para reter clientes.")

    # Cancelamento por insatisfação
    st.markdown("#### 📉 **Cancelamento devido à insatisfação**")
    st.write("**Estratégia:** Melhore **a qualidade do serviço, a cobertura da rede e a experiência do cliente** para reduzir o cancelamento por insatisfação.")

    # Cancelamento relacionado ao atendimento ao cliente
    st.markdown("#### 🤝 **Cancelamento devido ao atendimento ao cliente**")
    st.write("**Estratégia:** Invista em **formação regional para equipas de suporte** e **otimização do atendimento ao cliente**.")

    # Cancelamento baseado na localização
    st.markdown("#### 🌍 **Tendências de cancelamento por localização**")
    st.write("**Estratégia:** Implemente **ofertas de retenção baseadas na localização**, direcionadas para áreas urbanas com altas taxas de cancelamento.")

    # Preocupações com preços
    st.markdown("#### 💰 **Preocupações com preços e perceção de valor**")
    st.write("**Estratégia:** Introduza **planos de preços** e **descontos regionais específicos** para melhorar a acessibilidade e retenção.")

    # Retenção de clientes de alto valor
    st.markdown("#### 🏆 **Retenção de clientes de alto valor e longo prazo**")
    st.write("**Estratégia:** Ofereça **benefícios de lealdade, linhas de suporte VIP ou upgrades de dispositivos** para premiar e reter estes clientes valiosos.")

    # **Observações Finais**
    st.subheader("🔍 Observações Finais")
    st.write("Clientes **seniores e adultos de meia-idade** são os mais propensos a cancelar devido à concorrência e à insatisfação com o serviço. "
        "Já os **jovens adultos** buscam maior flexibilidade, preferindo contratos de curto prazo.")
 

st.write('---')
