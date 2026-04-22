import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_palette("Set2")
import os
from tabulate import tabulate
import folium
from folium.plugins import HeatMap
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# ==============================================================================
# 1. DATA INGESTION & CONSOLIDATION
# ==============================================================================

csv_urls = [
    "data/amsterdam_weekdays.csv",
    "data/amsterdam_weekends.csv",
    "data/athens_weekdays.csv",
    "data/athens_weekends.csv",
    "data/barcelona_weekdays.csv",
    "data/barcelona_weekends.csv",
    "data/berlin_weekdays.csv",
    "data/berlin_weekends.csv",
    "data/budapest_weekdays.csv",
    "data/budapest_weekends.csv",
    "data/lisbon_weekdays.csv",
    "data/lisbon_weekends.csv",
    "data/london_weekdays.csv",
    "data/london_weekends.csv",
    "data/paris_weekdays.csv",
    "data/paris_weekends.csv",
    "data/rome_weekdays.csv",
    "data/rome_weekends.csv",
    "data/vienna_weekdays.csv",
    "data/vienna_weekends.csv",
]

dfs = []
for url in csv_urls:
  df = pd.read_csv(url)
  df['city'] = url.split('/')[-1].split('_')[0].capitalize()
  if url.endswith("days.csv"):
    df['is_weekend'] = False
  else:
    df['is_weekend'] = True
  dfs.append(df)

original_data = pd.concat(dfs, ignore_index=True)
print(original_data.head())
print(original_data.info())

# ==============================================================================
# 2. DATA CLEANING & TRANSFORMATION
# ==============================================================================

cleaned_data = original_data.copy()

# Extracting city name from file path
# Option A: Using pandas string operations (Easiest)
cleaned_data['city'] = cleaned_data['city'].str.split('\\').str[-1]

# Option B: Using the os library (More robust)
cleaned_data['city'] = cleaned_data['city'].apply(lambda x: os.path.basename(x))

# This will turn 'vienna' into 'Vienna', 'london' into 'London', etc.
cleaned_data['city'] = cleaned_data['city'].str.capitalize()

# Removing unnecessary columns
cleaned_data.drop(columns=['Unnamed: 0', 'attr_index_norm', 'rest_index_norm'], inplace=True)
cleaned_data = cleaned_data.reset_index(drop=True)

# Rename the columns
cleaned_data.rename(columns={'realSum': 'price', 'dist': 'centr_dist'}, inplace=True)

# Remove the duplicate columns
cleaned_data.drop_duplicates(inplace=True)

# Check if there's any missing values
print(cleaned_data.isnull().sum())

# Convert 'multi' and 'biz' into boolean columns
cleaned_data['multi'] = cleaned_data['multi'].astype(bool)
cleaned_data['biz'] = cleaned_data['biz'].astype(bool)
print(cleaned_data.info)

# ==============================================================================
# 3. INITIAL EXPLORATORY DATA ANALYSIS (EDA)
# ==============================================================================

# Count the number of listings per city
counts = cleaned_data.groupby(['city']).size()

# Plot the pie chart
plt.figure(figsize=(10, 6))
plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90, counterclock=False)

# Customize the plot
plt.title('Percentage of Listing Numbers', y=1.05)
plt.axis('equal')

plt.show()

# Geospatial Heatmap Generation
map = folium.Map(location=[50.0, 10.0], zoom_start=4)

# Prepare data for the heatmap, using price as the weight
heat_data = [[row['lat'], row['lng'], row['price']] for index, row in cleaned_data.iterrows()]

# Create and add heatmap layer
HeatMap(
    heat_data,
    gradient={0.2: 'blue', 1: 'blue'},  # Single color for heatmap
    radius=15,  # Adjust radius for heat intensity
    blur=10,    # Adjust blur to spread the heat
    max_zoom=1
).add_to(map)

# ==============================================================================
# 4. OUTLIER DETECTION & REMOVAL (IQR METHOD)
# ==============================================================================

cities = cleaned_data['city'].unique()

# Plot the density plot
plt.figure(figsize=(12, 6))
for city in cities:
    city_data = cleaned_data[cleaned_data['city'] == city]['price']
    sns.kdeplot(city_data, label=city, alpha=0.5)

