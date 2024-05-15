import pandas as pd
from datetime import datetime
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator
import mplcursors


# Import filtered table from Global Footprint Network
df = pd.read_csv("Filtered_Earth_Overshoot_Days_2024.csv")
df = df.rename(columns = {"Total Ecological Footprint (Consumption)" : "footprint_consumption", 
                          "Total Ecological Footprint (Production)" : "footprint_production",
                          "Number of Earths required" : "num_earths",
                          "Official Overshoot Day" : "official_overshoot_day"
                          })

# country_footprint = total ecological footprint global hectares per person (consumption)

# Function to calculate overshoot day
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


## Plotting Graph: Overshoot Days by Consumption v Number of Earths

# Colourmap for the regions
region_colours = {
    'North America': 'mediumseagreen',
    'Central America/Caribbean': 'lightseagreen',
    'South America': 'teal',
    'EU-27': 'mediumblue',
    'Other Europe': 'cornflowerblue',
    'Africa': 'maroon',
    'Middle East/Central Asia': 'red',
    'Asia-Pacific': 'orange'
}

# Create a figure and axis
fig, ax = plt.subplots(figsize=(18, 6))

# Create a separate bar plot for each region:
for region, color in region_colours.items():
    region_data = df[df['Region'] == region]
    bars = ax.bar(region_data['overshoot_day_consumption'], region_data['num_earths'], color=color,
                  label=f"{region} - Overshoot Day: {region_data['overshoot_day_consumption'].mean().strftime('%d %B %Y')}")

# Titles and labels
ax.set_title("Country Overshoot Days (by Consumption) and Number of Earths")
ax.set_xlabel("Country Overshoot Day")
ax.set_ylabel("Number of Earths")

# Format x-axis
# Format x-axis ticks as months
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))
# Set x-axis tick labels to display every 2 months
ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=2))
# Add ticks to indicate year changes
ax.xaxis.set_major_locator(mdates.YearLocator())
# Display minor ticks as year labels
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
# Adjust position of year labels to be below month labels
ax.tick_params(axis='x', which='major', pad=15)
# Set x-axis limits to start from the origin
start_date = datetime(2024, 1, 1)
ax.set_xlim(start_date, df['overshoot_day_consumption'].max())

# Format y-axis
ax.yaxis.set_major_locator(MultipleLocator(2))
ax.grid(which='major', axis='x')

# Hide top spine
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Function to format hover annotations
def format_annotation(sel):
    index = sel.target.index
    country = df.iloc[index]['Country']
    overshoot_day = df.iloc[index]['overshoot_day_consumption'].strftime('%d %B %Y')
    num_earths = df.iloc[index]['num_earths']
    return f"Country: {country}\nOvershoot Day: {overshoot_day}\nNumber of Earths: {num_earths:.2f}"

# Add hover annotations using mplcursors
mplcursors.cursor(hover=True).connect("add", format_annotation)

# Display legend based on average overshoot day by region
# get legend handles and labels
handles, labels = ax.get_legend_handles_labels()
# sort legend labels based on the average overshoot day
sorted_labels = sorted(labels, key=lambda x: datetime.strptime(x.split(': ')[-1].strip(), '%d %B %Y'))
sorted_handles = [handles[labels.index(label)] for label in sorted_labels]
# Recreate legend with sorted labels and handles
legend = ax.legend(sorted_handles, sorted_labels, loc='upper center', bbox_to_anchor=(0.5, -0.2), frameon=False, ncol=2)

# save figure
fig.savefig('EarthOvershoot Days 2024 by Consumption.png', bbox_inches='tight')

plt.show()
