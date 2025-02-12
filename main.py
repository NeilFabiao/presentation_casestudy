# Import necessary libraries
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.cluster import KMeans
import plotly.graph_objs as go  # Import graph objects

# Load the housing dataset from a CSV file
housing = pd.read_csv('housing.csv')

# Drop NaN values and duplicates
housing.dropna(inplace=True)
housing.drop_duplicates(inplace=True)

# Define ocean proximity options
ocean_proximity_options = ['<1H OCEAN', 'INLAND', 'NEAR OCEAN', 'NEAR BAY', 'ISLAND']

# Streamlit UI setup
st.set_page_config(page_title="California Housing Dashboard", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")
st.title("Housing Price Prediction 🏠")
st.write('Top left are the sliders to make the housing prediction')
st.write('---')

# Sidebar for user inputs
with st.sidebar:
    st.title("Input Features")
    # Collect user input
    user_input = {
        'total_bedrooms': st.slider('Total Bedrooms', housing['total_bedrooms'].min(), housing['total_bedrooms'].max(), housing['total_bedrooms'].median()),
        'median_income': st.slider('Median Income', housing['median_income'].min(), housing['median_income'].max(), housing['median_income'].median()),
        'housing_median_age': st.slider('Housing Median Age', housing['housing_median_age'].min(), housing['housing_median_age'].max(), housing['housing_median_age'].median()),
    }

# Convert user input to DataFrame
user_input_df = pd.DataFrame([user_input])

# Train the model with the entire dataset
X = housing[['total_bedrooms', 'median_income', 'housing_median_age']]
Y = housing['median_house_value']
model = DecisionTreeRegressor()
model.fit(X, Y)

# Define columns layout for the main panel
col1, col2, col3 = st.columns((2, 3, 2), gap="medium")

# Column 1: Input parameters and prediction
with col1:
    st.markdown('### Prediction')

    # Predict the price
    prediction = model.predict(user_input_df)[0]
    st.metric(label="Predicted Median House Value", value=f"${prediction * 1000:,.0f}")

# Column 2: Geographical distribution of predicted house
with col2:
    st.markdown('### Geographical Distribution of Predicted House')

    # Predict the price for the user input
    prediction = model.predict(user_input_df)[0]

    # Find the nearest record in the dataset to the predicted price
    nearest_record = housing.iloc[(housing['median_house_value'] - prediction).abs().argsort()[:1]]

    # Extract latitude and longitude from the nearest record
    latitude = nearest_record['latitude'].values[0]
    longitude = nearest_record['longitude'].values[0]

    # Create a DataFrame with predicted house values using the latitude and longitude from the nearest record
    predicted_house = pd.DataFrame({
        'latitude': [latitude],
        'longitude': [longitude],
        'PredictedValue': [prediction]
    })

    # Create a scatter plot for the predicted house
    fig = px.scatter_mapbox(
        predicted_house, 
        lat="latitude", 
        lon="longitude", 
        color="PredictedValue", 
        size="PredictedValue", 
        color_continuous_scale='viridis', 
        size_max=15, 
        zoom=3
    )
    fig.update_layout(mapbox_style="carto-positron")
    st.plotly_chart(fig, use_container_width=True)


# Column 3: Information about the data and top districts
with col3:
    st.markdown('### Dataset Citation and Reference')
    st.write("""
    The data was originally featured in a paper titled "Sparse spatial autoregressions" by 
    R. Kelley Pace and Ronald Barry. This dataset is a modified version of the California Housing dataset, 
    which is available from Luís Torgo's page at the University of Porto. 
    The information was encountered in "Hands-On Machine learning with Scikit-Learn and TensorFlow" by 
    [Aurélien Géron](https://inria.github.io/scikit-learn-mooc/python_scripts/datasets_california_housing.html).

    """)

# Additional analysis and visualizations can be added below

# Additional analysis and visualizations can be added below

st.markdown('### Geographical Distribution of Median House Value')
    
# Create a scatter plot
fig = px.scatter_mapbox(
    housing, 
    lat="latitude", 
    lon="longitude", 
    color="median_house_value", 
    size="median_house_value", 
    color_continuous_scale='viridis', 
    size_max=15, 
    zoom=3
)
fig.update_layout(mapbox_style="carto-positron")

# Add the predicted house location with a distinct color and legend
fig.add_trace(px.scatter_mapbox(
    predicted_house, 
    lat="latitude", 
    lon="longitude", 
    color="PredictedValue", 
    size="PredictedValue", 
    color_continuous_scale=[[0, 'red'], [1, 'red']], 
    size_max=15
).data[0])

st.plotly_chart(fig, use_container_width=True)

st.write("---")

# Select relevant features for clustering
features_for_clustering = housing[['longitude', 'latitude']]

# Perform k-means clustering
kmeans = KMeans(n_clusters=5, random_state=42)
housing['district'] = kmeans.fit_predict(features_for_clustering)

# Group by the fictitious 'district' column and calculate the median house value
district_median_values = housing.groupby('district')['median_house_value'].median()

# Identify the top districts by median house value
top_districts = district_median_values.nlargest(5)

# Assign colors to each district for the map
color_discrete_map = {0: 'blue', 1: 'green', 2: 'red', 3: 'purple', 4: 'orange'}

# Create a scatter mapbox for the top districts
fig_districts = go.Figure()

for district in top_districts.index:
    district_data = housing[housing['district'] == district]
    fig_districts.add_trace(
        go.Scattermapbox(
            lat=district_data['latitude'],
            lon=district_data['longitude'],
            mode='markers',
            marker=dict(size=9, color=color_discrete_map[district]),
            name=f"District {district}"
        )
    )

# Update layout to set mapbox properties
fig_districts.update_layout(
    title='Map of Top Districts',
    mapbox=dict(
        style="carto-positron",
        zoom=4,
        center=dict(lat=district_data['latitude'].mean(), lon=district_data['longitude'].mean())
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    legend_title_text='District'
)

# Geographical Distribution of Top Districts
st.markdown('### Geographical Distribution of Top Districts')

# Create two columns for the map and the table
col1, col2 = st.columns([3, 1])

with col1:
    st.plotly_chart(fig_districts, use_container_width=True)

with col2:
    # Create and display a table of top districts
    top_districts_table = top_districts.reset_index()
    top_districts_table.columns = ['District', 'Median House Value']
    st.write(top_districts)