# Customize the plot
plt.xlabel('Price')
plt.ylabel('Density')
plt.title('Price Distribution by City')
plt.legend(title='City')

plt.show()

# Plot the box plot for price for each city
plt.figure(figsize=(10, 6))
sns.boxplot(x='city', y='price', data=cleaned_data)

# Customize the plot
plt.title('Box Plot of Price for Each City')
plt.xlabel('City')
plt.ylabel('Price')

plt.show()

city_groups = cleaned_data.groupby('city')['price']
outlier_indices = []

#---------Identify outliers-----------

for city, prices in city_groups:
    # Calculate Q1 (25th percentile) and Q3 (75th percentile)
    Q1 = prices.quantile(0.25)
    Q3 = prices.quantile(0.75)
    IQR = Q3 - Q1  # Interquartile Range

    # Define bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Identify outlier indices for the city
    city_outliers_indices = cleaned_data[(cleaned_data['city'] == city) & ((cleaned_data['price'] < lower_bound) | (cleaned_data['price'] > upper_bound))].index

    outlier_indices.extend(city_outliers_indices)

# Create a dataframe for outliers
outliers = cleaned_data.loc[outlier_indices]

# Remove outliers from the original dataset
cleaned_data_no_outliers = cleaned_data.drop(index=outlier_indices)

print("Outliers:")
print(outliers)
print("\nDataFrame without Outliers:")
print(cleaned_data_no_outliers)
print(outliers.shape)

print(outliers.groupby('city').size().reset_index(name='number of outliers'))

# ==============================================================================
# 5. Q1: ANALYSIS OF RENTAL PRICE DIFFERENCES AMONG EUROPEAN CITIES
# ==============================================================================

cities = cleaned_data_no_outliers['city'].unique()

# Plot the density plot
plt.figure(figsize=(12, 6))
for city in cities:
    city_data = cleaned_data_no_outliers[cleaned_data_no_outliers['city'] == city]['price']
    sns.kdeplot(city_data, label=city, alpha=0.5)

# Customize the plot
plt.xlabel('Price')
plt.ylabel('Density')
plt.title('Price Distribution by City')
plt.legend(title='City')

plt.show()

# After removing the outliers, the price distributions of each city are still right-skewed but not as extreme.

# Plot the box plot
plt.figure(figsize=(10, 6))
sns.boxplot(x='city', y='price', data=cleaned_data_no_outliers)

# Customize the plot
plt.title('Box Plot of Rental Price by City')
plt.xlabel('City')
plt.ylabel('Price')

plt.show()

# Calculate descriptive statistics for price grouped by city

# Force PyCharm to show all columns and not wrap the text
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

price_summary = cleaned_data_no_outliers.groupby('city')['price'].describe().round(2)
print(price_summary)

#Box plot of rental price by room type

# Plot the box plot
plt.figure(figsize=(10, 6))
sns.boxplot(x='city', y='price', hue='room_type', data=cleaned_data_no_outliers)

# Customize the plot
plt.title('Box Plot of Rental Price by Room Type')
plt.xlabel('City')
plt.ylabel('Price')
plt.legend(title='Room type')

plt.show()

# Box plot of rental price for business purposes and non-business purposes

# Plot the box plot
plt.figure(figsize=(10, 6))
sns.boxplot(x='city', y='price', hue='biz', data=cleaned_data_no_outliers)

# Customize the plot
plt.title('Box Plot of Rental Price for Business Purposes and Non-Business Purposes')
plt.xlabel('City')
plt.ylabel('Price')
handles, _ = plt.gca().get_legend_handles_labels()
plt.legend(title=None, handles=handles, labels=['Non-business purpose', 'Business purpose'], bbox_to_anchor=(1.05, 1), loc='upper left')

plt.show()

# Box plot of rental price for weekdays and weekends

# Plot the box plot
plt.figure(figsize=(10, 6))
sns.boxplot(x='city', y='price', hue='is_weekend', data=cleaned_data_no_outliers)

# Customize the plot
plt.title('Box Plot of Rental Price for Weekdays and Weekends')
plt.xlabel('City')
plt.ylabel('Price')
handles, _ = plt.gca().get_legend_handles_labels()
plt.legend(title=None, handles=handles, labels=['Weekday','Weekend'], bbox_to_anchor=(1.05, 1), loc='upper left')

