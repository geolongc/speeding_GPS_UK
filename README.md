This is a respository to demonstrate how to use GPS trajectory data with snapped points and speed information, to investigate speeding behaviours across road links in British cities.

Code description:

Python

compass_preprocessing_trajectory_data.py is used to expand raw trajectory vectors to GPS points, save data to PostgreSQL, and filter data in British city regions

map_matching_GPS_highway_roadlink.py is used to conduct map-matching between GPS trajectory/points and highway road links using gotrackit package in python

compass_postprocessing_mapmatching.py is used to postprecess map-matching results to extract GPS point with matched road link id

summary statistics of GPS and highway road links.py is used to do summary statistics of GPS and highway road link level data using matched results

highway_roadlinks_processing.py is used to preprocess highway road links, and use the data to conduct spatial design network analysis (sDNA tool)

osmnx_download_features.ipynb is used to download OSM engineering featutes such as traffic calmings, crossings, junctions, traffic signals, speed cameras

process_osm_features.py is used to construct road network and links into multigraph in python and count OSM enginnering features for each road link within 100 meters


R

read model data.R is used to read data in R for plot and modelling

plot road link-level speeding.R is used to plot road link level speeding counts across road network in R

nb model for speeding.R is used to implement negative binominal model for speeding behaviours, network metrics, and engineering features

export model results.R is used to format and export negative binominal results in R

plot heatmap for model results.R is used to read structured model results and plot heatmap for incidence rate ratio across models
