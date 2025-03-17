This is a respository to demonstrate how to use GPS trajectory data with snapped points and speed information, to investigate speeding behaviours across road links in British cities.

**Code description:**

**Python**

* _compass_preprocessing_trajectory_data.py_  is used to expand raw trajectory vectors to GPS points, save data to PostgreSQL, and filter data in British city regions

* _map_matching_GPS_highway_roadlink.py_  is used to conduct map-matching between GPS trajectory/points and highway road links using gotrackit package in python

* _compass_postprocessing_mapmatching.py_  is used to postprecess map-matching results to extract GPS point with matched road link id

* _summary statistics of GPS and highway road links.py_  is used to do summary statistics of GPS and highway road link level data using matched results

* _highway_roadlinks_processing.py_  is used to preprocess highway road links, and use the data to conduct spatial design network analysis (sDNA tool)

* _osmnx_download_features.ipynb_  is used to download OSM engineering featutes such as traffic calmings, crossings, junctions, traffic signals, speed cameras

* _process_osm_features.py_  is used to construct road network and links into multigraph in python and count OSM enginnering features for each road link within 100 meters

Package versions: OSMnx 1.9


**R**

* _read model data.R_  is used to read data in R for plot and modelling

* _plot road link-level speeding.R_  is used to plot road link level speeding counts across road network in R

* _nb model for speeding.R_  is used to implement negative binominal model for speeding behaviours, network metrics, and engineering features

* _export model results.R_  is used to format and export negative binominal results in R

* _plot heatmap for model results.R_  is used to read structured model results and plot heatmap for incidence rate ratio across models


Package versions:  sf dplyr glmmTMB



**Software and package versions**

* Sparial Design Network Analysis (sDNA), version 4.1.1

* QGIS 3.22.5