plt.show()

# ============================================================================================
# 6. Q2: WHICH CITIES AND PROPERTY TYPED HAVE LOWER AVERAGE GUEST SATISFACTION ANALYSIS
# ============================================================================================

# Calculate the average guest satisfaction rating by city
mean_satisfaction_ratings = cleaned_data_no_outliers.groupby(['city'])['guest_satisfaction_overall'].mean().reset_index()
mean_satisfaction_ratings['guest_satisfaction_overall'] = mean_satisfaction_ratings['guest_satisfaction_overall'].round()

# Plot the bar chart
plt.figure(figsize=(12, 8))
ax = sns.barplot(x='city', y='guest_satisfaction_overall', data=mean_satisfaction_ratings, errorbar=None)

# Customize the plot
for container in ax.containers:
    ax.bar_label(container, fmt='%d', padding=3)
plt.title('Average Guest Satisfaction Rating by City')
plt.xlabel('City')
plt.ylabel('Average Guest Satisfaction Rating')
plt.xticks(rotation=0, ha='center')

# Add a line to represent the overall average rating
overall_average_rating = cleaned_data_no_outliers['guest_satisfaction_overall'].mean()
plt.axhline(overall_average_rating, color='red', linestyle='--', label=f'Overall Average Rating: {overall_average_rating:.2f}')
plt.text(x=5, y=overall_average_rating + 3,
         s=f'Overall Avg: {overall_average_rating:.2f}', color='red')

plt.show()

# According to the bar chart, Barcelona, Lisbon, London and Paris have lower average guest satisfaction ratings, which are below the overall average ratings for all cities.

# Calculate the average guest satisfaction rating by room type
mean_satisfaction_ratings = cleaned_data_no_outliers.groupby(['city', 'room_type'])['guest_satisfaction_overall'].mean().reset_index()
mean_satisfaction_ratings['guest_satisfaction_overall'] = mean_satisfaction_ratings['guest_satisfaction_overall'].round()

# Plot the bar chart
plt.figure(figsize=(12, 8))
ax = sns.barplot(x='city', y='guest_satisfaction_overall', hue='room_type', data=mean_satisfaction_ratings, errorbar=None)

# Customize the plot
for container in ax.containers:
    ax.bar_label(container, fmt='%d', padding=3)
plt.title('Average Guest Satisfaction Rating by Room Type')
plt.xlabel('City')
plt.ylabel('Average Guest Satisfaction Rating')
plt.xticks(rotation=0, ha='center')
plt.legend(title='Room Type', bbox_to_anchor=(1, 0.2), loc='upper right')

plt.show()

# Calculate the average guest satisfaction rating by business/non-business purposes
mean_satisfaction_ratings = cleaned_data.groupby(['city', 'biz'])['guest_satisfaction_overall'].mean().reset_index()
mean_satisfaction_ratings['guest_satisfaction_overall'] = mean_satisfaction_ratings['guest_satisfaction_overall'].round()

# Plot the bar chart
plt.figure(figsize=(12, 8))
ax = sns.barplot(x='city', y='guest_satisfaction_overall', hue='biz', data=mean_satisfaction_ratings, errorbar=None)

# Customize the plot
for container in ax.containers:
    ax.bar_label(container, fmt='%d', padding=3)
plt.title('Average Guest Satisfaction Rating by Business and Non-business Purposes')
plt.xlabel('City')
plt.ylabel('Average Guest Satisfaction Rating')
plt.xticks(rotation=0, ha='center')
handles, _ = plt.gca().get_legend_handles_labels()
plt.legend(title=None, handles=handles, labels=['Non-business purpose', 'Business purpose'], bbox_to_anchor=(1, 0.15), loc='upper right')

plt.show()

# Another interesting observation is that listings for business purposes apparently have lower satisfaction ratings than those for non-business purposes, which requires further investigation.

# Calculate the average guest satisfaction rating by
mean_satisfaction_ratings = cleaned_data.groupby(['city', 'multi'])['guest_satisfaction_overall'].mean().reset_index()
mean_satisfaction_ratings['guest_satisfaction_overall'] = mean_satisfaction_ratings['guest_satisfaction_overall'].round()

# Plot the bar chart
plt.figure(figsize=(12, 8))
ax = sns.barplot(x='city', y='guest_satisfaction_overall', hue='multi', data=mean_satisfaction_ratings, errorbar=None)

