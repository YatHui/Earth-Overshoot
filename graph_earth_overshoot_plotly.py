import pandas as pd
from datetime import datetime
from datetime import datetime
import dash
from dash import dcc, html, Input, Output, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objs as go


# Import filtered table from Global Footprint Network
df = pd.read_csv("Filtered_Earth_Overshoot_Days_2024.csv")
df = df.rename(columns = {"Total Ecological Footprint (Consumption)" : "footprint_consumption", 
                          "Total Ecological Footprint (Production)" : "footprint_production",
                          "Number of Earths required" : "num_earths",
                          "Official Overshoot Day" : "official_overshoot_day"
                          })

# country_footprint = total ecological footprint global hectares per person (consumption)

# Fuction to calculate overshoot day
def OvershootDayConsumption(footprint_consumption):
         global_footprint = 1.51 # 2024 figure
         day_num = int(366*(global_footprint/footprint_consumption))
        
        # accounting for countries using less than 1 year of resources
         if day_num > 366: # running into 2025
                 day_num -= 366 # leap year in 2024
                 if day_num > 365: # running into 2026
                         day_num -= 365
                         date = datetime.strptime("2026-" + str(day_num), "%Y-%j").strftime("%Y-%m-%d")                         
                 else:
                         date = datetime.strptime("2025-" + str(day_num), "%Y-%j").strftime("%Y-%m-%d")
         else:   
                date = datetime.strptime("2024-" + str(day_num), "%Y-%j").strftime("%Y-%m-%d")
         return date


# Apply function row-wise to calculate overshoot_day
df["overshoot_day_consumption"] = df["footprint_consumption"].apply(OvershootDayConsumption)

# Calculating difference between calculated overshoot days and official overshoot days
# Convert 'overshoot_day' column to datetime format for consistency
df['overshoot_day_consumption'] = pd.to_datetime(df['overshoot_day_consumption'])

# Convert 'official_overshoot_day' column to datetime format, handle NaN values
df['official_overshoot_day'] = pd.to_datetime(df['official_overshoot_day'], errors='coerce')

# Perform subtraction and extract the number of days
df['difference'] = (df['overshoot_day_consumption'] - df['official_overshoot_day']).dt.days


## Plotting graph on Plotly


# Define the colours based on regions
region_colours = {
    'North America' : 'mediumseagreen',
    'Central America/Caribbean' : 'lightseagreen',
    'South America' : 'teal',
    'EU-27' : 'mediumblue',
    'Other Europe' : 'cornflowerblue',    
    'Africa' : 'maroon',
    'Middle East/Central Asia' : 'red',
    'Asia-Pacific' : 'orange'
}


# Initialise the Dash app
app = dash.Dash(__name__)

# Define a function to map region names to colors
def map_region_to_color(region):
    return region_colours.get(region, 'gray')  # Default color is gray for unknown regions

# Define a callback to print hover annotations
@app.callback(
    Output('hover-data', 'children'),
    [Input('earth-overshoot-graph', 'hoverData')]
)
def display_hover_data(hoverData):
    if hoverData is not None:
        index = hoverData['points'][0]['pointIndex']
        country = df.iloc[index]['Country']
        region = df.iloc[index]['Region']
        overshoot_day = df.iloc[index]['overshoot_day_consumption'].strftime('%Y-%m-%d')
        num_earths = df.iloc[index]['num_earths']
        return (
            f"Country: {country}<br>"
            f"Region: {region}<br>"
            f"Overshoot Day: {overshoot_day}<br>"
            f"Number of Earths: {num_earths}"
        )
    return ""

# Define the layout of the Dash app
app.layout = html.Div([
    dcc.Graph(
        id='earth-overshoot-graph',
        figure={
            'data': [
                {
                    'x': df['overshoot_day_consumption'],
                    'y': df['num_earths'],
                    'type' : 'bar',
                    'text': [f"Country: {country}<br>"
                             f"Region: {region}<br>"
                             f"Overshoot Day: {overshoot_day}<br>"
                             f"Number of Earths: {num_earths}"
                             for country, region, overshoot_day, num_earths in
                             zip(df['Country'], df['Region'], df['overshoot_day_consumption'].dt.strftime('%Y-%m-%d'), df['num_earths'])],
                    'hoverinfo': 'text',  # Display custom text on hover
                    'name': df['Region'], # Set the legend labels
                    'marker': {'color': [map_region_to_color(region) for region in df['Region']]}
                }
            ],
            'layout': {
            'title': 'Earth Overshoot 2024',
            'xaxis': {'title': 'Overshoot Day'},
            'yaxis': {'title': 'Number of Earths'},
            'legend': {'orientation': 'h', 'x': 0, 'y': -0.2}  # Position legend at the bottom
            }
        }
    ),
    html.Div(id='hover-data')
])


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
