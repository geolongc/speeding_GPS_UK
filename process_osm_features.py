#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 21:49:28 2024

@author: longpc
"""


#%%  use RoadLink
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os

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

InputPath = f"/Users/longpc/Documents/Leeds/data/geocompass/digidown/highways_x/{region}/Roads1.gpkg"
RoadLink = "RoadLink"

gdflink = gpd.read_file(filename=InputPath, layer=RoadLink)

# print(gdflink.head())
# print(gdflink.dtypes)
print(gdflink.columns)
print(gdflink.shape)

print(gdflink['directionality_title'].unique())
print(gdflink['routehierarchy'].unique())
print(gdflink['formofway'].unique())
print(gdflink['trunkroad'].unique())
print(gdflink['primaryroute'].unique())
print(gdflink['formspartof_role'].unique())



#%%  analyse OSM Tags
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os

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
region = "WestMidlands"

PathLink = f"/Users/longpc/Documents/Leeds/data/geocompass/digidown/highways_x/{region}/Roads1.gpkg"
LayerLink = "RoadLink"

gdflink = gpd.read_file(filename=PathLink, layer=LayerLink)
print(gdflink.crs)

# analyse OSM Tags, traffic calming
PathCalming = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmdown/{region}/tags_trafficcalming.gpkg"
LayerCalming = "tags_trafficcalming"

gdf_calming = gpd.read_file(filename=PathCalming, layer=LayerCalming)
gdf_calming = gdf_calming[gdf_calming.geometry.type == 'Point']

print(gdf_calming.columns)
print(gdf_calming.shape)
print(gdf_calming['traffic_calming'].value_counts())

gdf_calming = gdf_calming.to_crs(gdflink.crs)
gdf_calming = gdf_calming[['element_type', 'osmid', 'traffic_calming', 'direction', \
    'crossing', 'crossing:island', 'crossing:markings', 'highway', 'geometry']]

gdf_calming1 = gpd.sjoin_nearest(
    gdf_calming, 
    gdflink[['TOID', 'geometry']], 
    how="left", 
    distance_col="distance_join"
)

gdf_calming2 = gdf_calming1[gdf_calming1['distance_join'] <= 20]
gdf_calming2 = gdf_calming2.reset_index(drop=True)
print(gdf_calming2.shape)

# Define the main categories you want to keep as is
main_categories_calming = ['hump', 'cushion', 'table', 'bump', 'island', 'choker']

# Function to categorize traffic calming types
def categorize_traffic_calming(value):
    if value in main_categories_calming:
        return value
    else:
        return 'other_calming'

# Apply the function to create the new column
gdf_calming2['traffic_calming_new'] = gdf_calming2['traffic_calming'].apply(categorize_traffic_calming)
print(gdf_calming2['traffic_calming_new'].value_counts())

OutPathCalming = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro/{region}/trafficcalming.gpkg"
OutLayerCalming = "trafficcalming"
os.makedirs(os.path.dirname(OutPathCalming), exist_ok=True)
gdf_calming2.to_file(OutPathCalming, layer=OutLayerCalming, driver='GPKG')


# analyse OSM Tags, traffic sign, give way
PathGiveway = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmdown/{region}/tags_trafficsign.gpkg"
LayerGiveway = "tags_trafficsign"

gdf_signgiveway = gpd.read_file(filename=PathGiveway, layer=LayerGiveway)

gdf_signgiveway = gdf_signgiveway[gdf_signgiveway.geometry.type == 'Point']
print(gdf_signgiveway.columns)
print(gdf_signgiveway['highway'].value_counts())

gdf_signgiveway = gdf_signgiveway[['element_type', 'osmid', 'highway', 'geometry']]
gdf_signgiveway = gdf_signgiveway.rename(columns={'highway': 'sign_giveway'})
gdf_signgiveway = gdf_signgiveway.to_crs(gdflink.crs)

gdf_signgiveway1 = gpd.sjoin_nearest(
    gdf_signgiveway, 
    gdflink[['TOID', 'geometry']], 
    how="left", 
    distance_col="distance_join"
)

gdf_signgiveway2 = gdf_signgiveway1[gdf_signgiveway1['distance_join'] <= 20]
gdf_signgiveway2 = gdf_signgiveway2.reset_index(drop=True)
print(gdf_signgiveway2.shape)

main_categories_sign = ['give_way']

def categorize_sign(value):
    if value in main_categories_sign:
        return value
    else:
        return 'other_sign'

gdf_signgiveway2['sign_giveway_new'] = gdf_signgiveway2['sign_giveway'].apply(categorize_sign)
print(gdf_signgiveway2['sign_giveway_new'].value_counts())

OutPathSign = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro/{region}/sign_giveway.gpkg"
OutLayerSign = "sign_giveway"
os.makedirs(os.path.dirname(OutPathSign), exist_ok=True)
gdf_signgiveway2.to_file(OutPathSign, layer=OutLayerSign, driver='GPKG')


#  analyse OSM Tags, crossing
PathCrossing = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmdown/{region}/tags_crossing.gpkg"
LayerCrossing = "tags_crossing"

gdf_crossing = gpd.read_file(filename=PathCrossing, layer=LayerCrossing)

gdf_crossing = gdf_crossing[gdf_crossing.geometry.type == 'Point']
print(gdf_crossing.columns)
print(gdf_crossing['crossing'].value_counts())

gdf_crossing = gdf_crossing.to_crs(gdflink.crs)
gdf_crossing = gdf_crossing[['element_type', 'osmid', 'crossing', 'crossing:island', 'highway', \
    'kerb', 'tactile_paving', 'crossing:markings', 'lit', 'button_operated', 'crossing:signals', 'crossing_ref', 'geometry']]

gdf_crossing1 = gpd.sjoin_nearest(
    gdf_crossing, 
    gdflink[['TOID', 'geometry']], 
    how="left", 
    distance_col="distance_join"
)

gdf_crossing2 = gdf_crossing1[gdf_crossing1['distance_join'] <= 20]
gdf_crossing2 = gdf_crossing2.reset_index(drop=True)
print(gdf_crossing2.shape)

main_categories_crossing = ['traffic_signals', 'uncontrolled', 'unmarked', 'marked']

def categorize_crossing(value):
    if value in main_categories_crossing:
        return value
    else:
        return 'other_crossing'

gdf_crossing2['crossing_new'] = gdf_crossing2['crossing'].apply(categorize_crossing)
print(gdf_crossing2['crossing_new'].value_counts())

OutPathCrossing = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro/{region}/crossing.gpkg"
OutLayerCrossing = "crossing"
os.makedirs(os.path.dirname(OutPathCrossing), exist_ok=True)
gdf_crossing2.to_file(OutPathCrossing, layer=OutLayerCrossing, driver='GPKG')


# analyse OSM Tags, junction
PathJunction = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmdown/{region}/tags_junction.gpkg"
LayerJunction = "tags_junction"

gdf_junction = gpd.read_file(filename=PathJunction, layer=LayerJunction)

gdf_junction_point = gdf_junction[gdf_junction.geometry.type == 'Point']
# print(gdf_junction_point.columns)
# print(gdf_junction_point['highway'].value_counts())

gdf_junction_point = gdf_junction_point[['element_type', 'osmid', 'highway', 'geometry']]
gdf_junction_point = gdf_junction_point.rename(columns={'highway': 'junction'})
gdf_junction_point = gdf_junction_point.to_crs(gdflink.crs)

gdf_junction_line = gdf_junction[gdf_junction.geometry.type == 'LineString']
# print(gdf_junction_line.columns)
# print(gdf_junction_line['junction'].value_counts())

gdf_junction_line = gdf_junction_line[['element_type', 'osmid', 'junction', 'geometry']]

gdf_junction_line = gdf_junction_line.to_crs(gdflink.crs)
gdf_line_to_point = gdf_junction_line.copy()
gdf_line_to_point['geometry'] = gdf_line_to_point['geometry'].centroid

OutPathLinetopoint = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmdown/{region}/tags_junction_linetopoint.gpkg"
OutLayerLinetopoint = "junction_linetopoint"
os.makedirs(os.path.dirname(OutPathLinetopoint), exist_ok=True)
gdf_line_to_point.to_file(OutPathLinetopoint, layer=OutLayerLinetopoint, driver='GPKG')

gdf_junction_combined = pd.concat([gdf_junction_point, gdf_line_to_point], ignore_index=True)
gdf_junction_combined = gdf_junction_combined.reset_index(drop=True)
print(gdf_junction_combined['junction'].value_counts())

gdf_junction_combined1 = gpd.sjoin_nearest(
    gdf_junction_combined, 
    gdflink[['TOID', 'geometry']], 
    how="left", 
    distance_col="distance_join"
)

gdf_junction_combined2 = gdf_junction_combined1[gdf_junction_combined1['distance_join'] <= 20]
gdf_junction_combined2 = gdf_junction_combined2.reset_index(drop=True)
print(gdf_junction_combined2.shape)

main_categories_junction = ['turning_circle', 'roundabout', 'mini_roundabout', \
    'circular', 'motorway_junction', 'turning_loop']

def categorize_junction(value):
    if value in main_categories_junction:
        return value
    else:
        return 'other_junction'

gdf_junction_combined2['junction_new'] = gdf_junction_combined2['junction'].apply(categorize_junction)
print(gdf_junction_combined2['junction_new'].value_counts())

OutPathJunction = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro/{region}/junction.gpkg"
OutLayerJunction = "junction"
os.makedirs(os.path.dirname(OutPathJunction), exist_ok=True)
gdf_junction_combined2.to_file(OutPathJunction, layer=OutLayerJunction, driver='GPKG')


# analyse OSM Tags, speedcamera
PathCamera = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmdown/{region}/tags_speedcamera.gpkg"
LayerCamera = "tags_speedcamera"

gdf_speedcamera = gpd.read_file(filename=PathCamera, layer=LayerCamera)

gdf_speedcamera = gdf_speedcamera[gdf_speedcamera.geometry.type == 'Point']
print(gdf_speedcamera.columns)
print(gdf_speedcamera['highway'].value_counts())

gdf_speedcamera = gdf_speedcamera[['element_type', 'osmid', 'highway', 'maxspeed', 'geometry']]
gdf_speedcamera = gdf_speedcamera.rename(columns={'highway': 'camera'})
gdf_speedcamera = gdf_speedcamera.to_crs(gdflink.crs)

gdf_speedcamera1 = gpd.sjoin_nearest(
    gdf_speedcamera, 
    gdflink[['TOID', 'geometry']], 
    how="left", 
    distance_col="distance_join"
)

gdf_speedcamera2 = gdf_speedcamera1[gdf_speedcamera1['distance_join'] <= 20]
gdf_speedcamera2 = gdf_speedcamera2.reset_index(drop=True)
print(gdf_speedcamera2.shape)

main_categories_camera = ['speed_camera']

def categorize_camera(value):
    if value in main_categories_camera:
        return value
    else:
        return 'other_camera'

gdf_speedcamera2['camera_new'] = gdf_speedcamera2['camera'].apply(categorize_camera)
print(gdf_speedcamera2['camera_new'].value_counts())

OutPathCamera = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro/{region}/speedcamera.gpkg"
OutLayerCamera = "speedcamera"
os.makedirs(os.path.dirname(OutPathCamera), exist_ok=True)
gdf_speedcamera2.to_file(OutPathCamera, layer=OutLayerCamera, driver='GPKG')


# analyse OSM Tags, traffic signals
PathSignal = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmdown/{region}/tags_trafficsignal.gpkg"
LayerSignal = "tags_trafficsignal"

gdf_trafficsignal = gpd.read_file(filename=PathSignal, layer=LayerSignal)

gdf_trafficsignal = gdf_trafficsignal[gdf_trafficsignal.geometry.type == 'Point']
print(gdf_trafficsignal.columns)
print(gdf_trafficsignal['highway'].value_counts())
print(gdf_trafficsignal['traffic_signals'].value_counts())

gdf_trafficsignal = gdf_trafficsignal[['element_type', 'osmid', 'highway', 'geometry']]
gdf_trafficsignal = gdf_trafficsignal.rename(columns={'highway': 'signal'})
gdf_trafficsignal = gdf_trafficsignal.to_crs(gdflink.crs)

gdf_trafficsignal1 = gpd.sjoin_nearest(
    gdf_trafficsignal, 
    gdflink[['TOID', 'geometry']], 
    how="left", 
    distance_col="distance_join"
)

gdf_trafficsignal2 = gdf_trafficsignal1[gdf_trafficsignal1['distance_join'] <= 20]
gdf_trafficsignal2 = gdf_trafficsignal2.reset_index(drop=True)
print(gdf_trafficsignal2.shape)

main_categories_signal = ['traffic_signals']

def categorize_signal(value):
    if value in main_categories_signal:
        return value
    else:
        return 'other_signal'

gdf_trafficsignal2['signal_new'] = gdf_trafficsignal2['signal'].apply(categorize_signal)
print(gdf_trafficsignal2['signal_new'].value_counts())

OutPathSignal = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro/{region}/trafficsignal.gpkg"
OutLayerSignal = "trafficsignal"
os.makedirs(os.path.dirname(OutPathSignal), exist_ok=True)
gdf_trafficsignal2.to_file(OutPathSignal, layer=OutLayerSignal, driver='GPKG')










#%%  analyse OSM Tags, crossing island
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os

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

PathLink = f"/Users/longpc/Documents/Leeds/data/geocompass/digidown/highways_x/{region}/Roads1.gpkg"
LayerLink = "RoadLink"

gdflink = gpd.read_file(filename=PathLink, layer=LayerLink)
print(gdflink.crs)

#  analyse OSM Tags, crossing
PathCrossing = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmdown/{region}/tags_crossing.gpkg"
LayerCrossing = "tags_crossing"

gdf_crossing = gpd.read_file(filename=PathCrossing, layer=LayerCrossing)

gdf_crossing = gdf_crossing[gdf_crossing.geometry.type == 'Point']
print(gdf_crossing.columns)
print(gdf_crossing['crossing'].value_counts())

gdf_crossing = gdf_crossing.to_crs(gdflink.crs)
gdf_crossing = gdf_crossing[['element_type', 'osmid', 'crossing', 'crossing:island', 'highway', 'geometry']]

gdf_crossing1 = gpd.sjoin_nearest(
    gdf_crossing, 
    gdflink[['TOID', 'geometry']], 
    how="left", 
    distance_col="distance_join"
)

gdf_crossing2 = gdf_crossing1[gdf_crossing1['distance_join'] <= 20]
gdf_crossing2 = gdf_crossing2.reset_index(drop=True)
print(gdf_crossing2.shape)

gdf_crossing2['crossing_island'] = gdf_crossing2['crossing:island']
print(gdf_crossing2['crossing_island'].value_counts())

gdf_crossing_island = gdf_crossing2[gdf_crossing2['crossing_island'] == 'yes']
print(gdf_crossing_island.shape[0])
print(gdf_crossing_island['crossing'].value_counts())

OutPathCrossing = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect/{region}/crossing_island.gpkg"
OutLayerCrossing = "crossing_island"
os.makedirs(os.path.dirname(OutPathCrossing), exist_ok=True)
gdf_crossing_island.to_file(OutPathCrossing, layer=OutLayerCrossing, driver='GPKG')











# finally used and correct codes
#%%  analyse OSM Tags, undirected, snapped
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os

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
region = "WestMidlands"

PathLink = f"/Users/longpc/Documents/Leeds/data/geocompass/digidown/highways_x/{region}/Roads1.gpkg"
LayerLink = "RoadLink"

gdflink = gpd.read_file(filename=PathLink, layer=LayerLink)
print(gdflink.crs)

# analyse OSM Tags, traffic calming
PathCalming = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmdown/{region}/tags_trafficcalming.gpkg"
LayerCalming = "tags_trafficcalming"

gdf_calming = gpd.read_file(filename=PathCalming, layer=LayerCalming)
gdf_calming = gdf_calming[gdf_calming.geometry.type == 'Point']

print(gdf_calming.columns)
print(gdf_calming.shape)
print(gdf_calming['traffic_calming'].value_counts())

gdf_calming = gdf_calming.to_crs(gdflink.crs)
gdf_calming = gdf_calming[['element_type', 'osmid', 'traffic_calming', 'direction', \
    'crossing', 'crossing:island', 'crossing:markings', 'highway', 'geometry']]

gdf_calming1 = gpd.sjoin_nearest(
    gdf_calming, 
    gdflink[['TOID', 'geometry']], 
    how="left", 
    distance_col="distance_join"
)

gdf_calming2 = gdf_calming1[gdf_calming1['distance_join'] <= 20]
gdf_calming2 = gdf_calming2.reset_index(drop=True)
print(gdf_calming2.shape)

# Define the main categories you want to keep as is
main_categories_calming = ['hump', 'cushion', 'table', 'bump', 'island', 'choker']

# Function to categorize traffic calming types
def categorize_traffic_calming(value):
    if value in main_categories_calming:
        return value
    else:
        return 'other_calming'

# Apply the function to create the new column
gdf_calming2['traffic_calming_new'] = gdf_calming2['traffic_calming'].apply(categorize_traffic_calming)
print(gdf_calming2['traffic_calming_new'].value_counts())

OutPathCalming = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/trafficcalming.gpkg"
OutLayerCalming = "trafficcalming"
os.makedirs(os.path.dirname(OutPathCalming), exist_ok=True)
gdf_calming2.to_file(OutPathCalming, layer=OutLayerCalming, driver='GPKG')


#  analyse OSM Tags, crossing
PathCrossing = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmdown/{region}/tags_crossing.gpkg"
LayerCrossing = "tags_crossing"

gdf_crossing = gpd.read_file(filename=PathCrossing, layer=LayerCrossing)

gdf_crossing = gdf_crossing[gdf_crossing.geometry.type == 'Point']
print(gdf_crossing.columns)
print(gdf_crossing['crossing'].value_counts())

gdf_crossing = gdf_crossing.to_crs(gdflink.crs)
gdf_crossing = gdf_crossing[['element_type', 'osmid', 'crossing', 'crossing:island', 'highway', \
    'kerb', 'tactile_paving', 'crossing:markings', 'lit', 'button_operated', 'crossing:signals', 'crossing_ref', 'geometry']]

gdf_crossing1 = gpd.sjoin_nearest(
    gdf_crossing, 
    gdflink[['TOID', 'geometry']], 
    how="left", 
    distance_col="distance_join"
)

gdf_crossing2 = gdf_crossing1[gdf_crossing1['distance_join'] <= 20]
gdf_crossing2 = gdf_crossing2.reset_index(drop=True)
print(gdf_crossing2.shape)

main_categories_crossing = ['traffic_signals', 'uncontrolled', 'unmarked', 'marked']

def categorize_crossing(value):
    if value in main_categories_crossing:
        return value
    else:
        return 'other_crossing'

gdf_crossing2['crossing_new'] = gdf_crossing2['crossing'].apply(categorize_crossing)
print(gdf_crossing2['crossing_new'].value_counts())

OutPathCrossing = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/crossing.gpkg"
OutLayerCrossing = "crossing"
os.makedirs(os.path.dirname(OutPathCrossing), exist_ok=True)
gdf_crossing2.to_file(OutPathCrossing, layer=OutLayerCrossing, driver='GPKG')


gdf_crossing2['crossing_island'] = gdf_crossing2['crossing:island']
print(gdf_crossing2['crossing_island'].value_counts())

gdf_crossing_island = gdf_crossing2[gdf_crossing2['crossing_island'] == 'yes']
print(gdf_crossing_island.shape[0])
print(gdf_crossing_island['crossing'].value_counts())

OutPathCrossing = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/crossing_island.gpkg"
OutLayerCrossing = "crossing_island"
os.makedirs(os.path.dirname(OutPathCrossing), exist_ok=True)
gdf_crossing_island.to_file(OutPathCrossing, layer=OutLayerCrossing, driver='GPKG')


# analyse OSM Tags, junction
PathJunction = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmdown/{region}/tags_junction.gpkg"
LayerJunction = "tags_junction"

gdf_junction = gpd.read_file(filename=PathJunction, layer=LayerJunction)

gdf_junction_point = gdf_junction[gdf_junction.geometry.type == 'Point']
# print(gdf_junction_point.columns)
# print(gdf_junction_point['highway'].value_counts())

gdf_junction_point = gdf_junction_point[['element_type', 'osmid', 'highway', 'geometry']]
gdf_junction_point = gdf_junction_point.rename(columns={'highway': 'junction'})
gdf_junction_point = gdf_junction_point.to_crs(gdflink.crs)

gdf_junction_line = gdf_junction[gdf_junction.geometry.type == 'LineString']
# print(gdf_junction_line.columns)
# print(gdf_junction_line['junction'].value_counts())

gdf_junction_line = gdf_junction_line[['element_type', 'osmid', 'junction', 'geometry']]

gdf_junction_line = gdf_junction_line.to_crs(gdflink.crs)
gdf_line_to_point = gdf_junction_line.copy()
gdf_line_to_point['geometry'] = gdf_line_to_point['geometry'].centroid

OutPathLinetopoint = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmdown/{region}/tags_junction_linetopoint.gpkg"
OutLayerLinetopoint = "junction_linetopoint"
os.makedirs(os.path.dirname(OutPathLinetopoint), exist_ok=True)
gdf_line_to_point.to_file(OutPathLinetopoint, layer=OutLayerLinetopoint, driver='GPKG')

gdf_junction_combined = pd.concat([gdf_junction_point, gdf_line_to_point], ignore_index=True)
gdf_junction_combined = gdf_junction_combined.reset_index(drop=True)
print(gdf_junction_combined['junction'].value_counts())

gdf_junction_combined1 = gpd.sjoin_nearest(
    gdf_junction_combined, 
    gdflink[['TOID', 'geometry']], 
    how="left", 
    distance_col="distance_join"
)

gdf_junction_combined2 = gdf_junction_combined1[gdf_junction_combined1['distance_join'] <= 20]
gdf_junction_combined2 = gdf_junction_combined2.reset_index(drop=True)
print(gdf_junction_combined2.shape)

main_categories_junction = ['turning_circle', 'roundabout', 'mini_roundabout', \
    'circular', 'motorway_junction', 'turning_loop']

def categorize_junction(value):
    if value in main_categories_junction:
        return value
    else:
        return 'other_junction'

gdf_junction_combined2['junction_new'] = gdf_junction_combined2['junction'].apply(categorize_junction)
print(gdf_junction_combined2['junction_new'].value_counts())

OutPathJunction = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/junction.gpkg"
OutLayerJunction = "junction"
os.makedirs(os.path.dirname(OutPathJunction), exist_ok=True)
gdf_junction_combined2.to_file(OutPathJunction, layer=OutLayerJunction, driver='GPKG')


# analyse OSM Tags, speedcamera
PathCamera = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmdown/{region}/tags_speedcamera.gpkg"
LayerCamera = "tags_speedcamera"

gdf_speedcamera = gpd.read_file(filename=PathCamera, layer=LayerCamera)

gdf_speedcamera = gdf_speedcamera[gdf_speedcamera.geometry.type == 'Point']
print(gdf_speedcamera.columns)
print(gdf_speedcamera['highway'].value_counts())

gdf_speedcamera = gdf_speedcamera[['element_type', 'osmid', 'highway', 'maxspeed', 'geometry']]
gdf_speedcamera = gdf_speedcamera.rename(columns={'highway': 'camera'})
gdf_speedcamera = gdf_speedcamera.to_crs(gdflink.crs)

gdf_speedcamera1 = gpd.sjoin_nearest(
    gdf_speedcamera, 
    gdflink[['TOID', 'geometry']], 
    how="left", 
    distance_col="distance_join"
)

gdf_speedcamera2 = gdf_speedcamera1[gdf_speedcamera1['distance_join'] <= 20]
gdf_speedcamera2 = gdf_speedcamera2.reset_index(drop=True)
print(gdf_speedcamera2.shape)

main_categories_camera = ['speed_camera']

def categorize_camera(value):
    if value in main_categories_camera:
        return value
    else:
        return 'other_camera'

gdf_speedcamera2['camera_new'] = gdf_speedcamera2['camera'].apply(categorize_camera)
print(gdf_speedcamera2['camera_new'].value_counts())

OutPathCamera = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/speedcamera.gpkg"
OutLayerCamera = "speedcamera"
os.makedirs(os.path.dirname(OutPathCamera), exist_ok=True)
gdf_speedcamera2.to_file(OutPathCamera, layer=OutLayerCamera, driver='GPKG')


# analyse OSM Tags, traffic signals
PathSignal = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmdown/{region}/tags_trafficsignal.gpkg"
LayerSignal = "tags_trafficsignal"

gdf_trafficsignal = gpd.read_file(filename=PathSignal, layer=LayerSignal)

gdf_trafficsignal = gdf_trafficsignal[gdf_trafficsignal.geometry.type == 'Point']
print(gdf_trafficsignal.columns)
print(gdf_trafficsignal['highway'].value_counts())
print(gdf_trafficsignal['traffic_signals'].value_counts())

gdf_trafficsignal = gdf_trafficsignal[['element_type', 'osmid', 'highway', 'geometry']]
gdf_trafficsignal = gdf_trafficsignal.rename(columns={'highway': 'signal'})
gdf_trafficsignal = gdf_trafficsignal.to_crs(gdflink.crs)

gdf_trafficsignal1 = gpd.sjoin_nearest(
    gdf_trafficsignal, 
    gdflink[['TOID', 'geometry']], 
    how="left", 
    distance_col="distance_join"
)

gdf_trafficsignal2 = gdf_trafficsignal1[gdf_trafficsignal1['distance_join'] <= 20]
gdf_trafficsignal2 = gdf_trafficsignal2.reset_index(drop=True)
print(gdf_trafficsignal2.shape)

main_categories_signal = ['traffic_signals']

def categorize_signal(value):
    if value in main_categories_signal:
        return value
    else:
        return 'other_signal'

gdf_trafficsignal2['signal_new'] = gdf_trafficsignal2['signal'].apply(categorize_signal)
print(gdf_trafficsignal2['signal_new'].value_counts())

OutPathSignal = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/trafficsignal.gpkg"
OutLayerSignal = "trafficsignal"
os.makedirs(os.path.dirname(OutPathSignal), exist_ok=True)
gdf_trafficsignal2.to_file(OutPathSignal, layer=OutLayerSignal, driver='GPKG')





# finally used and correct codes
# %%  analyse and count OSM Tags, within network distance, undirected road network, snap OSM tags to links
import os
import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
from functools import lru_cache
import time
from rtree import index

# Generate unique indices for all vertices (coordinates) and edges (TOIDs)
def generate_indices(gdflink):
    """
    Generates unique node indices for each coordinate (vertex) in the road network
    and edge indices for each TOID. Adds edge index to the GeoDataFrame.
    """
    # Generate edge indices for each TOID
    edge_indices = {toid: idx for idx, toid in enumerate(gdflink['TOID'].unique())}
    
    # Extract all coordinates (nodes) from the geometries
    nodes = pd.Series([coord for geom in gdflink.geometry for coord in geom.coords])
    unique_nodes = pd.Series(nodes.unique()).apply(tuple)
    
    # Generate node indices for each unique coordinate
    node_indices = {coord: idx for idx, coord in enumerate(unique_nodes)}
    
    # Add the edge indices to the GeoDataFrame
    gdflink['edge_id'] = gdflink['TOID'].map(edge_indices)

    return gdflink, node_indices, edge_indices

# Build a spatial index for the road links to optimize nearest neighbor searches
def build_spatial_index(gdflink):
    """Build a spatial index for road links."""
    spatial_idx = index.Index()
    for pos, line in enumerate(gdflink.geometry):
        spatial_idx.insert(pos, line.bounds)
    return spatial_idx

def get_nearest_link_and_snapped_point(gdf_point, gdflink, node_indices, buffer_size=30):
    """
    Find the nearest link ID and snapped point for each point in gdf_point using a spatial index
    to speed up the search process. A buffer is used to limit the candidates.

    Args:
    - gdf_point: GeoDataFrame of points (e.g., OSM tags).
    - gdflink: GeoDataFrame of road links.
    - node_indices: Dictionary mapping coordinates to node indices.
    - buffer_size: Size of buffer around each point to find candidate road links.

    Returns:
    - gdf_point_nearest: Updated GeoDataFrame with nearest link ID and snapped points.
    - node_indices: Updated dictionary with node indices.
    """
    nearest_results = []

    # Build a spatial index for road links
    spatial_idx = build_spatial_index(gdflink)

    # Iterate through each point and calculate the nearest link manually using the spatial index
    for point_idx, point_row in gdf_point.iterrows():
        point_geom = point_row.geometry
        nearest_distance = None
        nearest_link_id = None
        snapped_point = None
        snapped_node = None

        # Create a buffer around the point to limit the candidates
        point_buffer = point_geom.buffer(buffer_size)
        possible_matches_index = list(spatial_idx.intersection(point_buffer.bounds))
        possible_matches = gdflink.iloc[possible_matches_index]

        if not possible_matches.empty:
            # Calculate distances from point to all possible matching road segments
            distances_to_segments = possible_matches.geometry.apply(lambda geom: point_geom.distance(geom))
            nearest_idx = distances_to_segments.idxmin()

            # Get the nearest geometry and edge information using edge_indices
            nearest_geom = possible_matches.loc[nearest_idx].geometry
            nearest_link_id = possible_matches.loc[nearest_idx, 'edge_id']
            
            # Get the actual snapped point on the road link (nearest_geom)
            snapped_point_on_link, _ = nearest_points(nearest_geom, point_geom)

            # Calculate nearest distance to the link
            nearest_distance = point_geom.distance(snapped_point_on_link)

            # Set snapped_point to the actual snapped point on the road link
            snapped_point = snapped_point_on_link

            # Check if the snapped point is already a vertex of the link
            coords = list(nearest_geom.coords)
            if tuple(snapped_point.coords[0]) in coords:
                # If snapped point is already a vertex, use its corresponding node index
                snapped_node = node_indices.get(tuple(snapped_point.coords[0]))
            else:
                # If the snapped point is not already in the node index, add it as a new node
                snapped_node = len(node_indices)
                node_indices[tuple(snapped_point.coords[0])] = snapped_node
        else:
            # If no matches are found, handle it accordingly
            nearest_link_id = None
            snapped_point = None
            snapped_node = None
            nearest_distance = None

        # Store the results for this point (None for empty cases)
        nearest_results.append({
            'point_index': point_idx,
            'nearest_link_id': nearest_link_id,
            'snapped_point': snapped_point,
            'distance_to_link': nearest_distance,
            'nearest_node': snapped_node
        })

    # Convert the results to a DataFrame for easy merging with gdf_point
    nearest_df = pd.DataFrame(nearest_results)

    # Merge the nearest results back into the original gdf_point DataFrame
    gdf_point_nearest = gdf_point.merge(
        nearest_df[['point_index', 'nearest_link_id', 'nearest_node', 'distance_to_link', 'snapped_point']], 
        left_index=True, right_on='point_index', 
        how='left'
    )

    # Ensure snapped_point is already valid geometry (as you've confirmed it is)
    # print(gdf_point_nearest['snapped_point'])

    # Set 'snapped_point' as the active geometry column
    gdf_point_nearest = gdf_point_nearest.set_geometry('snapped_point', inplace=False)

    # Now drop the original 'geometry' column, which is not needed anymore
    gdf_point_nearest = gdf_point_nearest.drop(columns=['geometry'])

    # Ensure the CRS is set correctly if it's not already set
    gdf_point_nearest.set_crs(epsg=27700, inplace=True)  # Example for British National Grid

    # Return the updated gdf_point and node_indices
    return gdf_point_nearest, node_indices

def find_nearest_segment_index(coords, snapped_point):
    """
    Find the index of the segment in the original geometry that is closest to the snapped point.
    """
    nearest_index = -1
    nearest_distance = float('inf')
    
    for i in range(len(coords) - 1):
        segment = LineString([coords[i], coords[i + 1]])
        distance = segment.distance(snapped_point)
        
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_index = i
    
    return nearest_index

# Function to modify the gdflink by inserting snapped points into the road link geometries
def modify_gdflink_with_snapped_points(gdflink, gdf_point_nearest):
    """
    Modify gdflink by inserting snapped points as vertices within the corresponding road link geometries.
    """
    modified_links = []

    for idx, row in gdflink.iterrows():
        original_geom = row.geometry
        edge_id = row['edge_id']  # Refer to edge_id, not TOID
        
        # Find all snapped points for this edge_id (if any)
        snapped_points = gdf_point_nearest[gdf_point_nearest['nearest_link_id'] == edge_id]
        
        if snapped_points.empty:
            # No snapped points, keep the original geometry
            modified_links.append(original_geom)
        else:
            # Insert the snapped points into the original geometry
            coords = list(original_geom.coords)

            for _, snapped_row in snapped_points.iterrows():
                snapped_point = snapped_row['snapped_point']
                
                # Find the nearest segment in the geometry to insert the snapped point
                nearest_index = find_nearest_segment_index(coords, snapped_point)
                
                # Insert the snapped point into the geometry at the correct position
                coords.insert(nearest_index + 1, (snapped_point.x, snapped_point.y))
            
            # Create a new LineString with the updated coordinates
            new_geom = LineString(coords)
            modified_links.append(new_geom)

    # Replace the geometries in gdflink with the modified ones
    gdflink['geometry'] = modified_links

    return gdflink

# Function to create a graph from the modified road link data with key for each edge
def create_undirected_road_graph(gdflink, node_indices):
    """
    Create an undirected multigraph from the road link data, including all vertices.
    Each edge has a unique key based on the edge ID (TOID).
    """
    G = nx.MultiGraph()
    
    for idx, row in gdflink.iterrows():
        coords = list(row.geometry.coords)
        edge_id = row['edge_id']  # Use edge_id as the unique key for the edges
        
        for i in range(len(coords) - 1):
            u, v = tuple(coords[i]), tuple(coords[i + 1])
            node_u = node_indices[u]
            node_v = node_indices[v]
            distance = Point(u).distance(Point(v))
            edge_attributes = row.to_dict()
            edge_attributes['geometry'] = LineString([u, v])
            
            # Add the edge between consecutive vertices with a unique key (edge_id)
            G.add_edge(node_u, node_v, key=edge_id, length=distance, **edge_attributes)
    
    return G

# Function to cache the reachable nodes within a given distance in the network
@lru_cache(maxsize=None)
def get_reachable_nodes(G, node, distance):
    return nx.single_source_dijkstra_path_length(G, node, cutoff=distance, weight='length')

# Function to count the number of points at link level
def count_points_at_link_level(gdflink, gdf_point, type_column):
    link_column_total = f'{type_column}_counts'
    new_columns = {link_column_total: np.zeros(len(gdflink))}

    point_types = gdf_point[type_column].unique()

    for pt_type in point_types:
        new_columns[f'{pt_type}_counts'] = np.zeros(len(gdflink))

    for idx, row in gdflink.iterrows():
        key = row['edge_id']
        points_on_link = gdf_point[gdf_point['nearest_link_id'] == key]

        new_columns[link_column_total][idx] = len(points_on_link)

        for pt_type in point_types:
            type_count = points_on_link[points_on_link[type_column] == pt_type].shape[0]
            new_columns[f'{pt_type}_counts'][idx] = type_count

    return pd.DataFrame(new_columns, index=gdflink.index)

# Function to count the number of points and their types within a specified network distance
def count_points_within_distance(gdflink, gdf_point, G, node_indices, distance, type_column):
    distance_column_total = f'{type_column}_counts_{distance}m'
    new_columns = {distance_column_total: np.zeros(len(gdflink))}

    point_types = gdf_point[type_column].unique()
    for pt_type in point_types:
        new_columns[f'{pt_type}_counts_{distance}m'] = np.zeros(len(gdflink))

    for idx, row in gdflink.iterrows():
        u_coords = tuple(row.geometry.coords[0])
        v_coords = tuple(row.geometry.coords[-1])
        node_u = node_indices.get(u_coords)
        node_v = node_indices.get(v_coords)
        key = row['edge_id']

        reachable_nodes_u = get_reachable_nodes(G, node_u, distance)
        reachable_nodes_v = get_reachable_nodes(G, node_v, distance)
        reachable_nodes = set(reachable_nodes_u.keys()).union(set(reachable_nodes_v.keys()))

        points_in_distance = gdf_point[
            (gdf_point['nearest_link_id'] == key) |
            (gdf_point['nearest_node'].apply(lambda node: node is not None and node in reachable_nodes))
        ]

        new_columns[distance_column_total][idx] = len(points_in_distance)

        for pt_type in point_types:
            type_count = points_in_distance[points_in_distance[type_column] == pt_type].shape[0]
            new_columns[f'{pt_type}_counts_{distance}m'][idx] = type_count

    return pd.DataFrame(new_columns, index=gdflink.index)

# Start the timer to measure the execution time
start_time = time.time()

# Define the region of interest
# region = "London"
# region = "WestEngland"
# region = "Oxford"
# region = "Cambridge"
# region = "Newcastle"
# region = "Edinburgh"
# region = "Glasgow"
region = "WestYorkshire"
# region = "SouthYorkshire"
# region = "Manchester"
# region = "Cardiff"
# region = "Liverpool"
# region = "WestMidlands"

# Set file paths for road link data 
RoadPath = f"/Users/longpc/Documents/Leeds/data/geocompass/digidown/highways_x/{region}/Roads1.gpkg"
RoadLink = "RoadLink"

# Load the road link data
roadlink = gpd.read_file(filename=RoadPath, layer=RoadLink)
roadlink = roadlink[['TOID', 'directionality_title', 'geometry']]

# customize code for different point data
# Load traffic calming data
print(f"process region {region}")

roadlink_x_calming = roadlink.copy()
print(roadlink_x_calming.columns)

PathCalming = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/trafficcalming.gpkg"
LayerCalming = "trafficcalming"
gdf_calming = gpd.read_file(filename=PathCalming, layer=LayerCalming)

gdf_calming = gdf_calming[['osmid', 'traffic_calming', 'traffic_calming_new', 'TOID', 'distance_join', 'geometry']]
print(gdf_calming['traffic_calming_new'].value_counts())

# Generate indices and initialize the graph
roadlink_x_calming, node_indices_calming, edge_indices_calming = generate_indices(roadlink_x_calming)

# Snap points to the nearest edge and update the geometry
gdf_calming_nearest, node_indices_calming_updated = get_nearest_link_and_snapped_point(gdf_calming, roadlink_x_calming, node_indices_calming)
roadlink_x_calming_updated = modify_gdflink_with_snapped_points(roadlink_x_calming, gdf_calming_nearest)

# Create a graph from the modified road link data
G_calming = create_undirected_road_graph(roadlink_x_calming_updated, node_indices_calming_updated)

# Initialize an empty list to collect DataFrames
distance_dfs_calming = []

# Count traffic calming points directly on the link (not considering network distance)
direct_count_df_calming = count_points_at_link_level(roadlink_x_calming_updated, gdf_calming_nearest, type_column='traffic_calming_new')
print(direct_count_df_calming.columns)
distance_dfs_calming.append(direct_count_df_calming)

# Calculate the number of traffic calming points within various network distances
for dist in [50, 100, 200]:
    dist_df_calming = count_points_within_distance(roadlink_x_calming_updated, gdf_calming_nearest, G_calming, node_indices_calming_updated, distance=dist, type_column='traffic_calming_new')
    print(dist_df_calming.columns)
    distance_dfs_calming.append(dist_df_calming)
    get_reachable_nodes.cache_clear()

# Concatenate all the DataFrames (direct count and distances) with the roadlink_x_updated
roadlink_x_calming_count = pd.concat([roadlink_x_calming_updated] + distance_dfs_calming, axis=1)
print(roadlink_x_calming_count.columns)

# Save the final link data to a file
LinkPathCalming = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/roadlink_trafficcalming.gpkg"
LinklayerCalming = "roadlink_trafficcalming"
os.makedirs(os.path.dirname(LinkPathCalming), exist_ok=True)
roadlink_x_calming_count.to_file(LinkPathCalming, layer=LinklayerCalming, driver='GPKG')

PathCalmingSnapped = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/trafficcalming_snapped.gpkg"
LayerCalmingSnapped = "trafficcalming_snapped"
gdf_calming_nearest.to_file(PathCalmingSnapped, layer=LayerCalmingSnapped, driver='GPKG')

print(f"finished for region {region}, layer {LinklayerCalming}")

# End the timer and print the elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Total running time: {elapsed_time:.2f} seconds")


# Load crossing data
print(f"process region {region}")

roadlink_x_crossing = roadlink.copy()
print(roadlink_x_crossing.columns)

PathCrossing = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/crossing.gpkg"
LayerCrossing = "crossing"
gdf_crossing = gpd.read_file(filename=PathCrossing, layer=LayerCrossing)

gdf_crossing = gdf_crossing[['osmid', 'crossing', 'crossing_new', 'TOID', 'distance_join', 'geometry']]
print(gdf_crossing['crossing_new'].value_counts())

# Generate indices and initialize the graph
roadlink_x_crossing, node_indices_crossing, edge_indices_crossing = generate_indices(roadlink_x_crossing)

# Snap points to the nearest edge and update the geometry
gdf_crossing_nearest, node_indices_crossing_updated = get_nearest_link_and_snapped_point(gdf_crossing, roadlink_x_crossing, node_indices_crossing)
roadlink_x_crossing_updated = modify_gdflink_with_snapped_points(roadlink_x_crossing, gdf_crossing_nearest)

# Create a graph from the modified road link data
G_crossing = create_undirected_road_graph(roadlink_x_crossing_updated, node_indices_crossing_updated)

distance_dfs_crossing = []

direct_count_df_crossing = count_points_at_link_level(roadlink_x_crossing_updated, gdf_crossing_nearest, type_column='crossing_new')
print(direct_count_df_crossing.columns)
distance_dfs_crossing.append(direct_count_df_crossing)

for dist in [50, 100, 200]:
    dist_df_crossing = count_points_within_distance(roadlink_x_crossing_updated, gdf_crossing_nearest, G_crossing, node_indices_crossing_updated, distance=dist, type_column='crossing_new')
    print(dist_df_crossing.columns)
    distance_dfs_crossing.append(dist_df_crossing)
    get_reachable_nodes.cache_clear()

roadlink_x_crossing_count = pd.concat([roadlink_x_crossing_updated] + distance_dfs_crossing, axis=1)
print(roadlink_x_crossing_count.columns)

LinkPathCrossing = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/roadlink_crossing.gpkg"
LinklayerCrossing = "roadlink_crossing"
os.makedirs(os.path.dirname(LinkPathCrossing), exist_ok=True)
roadlink_x_crossing_count.to_file(LinkPathCrossing, layer=LinklayerCrossing, driver='GPKG')

PathCrossingSnapped = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/crossing_snapped.gpkg"
LayerCrossingSnapped = "crossing_snapped"
gdf_crossing_nearest.to_file(PathCrossingSnapped, layer=LayerCrossingSnapped, driver='GPKG')

print(f"finished for region {region}, layer {LinklayerCrossing}")

# End the timer and print the elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Total running time: {elapsed_time:.2f} seconds")


# Load crossing island data
print(f"process region {region}")

roadlink_x_island = roadlink.copy()
print(roadlink_x_island.columns)

PathIsland = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/crossing_island.gpkg"
LayerIsland = "crossing_island"
gdf_island = gpd.read_file(filename=PathIsland, layer=LayerIsland)

gdf_island = gdf_island[['osmid', 'crossing', 'crossing_island', 'TOID', 'distance_join', 'geometry']]
print(gdf_island['crossing_island'].value_counts())

# Generate indices and initialize the graph
roadlink_x_island, node_indices_island, edge_indices_island = generate_indices(roadlink_x_island)

# Snap points to the nearest edge and update the geometry
gdf_island_nearest, node_indices_island_updated = get_nearest_link_and_snapped_point(gdf_island, roadlink_x_island, node_indices_island)
roadlink_x_island_updated = modify_gdflink_with_snapped_points(roadlink_x_island, gdf_island_nearest)

# Create a graph from the modified road link data
G_island = create_undirected_road_graph(roadlink_x_island_updated, node_indices_island_updated)

distance_dfs_island = []

# Count points at the link level
direct_count_df_island = count_points_at_link_level(roadlink_x_island_updated, gdf_island_nearest, type_column='crossing_island')
print(direct_count_df_island.columns)
distance_dfs_island.append(direct_count_df_island)

# Count points within distances
for dist in [50, 100, 200]:
    dist_df_island = count_points_within_distance(roadlink_x_island_updated, gdf_island_nearest, G_island, node_indices_island_updated, distance=dist, type_column='crossing_island')
    print(dist_df_island.columns)
    distance_dfs_island.append(dist_df_island)
    get_reachable_nodes.cache_clear()

# Concatenate and save the final results
roadlink_x_island_count = pd.concat([roadlink_x_island_updated] + distance_dfs_island, axis=1)
print(roadlink_x_island_count.columns)

LinkPathIsland = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/roadlink_crossing_island.gpkg"
LinklayerIsland = "roadlink_crossing_island"
os.makedirs(os.path.dirname(LinkPathIsland), exist_ok=True)
roadlink_x_island_count.to_file(LinkPathIsland, layer=LinklayerIsland, driver='GPKG')

PathIslandSnapped = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/crossing_island_snapped.gpkg"
LayerIslandSnapped = "crossing_island_snapped"
gdf_island_nearest.to_file(PathIslandSnapped, layer=LayerIslandSnapped, driver='GPKG')

print(f"finished for region {region}, layer {LinklayerIsland}")

# End the timer and print the elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Total running time: {elapsed_time:.2f} seconds")


# Load junction data
print(f"process region {region}")

roadlink_x_junction = roadlink.copy()
print(roadlink_x_junction.columns)

PathJunction = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/junction.gpkg"
LayerJunction = "junction"
gdf_junction = gpd.read_file(filename=PathJunction, layer=LayerJunction)

gdf_junction = gdf_junction[['osmid', 'junction', 'junction_new', 'TOID', 'distance_join', 'geometry']]
print(gdf_junction['junction_new'].value_counts())

# Generate indices and initialize the graph
roadlink_x_junction, node_indices_junction, edge_indices_junction = generate_indices(roadlink_x_junction)

# Snap points to the nearest edge and update the geometry
gdf_junction_nearest, node_indices_junction_updated = get_nearest_link_and_snapped_point(gdf_junction, roadlink_x_junction, node_indices_junction)
roadlink_x_junction_updated = modify_gdflink_with_snapped_points(roadlink_x_junction, gdf_junction_nearest)

# Create a graph from the modified road link data
G_junction = create_undirected_road_graph(roadlink_x_junction_updated, node_indices_junction_updated)

distance_dfs_junction = []

direct_count_df_junction = count_points_at_link_level(roadlink_x_junction_updated, gdf_junction_nearest, type_column='junction_new')
print(direct_count_df_junction.columns)
distance_dfs_junction.append(direct_count_df_junction)

for dist in [50, 100, 200]:
    dist_df_junction = count_points_within_distance(roadlink_x_junction_updated, gdf_junction_nearest, G_junction, node_indices_junction_updated, distance=dist, type_column='junction_new')
    print(dist_df_junction.columns)
    distance_dfs_junction.append(dist_df_junction)
    get_reachable_nodes.cache_clear()

roadlink_x_junction_count = pd.concat([roadlink_x_junction_updated] + distance_dfs_junction, axis=1)
print(roadlink_x_junction_count.columns)

LinkPathJunction = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/roadlink_junction.gpkg"
LinklayerJunction = "roadlink_junction"
os.makedirs(os.path.dirname(LinkPathJunction), exist_ok=True)
roadlink_x_junction_count.to_file(LinkPathJunction, layer=LinklayerJunction, driver='GPKG')

PathJunctionSnapped = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/junction_snapped.gpkg"
LayerJunctionSnapped = "junction_snapped"
gdf_junction_nearest.to_file(PathJunctionSnapped, layer=LayerJunctionSnapped, driver='GPKG')

print(f"finished for region {region}, layer {LinklayerJunction}")

# End the timer and print the elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Total running time: {elapsed_time:.2f} seconds")


# Load traffic signal data
print(f"process region {region}")

roadlink_x_signal = roadlink.copy()
print(roadlink_x_signal.columns)

PathSignal = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/trafficsignal.gpkg"
LayerSignal = "trafficsignal"

gdf_signal = gpd.read_file(filename=PathSignal, layer=LayerSignal)

gdf_signal = gdf_signal[['osmid', 'signal', 'signal_new', 'TOID', 'distance_join', 'geometry']]
print(gdf_signal['signal_new'].value_counts())

# Generate indices and initialize the graph
roadlink_x_signal, node_indices_signal, edge_indices_signal = generate_indices(roadlink_x_signal)

# Snap points to the nearest edge and update the geometry
gdf_signal_nearest, node_indices_signal_updated = get_nearest_link_and_snapped_point(gdf_signal, roadlink_x_signal, node_indices_signal)
roadlink_x_signal_updated = modify_gdflink_with_snapped_points(roadlink_x_signal, gdf_signal_nearest)

# Create a graph from the modified road link data
G_signal = create_undirected_road_graph(roadlink_x_signal_updated, node_indices_signal_updated)

distance_dfs_signal = []

direct_count_df_signal = count_points_at_link_level(roadlink_x_signal_updated, gdf_signal_nearest, type_column='signal_new')
print(direct_count_df_signal.columns)
distance_dfs_signal.append(direct_count_df_signal)

for dist in [50, 100, 200]:
    dist_df_signal = count_points_within_distance(roadlink_x_signal_updated, gdf_signal_nearest, G_signal, node_indices_signal_updated, distance=dist, type_column='signal_new')
    print(dist_df_signal.columns)
    distance_dfs_signal.append(dist_df_signal)
    get_reachable_nodes.cache_clear()

roadlink_x_signal_count = pd.concat([roadlink_x_signal_updated] + distance_dfs_signal, axis=1)
print(roadlink_x_signal_count.columns)

LinkPathSignal = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/roadlink_trafficsignal.gpkg"
LinklayerSignal = "roadlink_trafficsignal"
os.makedirs(os.path.dirname(LinkPathSignal), exist_ok=True)
roadlink_x_signal_count.to_file(LinkPathSignal, layer=LinklayerSignal, driver='GPKG')

PathSignalSnapped = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/trafficsignal_snapped.gpkg"
LayerSignalSnapped = "trafficsignal_snapped"
gdf_signal_nearest.to_file(PathSignalSnapped, layer=LayerSignalSnapped, driver='GPKG')

print(f"finished for region {region}, layer {LinklayerSignal}")

# End the timer and print the elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Total running time: {elapsed_time:.2f} seconds")


# Load speed camera data
print(f"process region {region}")

roadlink_x_camera = roadlink.copy()
print(roadlink_x_camera.columns)

PathCamera = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/speedcamera.gpkg"
LayerCamera = "speedcamera"

gdf_camera = gpd.read_file(filename=PathCamera, layer=LayerCamera)

gdf_camera = gdf_camera[['osmid', 'camera', 'camera_new', 'TOID', 'distance_join', 'geometry']]
print(gdf_camera['camera_new'].value_counts())

# Generate indices and initialize the graph
roadlink_x_camera, node_indices_camera, edge_indices_camera = generate_indices(roadlink_x_camera)

# Snap points to the nearest edge and update the geometry
gdf_camera_nearest, node_indices_camera_updated = get_nearest_link_and_snapped_point(gdf_camera, roadlink_x_camera, node_indices_camera)
roadlink_x_camera_updated = modify_gdflink_with_snapped_points(roadlink_x_camera, gdf_camera_nearest)

# Create a graph from the modified road link data
G_camera = create_undirected_road_graph(roadlink_x_camera_updated, node_indices_camera_updated)

distance_dfs_camera = []

direct_count_df_camera = count_points_at_link_level(roadlink_x_camera_updated, gdf_camera_nearest, type_column='camera_new')
print(direct_count_df_camera.columns)
distance_dfs_camera.append(direct_count_df_camera)

for dist in [50, 100, 200]:
    dist_df_camera = count_points_within_distance(roadlink_x_camera_updated, gdf_camera_nearest, G_camera, node_indices_camera_updated, distance=dist, type_column='camera_new')
    print(dist_df_camera.columns)
    distance_dfs_camera.append(dist_df_camera)
    get_reachable_nodes.cache_clear()

roadlink_x_camera_count = pd.concat([roadlink_x_camera_updated] + distance_dfs_camera, axis=1)
print(roadlink_x_camera_count.columns)

LinkPathCamera = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/roadlink_speedcamera.gpkg"
LinklayerCamera = "roadlink_speedcamera"
os.makedirs(os.path.dirname(LinkPathCamera), exist_ok=True)
roadlink_x_camera_count.to_file(LinkPathCamera, layer=LinklayerCamera, driver='GPKG')

PathCameraSnapped = f"/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/{region}/speedcamera_snapped.gpkg"
LayerCameraSnapped = "speedcamera_snapped"
gdf_camera_nearest.to_file(PathCameraSnapped, layer=LayerCameraSnapped, driver='GPKG')

print(f"finished for region {region}, layer {LinklayerCamera}")

# End the timer and print the elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Total running time: {elapsed_time:.2f} seconds")








# %%