# Customize the plot
for container in ax.containers:
    ax.bar_label(container, fmt='%d', padding=3)
plt.title('Average Guest Satisfaction Rating by Multiple rooms and Single Room')
plt.xlabel('City')
plt.ylabel('Average Guest Satisfaction Rating')
plt.xticks(rotation=0, ha='center')
handles, _ = plt.gca().get_legend_handles_labels()
plt.legend(title=None, handles=handles, labels=['Single room', 'Multiple rooms'], bbox_to_anchor=(1, 0.15), loc='upper right')

plt.show()

# Calculate the avearge guest satisfaction rating by weekdays and weekends
mean_satisfaction_ratings = cleaned_data.groupby(['city', 'is_weekend'])['guest_satisfaction_overall'].mean().reset_index()
mean_satisfaction_ratings['guest_satisfaction_overall'] = mean_satisfaction_ratings['guest_satisfaction_overall'].round()

# Plot the bar chart
plt.figure(figsize=(12, 8))
ax = sns.barplot(x='city', y='guest_satisfaction_overall', hue='is_weekend', data=mean_satisfaction_ratings, errorbar=None)

# Customize the plot
for container in ax.containers:
    ax.bar_label(container, fmt='%d', padding=3)
plt.title('Average Guest Satisfaction Rating by Weekdays and Weekends')
plt.xlabel('City')
plt.ylabel('Average Guest Satisfaction Rating')
plt.xticks(rotation=0, ha='center')
handles, _ = plt.gca().get_legend_handles_labels()
plt.legend(title=None, handles=handles, labels=['Weekdays', 'Weekends'], bbox_to_anchor=(1, 0.15), loc='upper right')

plt.show()

# ======================================================================================
# 7. Q3: HOW TO DO INDEX AND DISTANCE ATTRIBUTES CORRELATE GUEST SATISFACTION RATING?
# ======================================================================================

