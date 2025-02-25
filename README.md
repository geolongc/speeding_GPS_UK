This is a respository to demonstrate how to use GPS trajectory data with snapped points and speed information, to investigate speeding behaviours across road links in British cities.

Code description:

Python

compass_preprocessing_trajectory_data.py is used to expand raw trajectory vectors to GPS points, save data to PostgreSQL, and filter data in British city regions

osmnx_download_features.ipynb is used to download OSM engineering featutes such as traffic calmings, crossings, junctions, traffic signals, speed cameras


R

export model results.R is used to format and export negative binominal results in R
