Europe Airbnb Geospatial Exploratory Data Analysis (EDA):


This repository contains a comprehensive geospatial and statistical analysis of European Airbnb markets using Python. The analysis investigates key factors influencing rental prices, guest satisfaction, and locational attributes across major European cities.

Project Overview:

The European Airbnb dataset encompasses information on listings across ten major European cities (Amsterdam, Athens, Barcelona, Budapest, Lisbon, London, Paris, Rome, and Vienna). This project performs data consolidation, cleaning, outlier handling, and exploratory data analysis to answer key business and geospatial questions.

Key Objectives:

Price Discrepancies: 

Analyze how rental prices vary across cities, room types, and between weekdays and weekends.

Guest Satisfaction: 

Identify cities and property types with lower average guest satisfaction ratings and explore contributing factors.

Location Correlation: 

Determine how distance to the city center and transport links (metro stations) correlate with guest ratings and pricing.

Index Analysis: 

Evaluate the concentration of attractions and restaurants across cities and their relationship with business-oriented listings.

Technical Specifications & Methodology:

The analysis is broken down into modular steps utilizing popular scientific computing and data visualization libraries.

1.Data Ingestion & Consolidation:

Iteratively loads individual city datasets (separated into weekday and weekend subsets).Applies city labels and weekend indicators derived from file paths.Concatenates individual datasets into a single master data frame.

2.Data Cleaning & Transformation:

Standardizes city naming conventions via string manipulation and os operations.Drops uninformative columns (e.g., Unnamed: 0, attr_index_norm, rest_index_norm).Cleans and casts data types (converts boolean categorical columns from numerical types).Removes exact duplicates.

3.Outlier Treatment:

IQR (Interquartile Range) Method: Identifies and isolates listings whose prices fall outside the bounds defined by:$$[Q_1 - 1.5 \times \text{IQR}, \, Q_3 + 1.5 \times \text{IQR}]$$

4.Geospatial and Statistical AnalysisHeatmaps: 

Generates interactive Folium visualizations highlighting the density and pricing intensity across Europe.Correlation Analysis: Calculates Pearson correlation coefficients between economic and spatial indices.Comparative Statistics: Summarizes the distributions of pricing and distances to transport nodes via grouped box and whisker plots.

Exploratory Data Analysis Insights:

The code provides insights into a number of key analytical questions:

Pricing Insights: 

The data reveals that while prices remain right-skewed, removing outliers brings variance to light. Listings designated for business purposes exhibit different structural distributions compared to typical consumer listings.

Satisfaction Analysis: 

Barcelona, Lisbon, London, and Paris show guest satisfaction ratings below the overall European average. Single rooms and weekday bookings show marginal differences compared to weekends.

Geospatial Clustering: C

ities like Rome, Paris, and Barcelona lead in Attraction and Restaurant Indices, meaning they are located closer to popular tourist amenities.