# Plot the heatmap
plt.figure(figsize=(16, 14))
sns.heatmap(cleaned_data_no_outliers[['price','centr_dist','metro_dist','attr_index','rest_index']].corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Heatmap of Correlations between Index/Distance Attributes and Guest Satisfaction Rating')

plt.show()

# The correlation coefficients between price and the index and distance attributes are all below 0.25, suggesting that there is no strong linear relationship between price and these variables.

# ======================================================================================
# 8. Q4: WHICH CITY HAS A HIGHER ATTRACTION INDEX AND RESTAURANT INDEX ?
# ======================================================================================

# Calculate the average attraction index by business/non-business purposes in each city
mean_index = cleaned_data_no_outliers.groupby(['city', 'biz'])['attr_index'].mean().reset_index()
mean_index['attr_index'] = mean_index['attr_index'].round()

# Plot the bar chart
plt.figure(figsize=(12, 8))
ax = sns.barplot(x='city', y='attr_index', hue='biz', data=mean_index, errorbar=None)

# Customize the plot
for container in ax.containers:
    ax.bar_label(container, fmt='%d', padding=3)
plt.title('Average Attraction Index for Business and Non-Business Purposes in Each City')
plt.xlabel('City')
plt.ylabel('Average Attraction Index')
plt.xticks(rotation=0, ha='center')
handles, _ = plt.gca().get_legend_handles_labels()
plt.legend(title=None, handles=handles, labels=['Non-business purpose', 'Business purpose'], bbox_to_anchor=(1, 0.15), loc='upper right')

# Add a line to represent the overall average index
overall_average_index = cleaned_data_no_outliers['attr_index'].mean()
plt.axhline(overall_average_index, color='red', linestyle='--', label=f'Overall Attraction Index: {overall_average_index:.2f}')
plt.text(x=3, y=overall_average_index + 5,
         s=f'Overall Avg: {overall_average_index:.2f}', color='red')

plt.show()

# Calculate the average restaurant index by business/non-business purposes in each city
mean_index = cleaned_data_no_outliers.groupby(['city', 'biz'])['rest_index'].mean().reset_index()
mean_index['rest_index'] = mean_index['rest_index'].round()

# Plot the bar chart
plt.figure(figsize=(12, 8))
ax = sns.barplot(x='city', y='rest_index', hue='biz', data=mean_index, errorbar=None)

# Customize the plot
for container in ax.containers:
    ax.bar_label(container, fmt='%d', padding=3)
plt.title('Average Restaurant Index for Business and Non-Business Purposes in Each City')
plt.xlabel('City')
plt.ylabel('Average Restaurant Index')
plt.xticks(rotation=0, ha='center')
handles, _ = plt.gca().get_legend_handles_labels()
plt.legend(title=None, handles=handles, labels=['Non-business purpose', 'Business purpose'], bbox_to_anchor=(1, 0.1), loc='upper right')

# Add a line to represent the overall average rating
overall_average_index = cleaned_data_no_outliers['rest_index'].mean()
plt.axhline(overall_average_index, color='red', linestyle='--', label=f'Overall Restaurant Index: {overall_average_index:.2f}')
plt.text(x=3, y=overall_average_index + 10,
         s=f'Overall Avg: {overall_average_index:.2f}', color='red')

plt.show()

# Rome, Paris, and Barcelona have the top 3 highest average attraction and restaurant indices, suggesting that the listings in these cities are closer to popular attractions and restaurants. Also, it's quite intriguing that listings for business purposes show higher levels of attraction and restaurant indices compared to non-business listings.

# Plot the regression lines between attraction index and restaurant index
sns.lmplot(x="attr_index", y="rest_index", hue="city", data=cleaned_data_no_outliers,
      scatter=False, markers="o", palette="Accent", aspect=1.5, height=6)
plt.title("Correlation between Attraction Index and Restaurant Index by City")
plt.show()

# Calculate the correlation coefficients between attraction index and restaurant index for each city

# Clean the city names first (so they aren't long file paths)
cleaned_data_no_outliers['city'] = cleaned_data_no_outliers['city'].str.split('\\').str[-1].str.capitalize()

# Calculate the correlation
correlation_per_city = cleaned_data_no_outliers.groupby('city').apply(
    lambda x: x['attr_index'].corr(x['rest_index']),
    include_groups=False
).reset_index()

correlation_per_city.columns = ['City', 'Correlation Coefficient']

# 3. Format the numbers and sort
# Keep them as floats for sorting, format them during the print
correlation_per_city = correlation_per_city.sort_values(by='Correlation Coefficient', ascending=False)

# 4. Print using tabulate for the console
print("\n--- Correlation: Attractions vs Restaurants ---")
print(tabulate(correlation_per_city, headers='keys', tablefmt='psql', showindex=False, floatfmt=".4f"))

# =========================================================================================
# 9. Q5: WHICH CITY HAS A HIGHER CONCENTRATION OF LISTINGS NEAR THE CLOSEST METRO STATTION?
# =========================================================================================

# Create the box plot
plt.figure(figsize=(10, 6))
sns.boxplot(x='city', y='metro_dist', data=cleaned_data_no_outliers)

# Customize the plot
plt.title('Box Plot of Distances from the Nearest Metro Station by city')
plt.xlabel('City')
plt.ylabel('Distance from the Nearest Metro Station')

plt.show()

# Calculate descriptive statistics for distance from the nearest metro station grouped by city
# 1. Clean city names (to remove the C:\path\ names)
cleaned_data_no_outliers['city'] = cleaned_data_no_outliers['city'].str.split('\\').str[-1].str.capitalize()

# 2. Calculate the descriptive statistics
metro_dist_summary = cleaned_data_no_outliers.groupby('city')['metro_dist'].describe().round(2)

# 3. Print to PyCharm Console
print("\n--- Descriptive Statistics: Distance to Metro ---")
print(tabulate(metro_dist_summary, headers='keys', tablefmt='psql'))


# Create the box plot
plt.figure(figsize=(10, 6))
sns.boxplot(x='city', y='metro_dist', hue='biz', data=cleaned_data_no_outliers)

# Customize the plot
plt.title('Box Plot of Distances from the Nearest Metro Station for Business and Non-Business Purposes')
plt.xlabel('City')
plt.ylabel('Distance from the Nearest Metro Station')
handles, _ = plt.gca().get_legend_handles_labels()
plt.legend(title=None, handles=handles, labels=['Non-business purpose', 'Business purpose'], bbox_to_anchor=(1, 1), loc='upper right')

plt.show()
