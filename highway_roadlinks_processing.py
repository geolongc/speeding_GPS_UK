#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 19:29:28 2024

@author: longpc
"""


#%%
# extract roadlink data
import pandas as pd
import geopandas as gpd

# Define the region of interest
# region = "London"
# region = "WestEngland"
# region = "Oxford"
# region = "Cambridge"
# region = "Newcastle"
# region = "Edinburgh"
# region = "Glasgow"
# region = "WestYorkshire"
# region = "SouthYorkshire"
# region = "Manchester"
# region = "Cardiff"
# region = "Liverpool"
# region = "WestMidlands"

# Define input path and layer names
InputPath = f"/Users/longpc/Documents/Leeds/data/geocompass/digidown/highways_x/{region}/Roads.gpkg"
RoadLink = "RoadLink"
RoadNode = "RoadNode"

# Read the GeoPackage layers
gdflink = gpd.read_file(filename=InputPath, layer=RoadLink)
gdfnode = gpd.read_file(filename=InputPath, layer=RoadNode)

# Print the CRS (Coordinate Reference System) and shape of the dataframes
print(gdflink.crs)
print(gdfnode.crs)
print(gdflink.shape)
print(gdfnode.shape)

# Filter links by geometry type
gdflink = gdflink[gdflink.geometry.type != 'MultiLineString']
print(gdflink.shape)

# Select relevant columns
gdflink = gdflink[['TOID', 'localid', 'startnode_href', 'endnode_href', 'directionality_title', 
                   'routehierarchy', 'formofway', 'trunkroad', 'primaryroute', 'length', 
                   'formspartof_role', 'averagewidth', 'minimumwidth', 'geometry']]

gdfnode = gdfnode[['TOID', 'localid', 'formofroadnode_title', 'geometry']]

# Define output path and layer names
OutPath = f"/Users/longpc/Documents/Leeds/data/geocompass/digidown/highways_x/{region}/Roads1.gpkg"
OutLink = "RoadLink"
OutNode = "RoadNode"

# Save the filtered data to the GeoPackage file
gdflink.to_file(OutPath, layer=OutLink, driver='GPKG')
gdfnode.to_file(OutPath, layer=OutNode, driver='GPKG')



#%%
# output roadlink1 data for sDNA calculation
import pandas as pd
import geopandas as gpd

# Define the region of interest
# region = "London"
# region = "WestEngland"
# region = "Oxford"
# region = "Cambridge"
# region = "Newcastle"
# region = "Edinburgh"
# region = "Glasgow"
# region = "WestYorkshire"
# region = "SouthYorkshire"
# region = "Manchester"
# region = "Cardiff"
# region = "Liverpool"
# region = "WestMidlands"

# Define input path and layer names
InputPath = f"/Users/longpc/Documents/Leeds/data/geocompass/digidown/highways_x/{region}/Roads.gpkg"
RoadLink = "RoadLink"
RoadNode = "RoadNode"

# Read the GeoPackage layers
gdflink = gpd.read_file(filename=InputPath, layer=RoadLink)
gdfnode = gpd.read_file(filename=InputPath, layer=RoadNode)

# Print the CRS (Coordinate Reference System) and shape of the dataframes
print(gdflink.crs)
print(gdfnode.crs)
print(gdflink.shape)
print(gdfnode.shape)

# Select relevant columns
# gdflink = gdflink[['TOID', 'localid', 'startnode_href', 'endnode_href', 'directionality_title', 'routehierarchy', 'geometry']]
# gdfnode = gdfnode[['TOID', 'localid', 'formofroadnode_title', 'geometry']]

# Get unique valid nodes
valid_nodes = gdfnode['TOID'].unique()

# Filter links by valid nodes
gdflink1 = gdflink[(gdflink['startnode_href'].isin(valid_nodes)) & (gdflink['endnode_href'].isin(valid_nodes))].reset_index(drop=True)
print(gdflink1.shape)

# Get unique valid start and end nodes
valid_startnodes = gdflink1['startnode_href'].unique()
valid_endnodes = gdflink1['endnode_href'].unique()

# Filter nodes by valid start and end nodes
gdfnode1 = gdfnode[(gdfnode['TOID'].isin(valid_startnodes)) | (gdfnode['TOID'].isin(valid_endnodes))].reset_index(drop=True)
print(gdfnode1.shape)

# Filter links by geometry type
gdflink1 = gdflink1[gdflink1.geometry.type != 'MultiLineString']
print(gdflink1.shape)

speedlimit_df = pd.read_csv("/Users/longpc/Documents/Leeds/data/geocompass/digidown/speed id/Speed_Limit.csv")
print(speedlimit_df.columns)

gdflink1 = gdflink1.merge(speedlimit_df, left_on='TOID', right_on='roadLinkID', how='left')
print(gdflink1.columns)
print(gdflink1.shape)

# Define output path and layer names
OutPath = f"/Users/longpc/Documents/Leeds/data/geocompass/digidown/highways_x/{region}/Roads1.gpkg"
OutLink = "RoadLink1"
OutNode = "RoadNode1"

# Save the filtered data to the GeoPackage file
gdflink1.to_file(OutPath, layer=OutLink, driver='GPKG')
gdfnode1.to_file(OutPath, layer=OutNode, driver='GPKG')



# %%
# sDNA data preparation for directionality
import os
import geopandas as gpd
from shapely.geometry import Point, LineString

# Preprocess road links to handle directionality
def preprocess_road_links(gdflink):
    """Reverse directionality of road links where needed."""
    mask = gdflink['directionality_title'] == 'in opposite direction'
    gdflink.loc[mask, ['startnode_href', 'endnode_href']] = gdflink.loc[mask, ['endnode_href', 'startnode_href']].values 
    gdflink.loc[mask, 'geometry'] = gdflink.loc[mask, 'geometry'].apply(lambda geom: LineString(geom.coords[::-1]))
    gdflink.loc[mask, 'directionality_title'] = 'in direction' 
    return gdflink

# Define the list of regions
regions = ["London", "WestEngland", "Oxford", "Cambridge", "Newcastle",
           "Edinburgh", "Glasgow", "WestYorkshire", "SouthYorkshire",
           "Manchester", "Cardiff", "Liverpool", "WestMidlands"]

# Base path to the shapefiles
base_path = "/Users/longpc/Documents/Leeds/data/geocompass/highways_sDNA_new/"

# Loop through each region
for region in regions:
    # Set file paths for road link data 
    RoadPath = f"/Users/longpc/Documents/Leeds/data/geocompass/digidown/highways_x/{region}/Roads1.gpkg"
    RoadLink = "RoadLink1"

    # Load the road link data
    roadlink = gpd.read_file(filename=RoadPath, layer=RoadLink)
    roadlink = roadlink[['TOID', 'directionality_title', 'startnode_href', 'endnode_href', 'geometry']]

    roadlink = preprocess_road_links(roadlink)
    print(roadlink['directionality_title'].unique())

    # Mapping dictionary for 'direction_title'
    mapping = {
        'in direction': 1,
        'both directions': 0
    }

    # Creating a new column 'oneway' based on 'direction_title'
    roadlink['oneway'] = roadlink['directionality_title'].map(mapping)

    outpath = os.path.join(base_path, region, "Roads_sDNA.gpkg")
    outlayer = "RoadLink1"

    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    roadlink.to_file(outpath, layer=outlayer, driver='GPKG')
    print(f"Saved {region} to {outpath}")



# %%
# sDNA result data join
import geopandas as gpd
import os

# Define the list of regions
regions = ["London", "WestEngland", "Oxford", "Cambridge", "Newcastle",
           "Edinburgh", "Glasgow", "WestYorkshire", "SouthYorkshire",
           "Manchester", "Cardiff", "Liverpool", "WestMidlands"]


# Base path to the shapefiles
base_path = "/Users/longpc/Documents/Leeds/data/geocompass/highways_sDNA_new/"

# Loop through each region
for region in regions:
    # Define paths to the shapefiles
    path_links = os.path.join(base_path, region, f"{region}_VEHICLE.shp")
    path_toid = os.path.join(base_path, region, "Roads_sDNA.gpkg")
    layer_toid = "RoadLink1"

    # Read the shapefiles
    gdf_links = gpd.read_file(path_links)
    print(gdf_links.shape)
    print(gdf_links.crs)
    gdf_toid = gpd.read_file(filename=path_toid, layer=layer_toid)
    print(gdf_toid.crs)
    gdf_toid = gdf_toid[['TOID', 'geometry']]

    # Ensure both GeoDataFrames use the same CRS
    if gdf_links.crs != gdf_toid.crs:
        gdf_toid = gdf_toid.to_crs(gdf_links.crs)

    # Convert road links to points by interpolating at 50% of the line length
    gdf_points = gdf_links.copy()
    gdf_points['geometry'] = gdf_points.geometry.interpolate(0.5, normalized=True)
    print(gdf_points.shape)

    # Perform a spatial join to combine the point data with the 'TOID' data
    # Assuming 'TOID' column exists in the gdf_toid DataFrame
    joined_gdf = gpd.sjoin_nearest(gdf_points, gdf_toid, how='left', distance_col="distance_sdna")
    print(joined_gdf.shape)
    print(joined_gdf['TOID'].nunique())

    # Remove any duplicate matches based on the left index (gdf_points)
    # This step ensures that each point only joins to one 'TOID', even if there were multiple equal distances
    joined_gdf = joined_gdf.drop_duplicates(subset='TOID')
    print(joined_gdf.shape)
    print(joined_gdf['TOID'].nunique())

    # Define the output path for the current region
    outlayer = "sDNA_join_toid"

    # Save the result for the current region
    joined_gdf.to_file(path_toid, layer=outlayer, driver='GPKG')

    # Optional: print to confirm the save
    print(f"Saved {region} to {path_toid}")









# %%
