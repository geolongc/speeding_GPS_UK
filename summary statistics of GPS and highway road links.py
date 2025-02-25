# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 17:57:10 2024

@author: geolche
"""


# new
#%%
import os
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, MetaData, select, text, func
import dask.dataframe as dd
import gc

# connect to postgresql database
dbname = "compass_db"
user = "compass_user"
password = "postgres"
host = "localhost"
port = "5432"

conn_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
db_engine = create_engine(conn_string)

region = "London"
# region = "Oxford"
# region = "Cambridge"
# region = "WestEngland"
# region = "Cardiff"
# region = "SouthYorkshire"
# region = "Manchester"
# region = "WestYorkshire"
# region = "Glasgow"
# region = "Liverpool"
# region = "Newcastle"
# region = "Edinburgh"
# region = "WestMidlands"

table_name = f'{region}_match'

InputPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1.gpkg"
link_layer = "RoadLink1x"
gdflink = gpd.read_file(filename=InputPath, layer=link_layer)

print(gdflink.shape)
print(gdflink['TOID'].nunique())
print(gdflink.columns)

print(gdflink.isna().sum())

#%%

gdflink = gdflink.dropna(subset=['speedLimit_mph']).reset_index(drop=True)
print(gdflink.shape)
print(gdflink['TOID'].nunique())
print(gdflink.columns)
print(gdflink['speedLimit_mph'].unique())
print(gdflink['routehierarchy'].unique())

gdflink_m = gdflink[['TOID', 'speedLimit_mph', 'routehierarchy']]
gdflink_m = dd.from_pandas(gdflink_m, npartitions=1)

metadata = MetaData()
metadata.reflect(bind=db_engine)
table = metadata.tables[table_name]
columns = table.columns.keys()
print(columns)

query = select(
    table.c.agent_id,
    table.c.time,
    table.c.speed,
    table.c.acc_speed,
    table.c.TOID
    )

chunks = []
with db_engine.connect() as conn:
    for chunk in pd.read_sql(query, conn, chunksize=2000000):
        chunk['index_col'] = chunk.index
        chunks.append(chunk)
    
df_data_pd = pd.concat(chunks, ignore_index=True)
print(df_data_pd.shape)

df_data = dd.from_pandas(df_data_pd, npartitions=10)
print(df_data.shape[0].compute())

del chunks, df_data_pd
gc.collect()

df_data['time'] = dd.to_datetime(df_data['time'], format='ISO8601')
df_data['time'] = df_data['time'].dt.strftime("%Y-%m-%d %H:%M:%S")
df_data['hour'] = dd.to_datetime(df_data['time']).dt.hour

df_data = df_data.merge(gdflink_m, on='TOID', how='inner')
df_data = df_data.persist()

print(df_data.columns)
print(df_data.isna().sum().compute())
print(df_data.shape[0].compute())

df_data = df_data.compute()
print(df_data.shape)
print(df_data['hour'].unique())


csv_dir = f"N:\\compass\\results_z\\summary\\{region}\\"
os.makedirs(csv_dir, exist_ok=True)


def count_speeding_events(group):
    speeding_pt_count = group[group['speed'] > group['speedLimit_mph']].shape[0]
    return speeding_pt_count


# speeding counts
speeding_counts_hour = df_data.groupby('hour').apply(count_speeding_events).reset_index(name=f'speeding_Total_{region}')
print(speeding_counts_hour)

speeding_counts_hour_speed = df_data.groupby(['speedLimit_mph', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
print(speeding_counts_hour_speed)

speeding_counts_hour_speed_pivot = speeding_counts_hour_speed.pivot(index='hour', columns='speedLimit_mph', values='speeding')
speeding_counts_hour_speed_pivot.columns = [f'speeding_{col}_{region}' for col in speeding_counts_hour_speed_pivot.columns]             
print(speeding_counts_hour_speed_pivot)

speeding_counts_hour_road = df_data.groupby(['routehierarchy', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
print(speeding_counts_hour_road)

speeding_counts_hour_road_pivot = speeding_counts_hour_road.pivot(index='hour', columns='routehierarchy', values='speeding')
speeding_counts_hour_road_pivot.columns = [f'speeding_{col}_{region}' for col in speeding_counts_hour_road_pivot.columns]
print(speeding_counts_hour_road_pivot)

speeding_counts_all = pd.merge(speeding_counts_hour, speeding_counts_hour_speed_pivot, on='hour', how='outer')
speeding_counts_all = pd.merge(speeding_counts_all, speeding_counts_hour_road_pivot, on='hour', how='outer')

speeding_counts_all.to_csv(f"N:\\compass\\results_z\\summary\\{region}\\speeding_byhour_{region}.csv", index=False)


speeding_mask = df_data['speed'] > df_data['speedLimit_mph']
speeding_count = speeding_mask.sum()
print(f"Total speeding count: {speeding_count}")

speeding_count_df = pd.DataFrame({'group': ['Total'], 'speeding': [speeding_count]})

speeding_counts_spl = df_data.groupby('speedLimit_mph').apply(count_speeding_events).reset_index()
speeding_counts_spl.columns = ['group', 'speeding']
print(speeding_counts_spl)

road_levels = ["Motorway", "A Road Primary", "A Road", "B Road", "Local Road", "Minor Road", 
               "Secondary Access Road", "Local Access Road", "Restricted Secondary Access Road", 
               "Restricted Local Access Road"]

speeding_counts_road = df_data.groupby('routehierarchy').apply(count_speeding_events).reset_index()
print(speeding_counts_road)

exist_levels = [level for level in road_levels if level in speeding_counts_road['routehierarchy'].unique()]
speeding_counts_road['routehierarchy'] = pd.Categorical(speeding_counts_road['routehierarchy'], categories=exist_levels, ordered=True)
speeding_counts_road = speeding_counts_road.sort_values('routehierarchy')
speeding_counts_road.columns = ['group', 'speeding']

speeding_counts_combined = pd.concat([speeding_count_df, speeding_counts_spl, speeding_counts_road], ignore_index=True)

# point counts
speed_limit_pointcounts = df_data['speedLimit_mph'].value_counts().reset_index(name='pointcount')
speed_limit_pointcounts = speed_limit_pointcounts.sort_values('speedLimit_mph')
speed_limit_pointcounts.columns = ['group', 'pointcount']
print(speed_limit_pointcounts)

total_pointcounts = len(df_data)
total_pointcounts_row = pd.DataFrame({'group': ['Total'], 'pointcount': [total_pointcounts]})

route_hierarchy_pointcounts = df_data['routehierarchy'].value_counts().reset_index(name='pointcount')
print(route_hierarchy_pointcounts)

exist_levels = [level for level in road_levels if level in route_hierarchy_pointcounts['routehierarchy'].unique()]
route_hierarchy_pointcounts['routehierarchy'] = pd.Categorical(route_hierarchy_pointcounts['routehierarchy'], categories=exist_levels, ordered=True)
route_hierarchy_pointcounts = route_hierarchy_pointcounts.sort_values('routehierarchy')
route_hierarchy_pointcounts.columns = ['group', 'pointcount']

speed_limit_pointcounts_combined = pd.concat([total_pointcounts_row, speed_limit_pointcounts, 
                                              route_hierarchy_pointcounts], ignore_index=True)

speed_limit_pointcounts_combined['point_pct'] = (speed_limit_pointcounts_combined['pointcount'] / total_pointcounts) * 100
speed_limit_pointcounts_combined['point_pct'] = round(speed_limit_pointcounts_combined['point_pct'], 2)


link_pointcountdf = df_data.groupby('TOID').size().reset_index(name='ptcount')
# print(link_pointcountdf.head())

gdflink = gdflink.merge(link_pointcountdf, on='TOID', how='left')

speeding_counts_roadid = df_data.groupby('TOID').apply(count_speeding_events).reset_index(name='link_speedingcount')
print(speeding_counts_roadid.head())

gdflink = gdflink.merge(speeding_counts_roadid, on='TOID', how='left')
print(gdflink.shape)
print(gdflink.columns)

print(gdflink['ptcount'].isnull().sum())
print(gdflink['ptcount'].notnull().sum())
print(gdflink[(gdflink['ptcount'] > 0) & (gdflink['ptcount'] < 5)].shape[0])

gdflink = gdflink.dropna(subset=['ptcount']).reset_index(drop=True)

out_path = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1_x_count.gpkg"
out_layer = "RoadLink1x_q"
gdflink.to_file(filename=out_path, layer=out_layer, driver="GPKG")

gdflink1 = gdflink[(gdflink['ptcount'] >= 5)].reset_index(drop=True)
print(gdflink1.shape[0])

out_path1 = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1_x_count.gpkg"
out_layer1 = "RoadLink1x_q1"
gdflink1.to_file(filename=out_path1, layer=out_layer1, driver="GPKG")


# points count
total_ptcount = gdflink['ptcount'].sum()
total_ptcount_df = pd.DataFrame({'group': ['Total'], 'pointcount1': [total_ptcount]})

speedlimit_ptsum = gdflink.groupby('speedLimit_mph')['ptcount'].sum().reset_index()
speedlimit_ptsum.columns = ['group', 'pointcount1']

routehierarchy_ptsum = gdflink.groupby('routehierarchy')['ptcount'].sum().reset_index()
routehierarchy_ptsum.columns = ['group', 'pointcount1']

exist_levels = [level for level in road_levels if level in routehierarchy_ptsum['group'].unique()]
routehierarchy_ptsum['group'] = pd.Categorical(routehierarchy_ptsum['group'], categories=exist_levels, ordered=True)
routehierarchy_ptsum = routehierarchy_ptsum.sort_values('group')

linkpointcounts_combined = pd.concat([total_ptcount_df, speedlimit_ptsum, routehierarchy_ptsum], ignore_index=True)
linkpointcounts_combined['point_pct1'] = (linkpointcounts_combined['pointcount1'] / total_ptcount) * 100
linkpointcounts_combined['point_pct1'] = round(linkpointcounts_combined['point_pct1'], 2)


total_ptcount1 = gdflink1['ptcount'].sum()
total_ptcount1_df = pd.DataFrame({'group': ['Total'], 'pointcount1': [total_ptcount1]})

speedlimit_ptsum1 = gdflink1.groupby('speedLimit_mph')['ptcount'].sum().reset_index()
speedlimit_ptsum1.columns = ['group', 'pointcount1']

routehierarchy_ptsum1 = gdflink1.groupby('routehierarchy')['ptcount'].sum().reset_index()
routehierarchy_ptsum1.columns = ['group', 'pointcount1']

exist_levels = [level for level in road_levels if level in routehierarchy_ptsum1['group'].unique()]
routehierarchy_ptsum1['group'] = pd.Categorical(routehierarchy_ptsum1['group'], categories=exist_levels, ordered=True)
routehierarchy_ptsum1 = routehierarchy_ptsum1.sort_values('group')

linkpointcounts_combined1 = pd.concat([total_ptcount1_df, speedlimit_ptsum1, routehierarchy_ptsum1], ignore_index=True)
linkpointcounts_combined1['point_pct1'] = (linkpointcounts_combined1['pointcount1'] / total_ptcount1) * 100
linkpointcounts_combined1['point_pct1'] = round(linkpointcounts_combined1['point_pct1'], 2)


# count road link
print(gdflink.shape)
print(gdflink['TOID'].nunique())

total_toid_count = len(gdflink)
print(total_toid_count)

toid_by_speedlimit = gdflink.groupby('speedLimit_mph')['TOID'].count().reset_index()
toid_by_speedlimit.columns = ['group', 'linkcount']
toid_by_speedlimit['link_pct'] = (toid_by_speedlimit['linkcount'] / total_toid_count) * 100
toid_by_speedlimit['link_pct'] = round(toid_by_speedlimit['link_pct'], 2)

toid_by_route = gdflink.groupby('routehierarchy')['TOID'].count().reset_index()
toid_by_route.columns = ['group', 'linkcount']
toid_by_route['link_pct'] = (toid_by_route['linkcount'] / total_toid_count) * 100
toid_by_route['link_pct'] = round(toid_by_route['link_pct'], 2)

exist_levels = [level for level in road_levels if level in toid_by_route['group'].unique()]
toid_by_route['group'] = pd.Categorical(toid_by_route['group'], categories=exist_levels, ordered=True)
toid_by_route = toid_by_route.sort_values('group')

total_count_df = pd.DataFrame({'group': ['Total'], 'linkcount': total_toid_count, 'link_pct': 100.0})

linkcount_combined = pd.concat([total_count_df, toid_by_speedlimit, toid_by_route], ignore_index=True)


print(gdflink1.shape)
print(gdflink1['TOID'].nunique())

total_toid_count1 = len(gdflink1)
print(total_toid_count1)

toid_by_speedlimit1 = gdflink1.groupby('speedLimit_mph')['TOID'].count().reset_index()
toid_by_speedlimit1.columns = ['group', 'linkcount']
toid_by_speedlimit1['link_pct'] = (toid_by_speedlimit1['linkcount'] / total_toid_count1) * 100
toid_by_speedlimit1['link_pct'] = round(toid_by_speedlimit1['link_pct'], 2)

toid_by_route1 = gdflink1.groupby('routehierarchy')['TOID'].count().reset_index()
toid_by_route1.columns = ['group', 'linkcount']
toid_by_route1['link_pct'] = (toid_by_route1['linkcount'] / total_toid_count1) * 100
toid_by_route1['link_pct'] = round(toid_by_route1['link_pct'], 2)

exist_levels = [level for level in road_levels if level in toid_by_route1['group'].unique()]
toid_by_route1['group'] = pd.Categorical(toid_by_route1['group'], categories=exist_levels, ordered=True)
toid_by_route1 = toid_by_route1.sort_values('group')

total_count_df1 = pd.DataFrame({'group': ['Total'], 'linkcount': total_toid_count1, 'link_pct': 100.0})

linkcount_combined1 = pd.concat([total_count_df1, toid_by_speedlimit1, toid_by_route1], ignore_index=True)


# link length
gdflink['linklength'] = gdflink.geometry.length

lengthsum = gdflink['linklength'].sum()
linklength_total = pd.DataFrame({'group': ['Total'], 'linklength': [lengthsum], 'length_pct': 100.0})

routehierarchy_lengthsum = gdflink.groupby('routehierarchy')['linklength'].sum().reset_index()
speedlimit_lengthsum = gdflink.groupby('speedLimit_mph')['linklength'].sum().reset_index()
print(routehierarchy_lengthsum)
print(speedlimit_lengthsum)

speedlimit_lengthsum.columns = ['group', 'linklength']
routehierarchy_lengthsum.columns = ['group', 'linklength']

exist_levels = [level for level in road_levels if level in routehierarchy_lengthsum['group'].unique()]
routehierarchy_lengthsum['group'] = pd.Categorical(routehierarchy_lengthsum['group'], categories=exist_levels, ordered=True)
routehierarchy_lengthsum = routehierarchy_lengthsum.sort_values('group')

speedlimit_lengthsum['length_pct'] = (speedlimit_lengthsum['linklength'] / lengthsum) * 100
speedlimit_lengthsum['length_pct'] = round(speedlimit_lengthsum['length_pct'], 2)
routehierarchy_lengthsum['length_pct'] = (routehierarchy_lengthsum['linklength'] / lengthsum) * 100
routehierarchy_lengthsum['length_pct'] = round(routehierarchy_lengthsum['length_pct'], 2)

linklength_combined = pd.concat([linklength_total, speedlimit_lengthsum, routehierarchy_lengthsum], ignore_index=True)
linklength_combined['linklength'] = linklength_combined['linklength'] / 1609.34
linklength_combined['linklength'] = round(linklength_combined['linklength'], 2)
print(linklength_combined)


gdflink1['linklength'] = gdflink1.geometry.length

lengthsum = gdflink1['linklength'].sum()
linklength_total = pd.DataFrame({'group': ['Total'], 'linklength': [lengthsum], 'length_pct': 100.0})

routehierarchy_lengthsum = gdflink1.groupby('routehierarchy')['linklength'].sum().reset_index()
speedlimit_lengthsum = gdflink1.groupby('speedLimit_mph')['linklength'].sum().reset_index()
print(routehierarchy_lengthsum)
print(speedlimit_lengthsum)

speedlimit_lengthsum.columns = ['group', 'linklength']
routehierarchy_lengthsum.columns = ['group', 'linklength']

exist_levels = [level for level in road_levels if level in routehierarchy_lengthsum['group'].unique()]
routehierarchy_lengthsum['group'] = pd.Categorical(routehierarchy_lengthsum['group'], categories=exist_levels, ordered=True)
routehierarchy_lengthsum = routehierarchy_lengthsum.sort_values('group')

speedlimit_lengthsum['length_pct'] = (speedlimit_lengthsum['linklength'] / lengthsum) * 100
speedlimit_lengthsum['length_pct'] = round(speedlimit_lengthsum['length_pct'], 2)
routehierarchy_lengthsum['length_pct'] = (routehierarchy_lengthsum['linklength'] / lengthsum) * 100
routehierarchy_lengthsum['length_pct'] = round(routehierarchy_lengthsum['length_pct'], 2)

linklength_combined1 = pd.concat([linklength_total, speedlimit_lengthsum, routehierarchy_lengthsum], ignore_index=True)
linklength_combined1['linklength'] = linklength_combined1['linklength'] / 1609.34
linklength_combined1['linklength'] = round(linklength_combined1['linklength'], 2)
print(linklength_combined1)


# filtering df_data
df_data = dd.from_pandas(df_data, npartitions=10)

df_data = df_data[df_data['TOID'].isin(gdflink1['TOID'])]
df_data = df_data.persist()

print(df_data.columns)
print(df_data.isna().sum().compute())
print(df_data.shape[0].compute())

df_data = df_data.compute()
print(df_data.shape)


speeding_counts_hour = df_data.groupby('hour').apply(count_speeding_events).reset_index(name=f'speeding_Total_{region}')
print(speeding_counts_hour)

speeding_counts_hour_speed = df_data.groupby(['speedLimit_mph', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
print(speeding_counts_hour_speed)

speeding_counts_hour_speed_pivot = speeding_counts_hour_speed.pivot(index='hour', columns='speedLimit_mph', values='speeding')
speeding_counts_hour_speed_pivot.columns = [f'adhrate_{col}_{region}' for col in speeding_counts_hour_speed_pivot.columns]             
print(speeding_counts_hour_speed_pivot)

speeding_counts_hour_road = df_data.groupby(['routehierarchy', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
print(speeding_counts_hour_road)

speeding_counts_hour_road_pivot = speeding_counts_hour_road.pivot(index='hour', columns='routehierarchy', values='speeding')
speeding_counts_hour_road_pivot.columns = [f'speeding_{col}_{region}' for col in speeding_counts_hour_road_pivot.columns]
print(speeding_counts_hour_road_pivot)

speeding_counts_all = pd.merge(speeding_counts_hour, speeding_counts_hour_speed_pivot, on='hour', how='outer')
speeding_counts_all = pd.merge(speeding_counts_all, speeding_counts_hour_road_pivot, on='hour', how='outer')

speeding_counts_all.to_csv(f"N:\\compass\\results_z\\summary\\{region}\\speeding1_byhour_{region}.csv", index=False)


speeding_mask = df_data['speed'] > df_data['speedLimit_mph']
speeding_count = speeding_mask.sum()
print(f"Total speeding count: {speeding_count}")

speeding_count_df = pd.DataFrame({'group': ['Total'], 'speeding': [speeding_count]})

speeding_counts_spl = df_data.groupby('speedLimit_mph').apply(count_speeding_events).reset_index()
speeding_counts_spl.columns = ['group', 'speeding']
print(speeding_counts_spl)

speeding_counts_road = df_data.groupby('routehierarchy').apply(count_speeding_events).reset_index()
print(speeding_counts_road)
exist_levels = [level for level in road_levels if level in speeding_counts_road['routehierarchy'].unique()]
speeding_counts_road['routehierarchy'] = pd.Categorical(speeding_counts_road['routehierarchy'], categories=exist_levels, ordered=True)
speeding_counts_road = speeding_counts_road.sort_values('routehierarchy')
speeding_counts_road.columns = ['group', 'speeding']

speeding_counts_combined1 = pd.concat([speeding_count_df, speeding_counts_spl, speeding_counts_road], ignore_index=True)


speed_limit_pointcounts = df_data['speedLimit_mph'].value_counts().reset_index(name='pointcount')
speed_limit_pointcounts = speed_limit_pointcounts.sort_values('speedLimit_mph')
speed_limit_pointcounts.columns = ['group', 'pointcount']
print(speed_limit_pointcounts)

total_pointcounts = len(df_data)
total_pointcounts_row = pd.DataFrame({'group': ['Total'], 'pointcount': [total_pointcounts]})

route_hierarchy_pointcounts = df_data['routehierarchy'].value_counts().reset_index(name='pointcount')
print(route_hierarchy_pointcounts)

exist_levels = [level for level in road_levels if level in route_hierarchy_pointcounts['routehierarchy'].unique()]
route_hierarchy_pointcounts['routehierarchy'] = pd.Categorical(route_hierarchy_pointcounts['routehierarchy'], categories=exist_levels, ordered=True)
route_hierarchy_pointcounts = route_hierarchy_pointcounts.sort_values('routehierarchy')
route_hierarchy_pointcounts.columns = ['group', 'pointcount']

speed_limit_pointcounts_combined1 = pd.concat([total_pointcounts_row, speed_limit_pointcounts, 
                                              route_hierarchy_pointcounts], ignore_index=True)

speed_limit_pointcounts_combined1['point_pct'] = (speed_limit_pointcounts_combined1['pointcount'] / total_pointcounts) * 100
speed_limit_pointcounts_combined1['point_pct'] = round(speed_limit_pointcounts_combined1['point_pct'], 2)


combined_df = pd.merge(speeding_counts_combined, speed_limit_pointcounts_combined, on='group', how='inner')
combined_df = pd.merge(combined_df, linkpointcounts_combined, on='group', how='inner')
combined_df = pd.merge(combined_df, linkcount_combined, on='group', how='inner')
combined_df = pd.merge(combined_df, linklength_combined, on='group', how='inner')
combined_df.to_csv(f"N:\\compass\\results_z\\summary\\{region}\\summary_{region}.csv", index=False)

combined_df1 = pd.merge(speeding_counts_combined1, speed_limit_pointcounts_combined1, on='group', how='inner')
combined_df1 = pd.merge(combined_df1, linkpointcounts_combined1, on='group', how='inner')
combined_df1 = pd.merge(combined_df1, linkcount_combined1, on='group', how='inner')
combined_df1 = pd.merge(combined_df1, linklength_combined1, on='group', how='inner')
combined_df1.to_csv(f"N:\\compass\\results_z\\summary\\{region}\\summary1_{region}.csv", index=False)


# re-group
#%%
import os
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, MetaData, select, text, func
import dask.dataframe as dd
import gc

# connect to postgresql database
dbname = "compass_db"
user = "compass_user"
password = "postgres"
host = "localhost"
port = "5432"

conn_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
db_engine = create_engine(conn_string)

region = "London"
# region = "Oxford"
# region = "Cambridge"
# region = "WestEngland"
# region = "Cardiff"
# region = "SouthYorkshire"
# region = "Manchester"
# region = "WestYorkshire"
# region = "Glasgow"
# region = "Liverpool"
# region = "Newcastle"
# region = "Edinburgh"
# region = "WestMidlands"

table_name = f'{region}_match'

InputPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1.gpkg"
link_layer = "RoadLink1x"
gdflink = gpd.read_file(filename=InputPath, layer=link_layer)

print(gdflink.shape)
print(gdflink['TOID'].nunique())
print(gdflink.columns)

print(gdflink.isna().sum())

speed_limit_mapping = {
    5: '10',
    10: '10',
    15: '10',
    20: '20',
    30: '30',
    40: '40',
    50: '50',
    60: '60',
    70: '70'
    }

route_hierarchy_mapping = {
    'Motorway': 'Motorway', 
    'A Road Primary': 'A Road', 
    'A Road': 'A Road', 
    'B Road': 'B Road', 
    'Local Road': 'Local Road', 
    'Minor Road': 'Minor Road', 
    'Secondary Access Road': 'Others', 
    'Local Access Road': 'Others', 
    'Restricted Secondary Access Road': 'Others', 
    'Restricted Local Access Road': 'Others'
    }


gdflink['speedLimit_group'] = gdflink['speedLimit_mph'].map(speed_limit_mapping)
gdflink['routehierarchy_group'] = gdflink['routehierarchy'].map(route_hierarchy_mapping)

print(gdflink.isna().sum())

out_path = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1_regroup.gpkg"
out_layer = "RoadLink1y"
gdflink.to_file(filename=out_path, layer=out_layer, driver="GPKG")


gdflink = gdflink.dropna(subset=['speedLimit_mph']).reset_index(drop=True)
print(gdflink.shape)
print(gdflink['TOID'].nunique())
print(gdflink.columns)
print(gdflink['speedLimit_group'].unique())
print(gdflink['routehierarchy_group'].unique())

gdflink_m = gdflink[['TOID', 'speedLimit_mph', 'speedLimit_group', 'routehierarchy_group']]
gdflink_m = dd.from_pandas(gdflink_m, npartitions=1)


metadata = MetaData()
metadata.reflect(bind=db_engine)
table = metadata.tables[table_name]
columns = table.columns.keys()
print(columns)

query = select(
    table.c.agent_id,
    table.c.time,
    table.c.speed,
    table.c.acc_speed,
    table.c.TOID
    )

chunks = []
with db_engine.connect() as conn:
    for chunk in pd.read_sql(query, conn, chunksize=2000000):
        chunk['index_col'] = chunk.index
        chunks.append(chunk)
    
df_data_pd = pd.concat(chunks, ignore_index=True)
print(df_data_pd.shape)

df_data = dd.from_pandas(df_data_pd, npartitions=10)
print(df_data.shape[0].compute())

del chunks, df_data_pd
gc.collect()

df_data['time'] = dd.to_datetime(df_data['time'], format='ISO8601')
df_data['time'] = df_data['time'].dt.strftime("%Y-%m-%d %H:%M:%S")
df_data['hour'] = dd.to_datetime(df_data['time']).dt.hour

df_data = df_data.merge(gdflink_m, on='TOID', how='inner')
df_data = df_data.persist()

print(df_data.columns)
print(df_data.isna().sum().compute())
print(df_data.shape[0].compute())

df_data = df_data.compute()
print(df_data.shape)
print(df_data['hour'].unique())


csv_dir = f"N:\\compass\\results_z\\summary_regroup\\{region}\\"
os.makedirs(csv_dir, exist_ok=True)


def count_speeding_events(group):
    speeding_pt_count = group[group['speed'] > group['speedLimit_mph']].shape[0]
    return speeding_pt_count


# speeding counts
speeding_counts_hour = df_data.groupby('hour').apply(count_speeding_events).reset_index(name=f'speeding_Total_{region}')
print(speeding_counts_hour)

speeding_counts_hour_speed = df_data.groupby(['speedLimit_group', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
print(speeding_counts_hour_speed)

speeding_counts_hour_speed_pivot = speeding_counts_hour_speed.pivot(index='hour', columns='speedLimit_group', values='speeding')
speeding_counts_hour_speed_pivot.columns = [f'speeding_{col}_{region}' for col in speeding_counts_hour_speed_pivot.columns]             
print(speeding_counts_hour_speed_pivot)

speeding_counts_hour_road = df_data.groupby(['routehierarchy_group', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
print(speeding_counts_hour_road)

speeding_counts_hour_road_pivot = speeding_counts_hour_road.pivot(index='hour', columns='routehierarchy_group', values='speeding')
speeding_counts_hour_road_pivot.columns = [f'speeding_{col}_{region}' for col in speeding_counts_hour_road_pivot.columns]
print(speeding_counts_hour_road_pivot)

speeding_counts_all = pd.merge(speeding_counts_hour, speeding_counts_hour_speed_pivot, on='hour', how='outer')
speeding_counts_all = pd.merge(speeding_counts_all, speeding_counts_hour_road_pivot, on='hour', how='outer')

speeding_counts_all.to_csv(f"N:\\compass\\results_z\\summary_regroup\\{region}\\speeding_byhour_{region}.csv", index=False)

speeding_mask = df_data['speed'] > df_data['speedLimit_mph']
speeding_count = speeding_mask.sum()
print(f"Total speeding count: {speeding_count}")

speeding_count_df = pd.DataFrame({'group': ['Total'], 'speeding': [speeding_count]})

speeding_counts_spl = df_data.groupby('speedLimit_group').apply(count_speeding_events).reset_index()
speeding_counts_spl.columns = ['group', 'speeding']
print(speeding_counts_spl)

road_levels = ["Motorway", "A Road", "B Road", "Local Road", "Minor Road", "Others"]

speeding_counts_road = df_data.groupby('routehierarchy_group').apply(count_speeding_events).reset_index()
print(speeding_counts_road)

exist_levels = [level for level in road_levels if level in speeding_counts_road['routehierarchy_group'].unique()]
speeding_counts_road['routehierarchy_group'] = pd.Categorical(speeding_counts_road['routehierarchy_group'], categories=exist_levels, ordered=True)
speeding_counts_road = speeding_counts_road.sort_values('routehierarchy_group')
speeding_counts_road.columns = ['group', 'speeding']

speeding_counts_combined = pd.concat([speeding_count_df, speeding_counts_spl, speeding_counts_road], ignore_index=True)

# point counts
speed_limit_pointcounts = df_data['speedLimit_group'].value_counts().reset_index(name='pointcount')
speed_limit_pointcounts = speed_limit_pointcounts.sort_values('speedLimit_group')
speed_limit_pointcounts.columns = ['group', 'pointcount']
print(speed_limit_pointcounts)

total_pointcounts = len(df_data)
total_pointcounts_row = pd.DataFrame({'group': ['Total'], 'pointcount': [total_pointcounts]})

route_hierarchy_pointcounts = df_data['routehierarchy_group'].value_counts().reset_index(name='pointcount')
print(route_hierarchy_pointcounts)

exist_levels = [level for level in road_levels if level in route_hierarchy_pointcounts['routehierarchy_group'].unique()]
route_hierarchy_pointcounts['routehierarchy_group'] = pd.Categorical(route_hierarchy_pointcounts['routehierarchy_group'], categories=exist_levels, ordered=True)
route_hierarchy_pointcounts = route_hierarchy_pointcounts.sort_values('routehierarchy_group')
route_hierarchy_pointcounts.columns = ['group', 'pointcount']

speed_limit_pointcounts_combined = pd.concat([total_pointcounts_row, speed_limit_pointcounts, 
                                              route_hierarchy_pointcounts], ignore_index=True)

speed_limit_pointcounts_combined['point_pct'] = (speed_limit_pointcounts_combined['pointcount'] / total_pointcounts) * 100
speed_limit_pointcounts_combined['point_pct'] = round(speed_limit_pointcounts_combined['point_pct'], 2)

link_pointcountdf = df_data.groupby('TOID').size().reset_index(name='ptcount')
# print(link_pointcountdf.head())

gdflink = gdflink.merge(link_pointcountdf, on='TOID', how='left')

speeding_counts_roadid = df_data.groupby('TOID').apply(count_speeding_events).reset_index(name='link_speedingcount')
print(speeding_counts_roadid.head())

gdflink = gdflink.merge(speeding_counts_roadid, on='TOID', how='left')
print(gdflink.shape)
print(gdflink.columns)

print(gdflink['ptcount'].isnull().sum())
print(gdflink['ptcount'].notnull().sum())
print(gdflink[(gdflink['ptcount'] > 0) & (gdflink['ptcount'] < 5)].shape[0])

gdflink = gdflink.dropna(subset=['ptcount']).reset_index(drop=True)

out_path = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1_regroup_count.gpkg"
out_layer = "RoadLink1y_q"
gdflink.to_file(filename=out_path, layer=out_layer, driver="GPKG")

gdflink1 = gdflink[(gdflink['ptcount'] >= 5)].reset_index(drop=True)
print(gdflink1.shape[0])

out_path1 = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1_regroup_count.gpkg"
out_layer1 = "RoadLink1y_q1"
gdflink1.to_file(filename=out_path1, layer=out_layer1, driver="GPKG")


# points count
total_ptcount = gdflink['ptcount'].sum()
total_ptcount_df = pd.DataFrame({'group': ['Total'], 'pointcount1': [total_ptcount]})

speedlimit_ptsum = gdflink.groupby('speedLimit_group')['ptcount'].sum().reset_index()
speedlimit_ptsum.columns = ['group', 'pointcount1']

routehierarchy_ptsum = gdflink.groupby('routehierarchy_group')['ptcount'].sum().reset_index()
routehierarchy_ptsum.columns = ['group', 'pointcount1']

exist_levels = [level for level in road_levels if level in routehierarchy_ptsum['group'].unique()]
routehierarchy_ptsum['group'] = pd.Categorical(routehierarchy_ptsum['group'], categories=exist_levels, ordered=True)
routehierarchy_ptsum = routehierarchy_ptsum.sort_values('group')

linkpointcounts_combined = pd.concat([total_ptcount_df, speedlimit_ptsum, routehierarchy_ptsum], ignore_index=True)
linkpointcounts_combined['point_pct1'] = (linkpointcounts_combined['pointcount1'] / total_ptcount) * 100
linkpointcounts_combined['point_pct1'] = round(linkpointcounts_combined['point_pct1'], 2)


total_ptcount1 = gdflink1['ptcount'].sum()
total_ptcount1_df = pd.DataFrame({'group': ['Total'], 'pointcount1': [total_ptcount1]})

speedlimit_ptsum1 = gdflink1.groupby('speedLimit_group')['ptcount'].sum().reset_index()
speedlimit_ptsum1.columns = ['group', 'pointcount1']

routehierarchy_ptsum1 = gdflink1.groupby('routehierarchy_group')['ptcount'].sum().reset_index()
routehierarchy_ptsum1.columns = ['group', 'pointcount1']

exist_levels = [level for level in road_levels if level in routehierarchy_ptsum1['group'].unique()]
routehierarchy_ptsum1['group'] = pd.Categorical(routehierarchy_ptsum1['group'], categories=exist_levels, ordered=True)
routehierarchy_ptsum1 = routehierarchy_ptsum1.sort_values('group')

linkpointcounts_combined1 = pd.concat([total_ptcount1_df, speedlimit_ptsum1, routehierarchy_ptsum1], ignore_index=True)
linkpointcounts_combined1['point_pct1'] = (linkpointcounts_combined1['pointcount1'] / total_ptcount1) * 100
linkpointcounts_combined1['point_pct1'] = round(linkpointcounts_combined1['point_pct1'], 2)


# count road link
print(gdflink.shape)
print(gdflink['TOID'].nunique())

total_toid_count = len(gdflink)
print(total_toid_count)

toid_by_speedlimit = gdflink.groupby('speedLimit_group')['TOID'].count().reset_index()
toid_by_speedlimit.columns = ['group', 'linkcount']
toid_by_speedlimit['link_pct'] = (toid_by_speedlimit['linkcount'] / total_toid_count) * 100
toid_by_speedlimit['link_pct'] = round(toid_by_speedlimit['link_pct'], 2)

toid_by_route = gdflink.groupby('routehierarchy_group')['TOID'].count().reset_index()
toid_by_route.columns = ['group', 'linkcount']
toid_by_route['link_pct'] = (toid_by_route['linkcount'] / total_toid_count) * 100
toid_by_route['link_pct'] = round(toid_by_route['link_pct'], 2)

exist_levels = [level for level in road_levels if level in toid_by_route['group'].unique()]
toid_by_route['group'] = pd.Categorical(toid_by_route['group'], categories=exist_levels, ordered=True)
toid_by_route = toid_by_route.sort_values('group')

total_count_df = pd.DataFrame({'group': ['Total'], 'linkcount': total_toid_count, 'link_pct': 100.0})

linkcount_combined = pd.concat([total_count_df, toid_by_speedlimit, toid_by_route], ignore_index=True)

print(gdflink1.shape)
print(gdflink1['TOID'].nunique())

total_toid_count1 = len(gdflink1)
print(total_toid_count1)

toid_by_speedlimit1 = gdflink1.groupby('speedLimit_group')['TOID'].count().reset_index()
toid_by_speedlimit1.columns = ['group', 'linkcount']
toid_by_speedlimit1['link_pct'] = (toid_by_speedlimit1['linkcount'] / total_toid_count1) * 100
toid_by_speedlimit1['link_pct'] = round(toid_by_speedlimit1['link_pct'], 2)

toid_by_route1 = gdflink1.groupby('routehierarchy_group')['TOID'].count().reset_index()
toid_by_route1.columns = ['group', 'linkcount']
toid_by_route1['link_pct'] = (toid_by_route1['linkcount'] / total_toid_count1) * 100
toid_by_route1['link_pct'] = round(toid_by_route1['link_pct'], 2)

exist_levels = [level for level in road_levels if level in toid_by_route1['group'].unique()]
toid_by_route1['group'] = pd.Categorical(toid_by_route1['group'], categories=exist_levels, ordered=True)
toid_by_route1 = toid_by_route1.sort_values('group')

total_count_df1 = pd.DataFrame({'group': ['Total'], 'linkcount': total_toid_count1, 'link_pct': 100.0})

linkcount_combined1 = pd.concat([total_count_df1, toid_by_speedlimit1, toid_by_route1], ignore_index=True)

# link length
gdflink['linklength'] = gdflink.geometry.length

lengthsum = gdflink['linklength'].sum()
linklength_total = pd.DataFrame({'group': ['Total'], 'linklength': [lengthsum], 'length_pct': 100.0})

speedlimit_lengthsum = gdflink.groupby('speedLimit_group')['linklength'].sum().reset_index()
routehierarchy_lengthsum = gdflink.groupby('routehierarchy_group')['linklength'].sum().reset_index()
print(speedlimit_lengthsum)
print(routehierarchy_lengthsum)

speedlimit_lengthsum.columns = ['group', 'linklength']
routehierarchy_lengthsum.columns = ['group', 'linklength']

exist_levels = [level for level in road_levels if level in routehierarchy_lengthsum['group'].unique()]
routehierarchy_lengthsum['group'] = pd.Categorical(routehierarchy_lengthsum['group'], categories=exist_levels, ordered=True)
routehierarchy_lengthsum = routehierarchy_lengthsum.sort_values('group')

speedlimit_lengthsum['length_pct'] = (speedlimit_lengthsum['linklength'] / lengthsum) * 100
speedlimit_lengthsum['length_pct'] = round(speedlimit_lengthsum['length_pct'], 2)
routehierarchy_lengthsum['length_pct'] = (routehierarchy_lengthsum['linklength'] / lengthsum) * 100
routehierarchy_lengthsum['length_pct'] = round(routehierarchy_lengthsum['length_pct'], 2)

linklength_combined = pd.concat([linklength_total, speedlimit_lengthsum, routehierarchy_lengthsum], ignore_index=True)
linklength_combined['linklength'] = linklength_combined['linklength'] / 1609.34
linklength_combined['linklength'] = round(linklength_combined['linklength'], 2)
print(linklength_combined)

gdflink1['linklength'] = gdflink1.geometry.length

lengthsum = gdflink1['linklength'].sum()
linklength_total = pd.DataFrame({'group': ['Total'], 'linklength': [lengthsum], 'length_pct': 100.0})

speedlimit_lengthsum = gdflink1.groupby('speedLimit_group')['linklength'].sum().reset_index()
routehierarchy_lengthsum = gdflink1.groupby('routehierarchy_group')['linklength'].sum().reset_index()
print(speedlimit_lengthsum)
print(routehierarchy_lengthsum)

speedlimit_lengthsum.columns = ['group', 'linklength']
routehierarchy_lengthsum.columns = ['group', 'linklength']

exist_levels = [level for level in road_levels if level in routehierarchy_lengthsum['group'].unique()]
routehierarchy_lengthsum['group'] = pd.Categorical(routehierarchy_lengthsum['group'], categories=exist_levels, ordered=True)
routehierarchy_lengthsum = routehierarchy_lengthsum.sort_values('group')

speedlimit_lengthsum['length_pct'] = (speedlimit_lengthsum['linklength'] / lengthsum) * 100
speedlimit_lengthsum['length_pct'] = round(speedlimit_lengthsum['length_pct'], 2)
routehierarchy_lengthsum['length_pct'] = (routehierarchy_lengthsum['linklength'] / lengthsum) * 100
routehierarchy_lengthsum['length_pct'] = round(routehierarchy_lengthsum['length_pct'], 2)

linklength_combined1 = pd.concat([linklength_total, speedlimit_lengthsum, routehierarchy_lengthsum], ignore_index=True)
linklength_combined1['linklength'] = linklength_combined1['linklength'] / 1609.34
linklength_combined1['linklength'] = round(linklength_combined1['linklength'], 2)
print(linklength_combined1)



# filtering df_data
df_data = dd.from_pandas(df_data, npartitions=10)

df_data = df_data[df_data['TOID'].isin(gdflink1['TOID'])]
df_data = df_data.persist()

print(df_data.columns)
print(df_data.isna().sum().compute())
print(df_data.shape[0].compute())

df_data = df_data.compute()
print(df_data.shape)


speeding_counts_hour = df_data.groupby('hour').apply(count_speeding_events).reset_index(name=f'speeding_Total_{region}')
print(speeding_counts_hour)

speeding_counts_hour_speed = df_data.groupby(['speedLimit_group', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
print(speeding_counts_hour_speed)

speeding_counts_hour_speed_pivot = speeding_counts_hour_speed.pivot(index='hour', columns='speedLimit_group', values='speeding')
speeding_counts_hour_speed_pivot.columns = [f'speeding_{col}_{region}' for col in speeding_counts_hour_speed_pivot.columns]             
print(speeding_counts_hour_speed_pivot)

speeding_counts_hour_road = df_data.groupby(['routehierarchy_group', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
print(speeding_counts_hour_road)

speeding_counts_hour_road_pivot = speeding_counts_hour_road.pivot(index='hour', columns='routehierarchy_group', values='speeding')
speeding_counts_hour_road_pivot.columns = [f'speeding_{col}_{region}' for col in speeding_counts_hour_road_pivot.columns]
print(speeding_counts_hour_road_pivot)

speeding_counts_all = pd.merge(speeding_counts_hour, speeding_counts_hour_speed_pivot, on='hour', how='outer')
speeding_counts_all = pd.merge(speeding_counts_all, speeding_counts_hour_road_pivot, on='hour', how='outer')

speeding_counts_all.to_csv(f"N:\\compass\\results_z\\summary_regroup\\{region}\\speeding1_byhour_{region}.csv", index=False)


speeding_mask = df_data['speed'] > df_data['speedLimit_mph']
speeding_count = speeding_mask.sum()
print(f"Total speeding count: {speeding_count}")

speeding_count_df = pd.DataFrame({'group': ['Total'], 'speeding': [speeding_count]})

speeding_counts_spl = df_data.groupby('speedLimit_group').apply(count_speeding_events).reset_index()
speeding_counts_spl.columns = ['group', 'speeding']
print(speeding_counts_spl)

speeding_counts_road = df_data.groupby('routehierarchy_group').apply(count_speeding_events).reset_index()
print(speeding_counts_road)

exist_levels = [level for level in road_levels if level in speeding_counts_road['routehierarchy_group'].unique()]
speeding_counts_road['routehierarchy_group'] = pd.Categorical(speeding_counts_road['routehierarchy_group'], categories=exist_levels, ordered=True)
speeding_counts_road = speeding_counts_road.sort_values('routehierarchy_group')
speeding_counts_road.columns = ['group', 'speeding']

speeding_counts_combined1 = pd.concat([speeding_count_df, speeding_counts_spl, speeding_counts_road], ignore_index=True)


speed_limit_pointcounts = df_data['speedLimit_group'].value_counts().reset_index(name='pointcount')
speed_limit_pointcounts = speed_limit_pointcounts.sort_values('speedLimit_group')
speed_limit_pointcounts.columns = ['group', 'pointcount']
print(speed_limit_pointcounts)

total_pointcounts = len(df_data)
total_pointcounts_row = pd.DataFrame({'group': ['Total'], 'pointcount': [total_pointcounts]})

route_hierarchy_pointcounts = df_data['routehierarchy_group'].value_counts().reset_index(name='pointcount')
print(route_hierarchy_pointcounts)

exist_levels = [level for level in road_levels if level in route_hierarchy_pointcounts['routehierarchy_group'].unique()]
route_hierarchy_pointcounts['routehierarchy_group'] = pd.Categorical(route_hierarchy_pointcounts['routehierarchy_group'], categories=exist_levels, ordered=True)
route_hierarchy_pointcounts = route_hierarchy_pointcounts.sort_values('routehierarchy_group')
route_hierarchy_pointcounts.columns = ['group', 'pointcount']

speed_limit_pointcounts_combined1 = pd.concat([total_pointcounts_row, speed_limit_pointcounts, 
                                              route_hierarchy_pointcounts], ignore_index=True)

speed_limit_pointcounts_combined1['point_pct'] = (speed_limit_pointcounts_combined1['pointcount'] / total_pointcounts) * 100
speed_limit_pointcounts_combined1['point_pct'] = round(speed_limit_pointcounts_combined1['point_pct'], 2)


combined_df = pd.merge(speeding_counts_combined, speed_limit_pointcounts_combined, on='group', how='inner')
combined_df = pd.merge(combined_df, linkpointcounts_combined, on='group', how='inner')
combined_df = pd.merge(combined_df, linkcount_combined, on='group', how='inner')
combined_df = pd.merge(combined_df, linklength_combined, on='group', how='inner')
combined_df.to_csv(f"N:\\compass\\results_z\\summary_regroup\\{region}\\summary_regroup_{region}.csv", index=False)

combined_df1 = pd.merge(speeding_counts_combined1, speed_limit_pointcounts_combined1, on='group', how='inner')
combined_df1 = pd.merge(combined_df1, linkpointcounts_combined1, on='group', how='inner')
combined_df1 = pd.merge(combined_df1, linkcount_combined1, on='group', how='inner')
combined_df1 = pd.merge(combined_df1, linklength_combined1, on='group', how='inner')
combined_df1.to_csv(f"N:\\compass\\results_z\\summary_regroup\\{region}\\summary1_regroup_{region}.csv", index=False)





# re-group new 5, 10, 15, 20 -> 20 mph, including adherence rate and speeding. 
#%%
import os
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, MetaData, select, text, func
import dask.dataframe as dd
import gc

# connect to postgresql database
dbname = "compass_db"
user = "compass_user"
password = "postgres"
host = "localhost"
port = "5432"

conn_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
db_engine = create_engine(conn_string)

# region = "London"
# region = "Oxford"
# region = "Cambridge"
# region = "WestEngland"
# region = "Cardiff"
# region = "SouthYorkshire"
# region = "Manchester"
# region = "WestYorkshire"
# region = "Glasgow"
# region = "Liverpool"
# region = "Newcastle"
region = "Edinburgh"
# region = "WestMidlands"

table_name = f'{region}_match'

InputPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1.gpkg"
link_layer = "RoadLink1x"
gdflink = gpd.read_file(filename=InputPath, layer=link_layer)

print(gdflink.shape)
print(gdflink['TOID'].nunique())
print(gdflink.columns)

print(gdflink.isna().sum())

speed_limit_mapping = {
    5: '20',
    10: '20',
    15: '20',
    20: '20',
    30: '30',
    40: '40',
    50: '50',
    60: '60',
    70: '70'
    }

route_hierarchy_mapping = {
    'Motorway': 'Motorway', 
    'A Road Primary': 'A Road', 
    'A Road': 'A Road', 
    'B Road': 'B Road', 
    'Local Road': 'Local Road', 
    'Minor Road': 'Minor Road', 
    'Secondary Access Road': 'Others', 
    'Local Access Road': 'Others', 
    'Restricted Secondary Access Road': 'Others', 
    'Restricted Local Access Road': 'Others'
    }


gdflink['speedLimit_group'] = gdflink['speedLimit_mph'].map(speed_limit_mapping)
gdflink['routehierarchy_group'] = gdflink['routehierarchy'].map(route_hierarchy_mapping)

print(gdflink.isna().sum())

out_path = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1_regroup.gpkg"
out_layer = "RoadLinkz1"
gdflink.to_file(filename=out_path, layer=out_layer, driver="GPKG")


gdflink = gdflink.dropna(subset=['speedLimit_mph']).reset_index(drop=True)
print(gdflink.shape)
print(gdflink['TOID'].nunique())
print(gdflink.columns)
print(gdflink['speedLimit_group'].unique())
print(gdflink['routehierarchy_group'].unique())

gdflink_m = gdflink[['TOID', 'speedLimit_mph', 'speedLimit_group', 'routehierarchy_group']]
gdflink_m = dd.from_pandas(gdflink_m, npartitions=1)


metadata = MetaData()
metadata.reflect(bind=db_engine)
table = metadata.tables[table_name]
columns = table.columns.keys()
print(columns)

query = select(
    table.c.agent_id,
    table.c.time,
    table.c.speed,
    table.c.acc_speed,
    table.c.TOID
    )

chunks = []
with db_engine.connect() as conn:
    for chunk in pd.read_sql(query, conn, chunksize=2000000):
        chunk['index_col'] = chunk.index
        chunks.append(chunk)
    
df_data_pd = pd.concat(chunks, ignore_index=True)
print(df_data_pd.shape)

df_data = dd.from_pandas(df_data_pd, npartitions=10)
print(df_data.shape[0].compute())

del chunks, df_data_pd
gc.collect()

df_data['time'] = dd.to_datetime(df_data['time'], format='ISO8601')
df_data['time'] = df_data['time'].dt.strftime("%Y-%m-%d %H:%M:%S")
df_data['hour'] = dd.to_datetime(df_data['time']).dt.hour

df_data = df_data.merge(gdflink_m, on='TOID', how='inner')
df_data = df_data.persist()

print(df_data.columns)
print(df_data.isna().sum().compute())
print(df_data.shape[0].compute())

df_data = df_data.compute()
print(df_data.shape)
print(df_data['hour'].unique())

with db_engine.connect() as conn:
    total_rows = conn.execute(select(func.count()).select_from(table)).scalar()
    
print("Total Rows:", total_rows)

csv_dir = f"N:\\compass\\results_z1\\summary_regroup\\{region}\\"
os.makedirs(csv_dir, exist_ok=True)


def calculate_adherence_rate(group):
    adherent_pt = group[group['speed'] <= group['speedLimit_mph']].shape[0]
    total_pt = group.shape[0]
    adherence_rate = (adherent_pt / total_pt if total_pt > 0 else 0) * 100
    adherence_rate = round(adherence_rate, 2)
    return adherence_rate


# adherence rates
adherence_rates_hour = df_data.groupby('hour').apply(calculate_adherence_rate).reset_index(name=f'adhrate_Total_{region}')
# print(adherence_rates_hour)

adherence_rates_hour_speed = df_data.groupby(['speedLimit_group', 'hour']).apply(calculate_adherence_rate).reset_index(name='adhrate')
# print(adherence_rates_hour_speed)

adherence_rates_hour_speed_pivot = adherence_rates_hour_speed.pivot(index='hour', columns='speedLimit_group', values='adhrate')
adherence_rates_hour_speed_pivot.columns = [f'adhrate_{col}_{region}' for col in adherence_rates_hour_speed_pivot.columns]             
# print(adherence_rates_hour_speed_pivot)

adherence_rates_hour_road = df_data.groupby(['routehierarchy_group', 'hour']).apply(calculate_adherence_rate).reset_index(name='adhrate')
# print(adherence_rates_hour_road)

adherence_rates_hour_road_pivot =adherence_rates_hour_road.pivot(index='hour', columns='routehierarchy_group', values='adhrate')
adherence_rates_hour_road_pivot.columns = [f'adhrate_{col}_{region}' for col in adherence_rates_hour_road_pivot.columns]
# print(adherence_rates_hour_road_pivot)

adherence_rates_all = pd.merge(adherence_rates_hour, adherence_rates_hour_speed_pivot, on='hour', how='outer')
adherence_rates_all = pd.merge(adherence_rates_all, adherence_rates_hour_road_pivot, on='hour', how='outer')

adherence_rates_all.to_csv(f"N:\\compass\\results_z1\\summary_regroup\\{region}\\adhrate_byhour_{region}.csv", index=False)


adherence_mask = df_data['speed'] < df_data['speedLimit_mph']
adherence_count = adherence_mask.sum()
adherence_rate = (adherence_count / len(df_data)) * 100
adherence_rate = round(adherence_rate, 2)
# print(f"Total adherence rate: {adherence_rate}")

adherence_rate_df = pd.DataFrame({'group': ['Total'], 'adhrate': [adherence_rate]})

adherence_rates_spl = df_data.groupby('speedLimit_group').apply(calculate_adherence_rate).reset_index()
adherence_rates_spl.columns = ['group', 'adhrate']
# print(adherence_rates_spl)

road_levels = ["Motorway", "A Road", "B Road", "Local Road", "Minor Road", "Others"]

adherence_rates_road = df_data.groupby('routehierarchy_group').apply(calculate_adherence_rate).reset_index()
# print(adherence_rates_road)

exist_levels = [level for level in road_levels if level in adherence_rates_road['routehierarchy_group'].unique()]
adherence_rates_road['routehierarchy_group'] = pd.Categorical(adherence_rates_road['routehierarchy_group'], categories=exist_levels, ordered=True)
adherence_rates_road = adherence_rates_road.sort_values('routehierarchy_group')
adherence_rates_road.columns = ['group', 'adhrate']

adherence_rates_combined = pd.concat([adherence_rate_df, adherence_rates_spl, adherence_rates_road], ignore_index=True)


def count_speeding_events(group):
    speeding_pt_count = group[group['speed'] > group['speedLimit_mph']].shape[0]
    return speeding_pt_count


# speeding counts
speeding_counts_hour = df_data.groupby('hour').apply(count_speeding_events).reset_index(name=f'speeding_Total_{region}')
# print(speeding_counts_hour)

speeding_counts_hour_speed = df_data.groupby(['speedLimit_group', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
# print(speeding_counts_hour_speed)

speeding_counts_hour_speed_pivot = speeding_counts_hour_speed.pivot(index='hour', columns='speedLimit_group', values='speeding')
speeding_counts_hour_speed_pivot.columns = [f'speeding_{col}_{region}' for col in speeding_counts_hour_speed_pivot.columns]             
# print(speeding_counts_hour_speed_pivot)

speeding_counts_hour_road = df_data.groupby(['routehierarchy_group', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
# print(speeding_counts_hour_road)

speeding_counts_hour_road_pivot = speeding_counts_hour_road.pivot(index='hour', columns='routehierarchy_group', values='speeding')
speeding_counts_hour_road_pivot.columns = [f'speeding_{col}_{region}' for col in speeding_counts_hour_road_pivot.columns]
# print(speeding_counts_hour_road_pivot)

speeding_counts_all = pd.merge(speeding_counts_hour, speeding_counts_hour_speed_pivot, on='hour', how='outer')
speeding_counts_all = pd.merge(speeding_counts_all, speeding_counts_hour_road_pivot, on='hour', how='outer')

speeding_counts_all.to_csv(f"N:\\compass\\results_z1\\summary_regroup\\{region}\\speeding_byhour_{region}.csv", index=False)

speeding_mask = df_data['speed'] > df_data['speedLimit_mph']
speeding_count = speeding_mask.sum()
# print(f"Total speeding count: {speeding_count}")

speeding_count_df = pd.DataFrame({'group': ['Total'], 'speeding': [speeding_count]})

speeding_counts_spl = df_data.groupby('speedLimit_group').apply(count_speeding_events).reset_index()
speeding_counts_spl.columns = ['group', 'speeding']
# print(speeding_counts_spl)

speeding_counts_road = df_data.groupby('routehierarchy_group').apply(count_speeding_events).reset_index()
# print(speeding_counts_road)

exist_levels = [level for level in road_levels if level in speeding_counts_road['routehierarchy_group'].unique()]
speeding_counts_road['routehierarchy_group'] = pd.Categorical(speeding_counts_road['routehierarchy_group'], categories=exist_levels, ordered=True)
speeding_counts_road = speeding_counts_road.sort_values('routehierarchy_group')
speeding_counts_road.columns = ['group', 'speeding']

speeding_counts_combined = pd.concat([speeding_count_df, speeding_counts_spl, speeding_counts_road], ignore_index=True)
speeding_counts_combined['speeding_pct'] = (speeding_counts_combined['speeding'] / speeding_count) * 100

# point counts
speed_limit_pointcounts = df_data['speedLimit_group'].value_counts().reset_index(name='pointcount')
speed_limit_pointcounts = speed_limit_pointcounts.sort_values('speedLimit_group')
speed_limit_pointcounts.columns = ['group', 'pointcount']
# print(speed_limit_pointcounts)

total_pointcounts = len(df_data)
total_pointcounts_row = pd.DataFrame({'group': ['Total'], 'pointcount': [total_pointcounts]})

route_hierarchy_pointcounts = df_data['routehierarchy_group'].value_counts().reset_index(name='pointcount')
# print(route_hierarchy_pointcounts)

exist_levels = [level for level in road_levels if level in route_hierarchy_pointcounts['routehierarchy_group'].unique()]
route_hierarchy_pointcounts['routehierarchy_group'] = pd.Categorical(route_hierarchy_pointcounts['routehierarchy_group'], categories=exist_levels, ordered=True)
route_hierarchy_pointcounts = route_hierarchy_pointcounts.sort_values('routehierarchy_group')
route_hierarchy_pointcounts.columns = ['group', 'pointcount']

speed_limit_pointcounts_combined = pd.concat([total_pointcounts_row, speed_limit_pointcounts, 
                                              route_hierarchy_pointcounts], ignore_index=True)

speed_limit_pointcounts_combined['point_pct'] = (speed_limit_pointcounts_combined['pointcount'] / total_pointcounts) * 100
speed_limit_pointcounts_combined['point_pct'] = round(speed_limit_pointcounts_combined['point_pct'], 2)

link_pointcountdf = df_data.groupby('TOID').size().reset_index(name='ptcount')
# print(link_pointcountdf.head())

gdflink = gdflink.merge(link_pointcountdf, on='TOID', how='left')

speeding_counts_roadid = df_data.groupby('TOID').apply(count_speeding_events).reset_index(name='link_speedingcount')
# print(speeding_counts_roadid.head())

gdflink = gdflink.merge(speeding_counts_roadid, on='TOID', how='left')
# print(gdflink.shape)
# print(gdflink.columns)

# print(gdflink['ptcount'].isnull().sum())
# print(gdflink['ptcount'].notnull().sum())
# print(gdflink[(gdflink['ptcount'] > 0) & (gdflink['ptcount'] < 5)].shape[0])

gdflink = gdflink.dropna(subset=['ptcount']).reset_index(drop=True)

out_path = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1_regroup_count.gpkg"
out_layer = "RoadLink1z1_q"
gdflink.to_file(filename=out_path, layer=out_layer, driver="GPKG")

gdflink1 = gdflink[(gdflink['ptcount'] >= 5)].reset_index(drop=True)
# print(gdflink1.shape[0])

out_path1 = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1_regroup_count.gpkg"
out_layer1 = "RoadLink1z1_q1"
gdflink1.to_file(filename=out_path1, layer=out_layer1, driver="GPKG")


# points count
total_ptcount = gdflink['ptcount'].sum()
total_ptcount_df = pd.DataFrame({'group': ['Total'], 'pointcount1': [total_ptcount]})

speedlimit_ptsum = gdflink.groupby('speedLimit_group')['ptcount'].sum().reset_index()
speedlimit_ptsum.columns = ['group', 'pointcount1']

routehierarchy_ptsum = gdflink.groupby('routehierarchy_group')['ptcount'].sum().reset_index()
routehierarchy_ptsum.columns = ['group', 'pointcount1']

exist_levels = [level for level in road_levels if level in routehierarchy_ptsum['group'].unique()]
routehierarchy_ptsum['group'] = pd.Categorical(routehierarchy_ptsum['group'], categories=exist_levels, ordered=True)
routehierarchy_ptsum = routehierarchy_ptsum.sort_values('group')

linkpointcounts_combined = pd.concat([total_ptcount_df, speedlimit_ptsum, routehierarchy_ptsum], ignore_index=True)
linkpointcounts_combined['point_pct1'] = (linkpointcounts_combined['pointcount1'] / total_ptcount) * 100
linkpointcounts_combined['point_pct1'] = round(linkpointcounts_combined['point_pct1'], 2)


total_ptcount1 = gdflink1['ptcount'].sum()
total_ptcount1_df = pd.DataFrame({'group': ['Total'], 'pointcount1': [total_ptcount1]})

speedlimit_ptsum1 = gdflink1.groupby('speedLimit_group')['ptcount'].sum().reset_index()
speedlimit_ptsum1.columns = ['group', 'pointcount1']

routehierarchy_ptsum1 = gdflink1.groupby('routehierarchy_group')['ptcount'].sum().reset_index()
routehierarchy_ptsum1.columns = ['group', 'pointcount1']

exist_levels = [level for level in road_levels if level in routehierarchy_ptsum1['group'].unique()]
routehierarchy_ptsum1['group'] = pd.Categorical(routehierarchy_ptsum1['group'], categories=exist_levels, ordered=True)
routehierarchy_ptsum1 = routehierarchy_ptsum1.sort_values('group')

linkpointcounts_combined1 = pd.concat([total_ptcount1_df, speedlimit_ptsum1, routehierarchy_ptsum1], ignore_index=True)
linkpointcounts_combined1['point_pct1'] = (linkpointcounts_combined1['pointcount1'] / total_ptcount1) * 100
linkpointcounts_combined1['point_pct1'] = round(linkpointcounts_combined1['point_pct1'], 2)


# count road link
# print(gdflink.shape)
# print(gdflink['TOID'].nunique())

total_toid_count = len(gdflink)
# print(total_toid_count)

toid_by_speedlimit = gdflink.groupby('speedLimit_group')['TOID'].count().reset_index()
toid_by_speedlimit.columns = ['group', 'linkcount']
toid_by_speedlimit['link_pct'] = (toid_by_speedlimit['linkcount'] / total_toid_count) * 100
toid_by_speedlimit['link_pct'] = round(toid_by_speedlimit['link_pct'], 2)

toid_by_route = gdflink.groupby('routehierarchy_group')['TOID'].count().reset_index()
toid_by_route.columns = ['group', 'linkcount']
toid_by_route['link_pct'] = (toid_by_route['linkcount'] / total_toid_count) * 100
toid_by_route['link_pct'] = round(toid_by_route['link_pct'], 2)

exist_levels = [level for level in road_levels if level in toid_by_route['group'].unique()]
toid_by_route['group'] = pd.Categorical(toid_by_route['group'], categories=exist_levels, ordered=True)
toid_by_route = toid_by_route.sort_values('group')

total_count_df = pd.DataFrame({'group': ['Total'], 'linkcount': total_toid_count, 'link_pct': 100.0})

linkcount_combined = pd.concat([total_count_df, toid_by_speedlimit, toid_by_route], ignore_index=True)

# print(gdflink1.shape)
# print(gdflink1['TOID'].nunique())

total_toid_count1 = len(gdflink1)
# print(total_toid_count1)

toid_by_speedlimit1 = gdflink1.groupby('speedLimit_group')['TOID'].count().reset_index()
toid_by_speedlimit1.columns = ['group', 'linkcount']
toid_by_speedlimit1['link_pct'] = (toid_by_speedlimit1['linkcount'] / total_toid_count1) * 100
toid_by_speedlimit1['link_pct'] = round(toid_by_speedlimit1['link_pct'], 2)

toid_by_route1 = gdflink1.groupby('routehierarchy_group')['TOID'].count().reset_index()
toid_by_route1.columns = ['group', 'linkcount']
toid_by_route1['link_pct'] = (toid_by_route1['linkcount'] / total_toid_count1) * 100
toid_by_route1['link_pct'] = round(toid_by_route1['link_pct'], 2)

exist_levels = [level for level in road_levels if level in toid_by_route1['group'].unique()]
toid_by_route1['group'] = pd.Categorical(toid_by_route1['group'], categories=exist_levels, ordered=True)
toid_by_route1 = toid_by_route1.sort_values('group')

total_count_df1 = pd.DataFrame({'group': ['Total'], 'linkcount': total_toid_count1, 'link_pct': 100.0})

linkcount_combined1 = pd.concat([total_count_df1, toid_by_speedlimit1, toid_by_route1], ignore_index=True)

# link length
gdflink['linklength'] = gdflink.geometry.length

lengthsum = gdflink['linklength'].sum()
linklength_total = pd.DataFrame({'group': ['Total'], 'linklength': [lengthsum], 'length_pct': 100.0})

speedlimit_lengthsum = gdflink.groupby('speedLimit_group')['linklength'].sum().reset_index()
routehierarchy_lengthsum = gdflink.groupby('routehierarchy_group')['linklength'].sum().reset_index()
# print(speedlimit_lengthsum)
# print(routehierarchy_lengthsum)

speedlimit_lengthsum.columns = ['group', 'linklength']
routehierarchy_lengthsum.columns = ['group', 'linklength']

exist_levels = [level for level in road_levels if level in routehierarchy_lengthsum['group'].unique()]
routehierarchy_lengthsum['group'] = pd.Categorical(routehierarchy_lengthsum['group'], categories=exist_levels, ordered=True)
routehierarchy_lengthsum = routehierarchy_lengthsum.sort_values('group')

speedlimit_lengthsum['length_pct'] = (speedlimit_lengthsum['linklength'] / lengthsum) * 100
speedlimit_lengthsum['length_pct'] = round(speedlimit_lengthsum['length_pct'], 2)
routehierarchy_lengthsum['length_pct'] = (routehierarchy_lengthsum['linklength'] / lengthsum) * 100
routehierarchy_lengthsum['length_pct'] = round(routehierarchy_lengthsum['length_pct'], 2)

linklength_combined = pd.concat([linklength_total, speedlimit_lengthsum, routehierarchy_lengthsum], ignore_index=True)
linklength_combined['linklength'] = linklength_combined['linklength'] / 1609.34
linklength_combined['linklength'] = round(linklength_combined['linklength'], 2)
# print(linklength_combined)

gdflink1['linklength'] = gdflink1.geometry.length

lengthsum = gdflink1['linklength'].sum()
linklength_total = pd.DataFrame({'group': ['Total'], 'linklength': [lengthsum], 'length_pct': 100.0})

speedlimit_lengthsum = gdflink1.groupby('speedLimit_group')['linklength'].sum().reset_index()
routehierarchy_lengthsum = gdflink1.groupby('routehierarchy_group')['linklength'].sum().reset_index()
# print(speedlimit_lengthsum)
# print(routehierarchy_lengthsum)

speedlimit_lengthsum.columns = ['group', 'linklength']
routehierarchy_lengthsum.columns = ['group', 'linklength']

exist_levels = [level for level in road_levels if level in routehierarchy_lengthsum['group'].unique()]
routehierarchy_lengthsum['group'] = pd.Categorical(routehierarchy_lengthsum['group'], categories=exist_levels, ordered=True)
routehierarchy_lengthsum = routehierarchy_lengthsum.sort_values('group')

speedlimit_lengthsum['length_pct'] = (speedlimit_lengthsum['linklength'] / lengthsum) * 100
speedlimit_lengthsum['length_pct'] = round(speedlimit_lengthsum['length_pct'], 2)
routehierarchy_lengthsum['length_pct'] = (routehierarchy_lengthsum['linklength'] / lengthsum) * 100
routehierarchy_lengthsum['length_pct'] = round(routehierarchy_lengthsum['length_pct'], 2)

linklength_combined1 = pd.concat([linklength_total, speedlimit_lengthsum, routehierarchy_lengthsum], ignore_index=True)
linklength_combined1['linklength'] = linklength_combined1['linklength'] / 1609.34
linklength_combined1['linklength'] = round(linklength_combined1['linklength'], 2)
# print(linklength_combined1)



# filtering df_data
df_data = dd.from_pandas(df_data, npartitions=10)

df_data = df_data[df_data['TOID'].isin(gdflink1['TOID'])]
df_data = df_data.persist()

print(df_data.columns)
print(df_data.isna().sum().compute())
print(df_data.shape[0].compute())

df_data = df_data.compute()
# print(df_data.shape)


adherence_rates_hour = df_data.groupby('hour').apply(calculate_adherence_rate).reset_index(name=f'adhrate_Total_{region}')
# print(adherence_rates_hour)

adherence_rates_hour_speed = df_data.groupby(['speedLimit_group', 'hour']).apply(calculate_adherence_rate).reset_index(name='adhrate')
# print(adherence_rates_hour_speed)

adherence_rates_hour_speed_pivot = adherence_rates_hour_speed.pivot(index='hour', columns='speedLimit_group', values='adhrate')
adherence_rates_hour_speed_pivot.columns = [f'adhrate_{col}_{region}' for col in adherence_rates_hour_speed_pivot.columns]             
# print(adherence_rates_hour_speed_pivot)

adherence_rates_hour_road = df_data.groupby(['routehierarchy_group', 'hour']).apply(calculate_adherence_rate).reset_index(name='adhrate')
# print(adherence_rates_hour_road)

adherence_rates_hour_road_pivot =adherence_rates_hour_road.pivot(index='hour', columns='routehierarchy_group', values='adhrate')
adherence_rates_hour_road_pivot.columns = [f'adhrate_{col}_{region}' for col in adherence_rates_hour_road_pivot.columns]
# print(adherence_rates_hour_road_pivot)

adherence_rates_all = pd.merge(adherence_rates_hour, adherence_rates_hour_speed_pivot, on='hour', how='outer')
adherence_rates_all = pd.merge(adherence_rates_all, adherence_rates_hour_road_pivot, on='hour', how='outer')

adherence_rates_all.to_csv(f"N:\\compass\\results_z1\\summary_regroup\\{region}\\adhrate1_byhour_{region}.csv", index=False)


adherence_mask = df_data['speed'] < df_data['speedLimit_mph']
adherence_count = adherence_mask.sum()
adherence_rate = (adherence_count / len(df_data)) * 100
adherence_rate = round(adherence_rate, 2)
# print(f"Total adherence rate: {adherence_rate}")

adherence_rate_df = pd.DataFrame({'group': ['Total'], 'adhrate': [adherence_rate]})

adherence_rates_spl = df_data.groupby('speedLimit_group').apply(calculate_adherence_rate).reset_index()
adherence_rates_spl.columns = ['group', 'adhrate']
# print(adherence_rates_spl)

adherence_rates_road = df_data.groupby('routehierarchy_group').apply(calculate_adherence_rate).reset_index()
# print(adherence_rates_road)

exist_levels = [level for level in road_levels if level in adherence_rates_road['routehierarchy_group'].unique()]
adherence_rates_road['routehierarchy_group'] = pd.Categorical(adherence_rates_road['routehierarchy_group'], categories=exist_levels, ordered=True)
adherence_rates_road = adherence_rates_road.sort_values('routehierarchy_group')
adherence_rates_road.columns = ['group', 'adhrate']

adherence_rates_combined1 = pd.concat([adherence_rate_df, adherence_rates_spl, adherence_rates_road], ignore_index=True)


speeding_counts_hour = df_data.groupby('hour').apply(count_speeding_events).reset_index(name=f'speeding_Total_{region}')
# print(speeding_counts_hour)

speeding_counts_hour_speed = df_data.groupby(['speedLimit_group', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
# print(speeding_counts_hour_speed)

speeding_counts_hour_speed_pivot = speeding_counts_hour_speed.pivot(index='hour', columns='speedLimit_group', values='speeding')
speeding_counts_hour_speed_pivot.columns = [f'speeding_{col}_{region}' for col in speeding_counts_hour_speed_pivot.columns]             
# print(speeding_counts_hour_speed_pivot)

speeding_counts_hour_road = df_data.groupby(['routehierarchy_group', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
# print(speeding_counts_hour_road)

speeding_counts_hour_road_pivot = speeding_counts_hour_road.pivot(index='hour', columns='routehierarchy_group', values='speeding')
speeding_counts_hour_road_pivot.columns = [f'speeding_{col}_{region}' for col in speeding_counts_hour_road_pivot.columns]
# print(speeding_counts_hour_road_pivot)

speeding_counts_all = pd.merge(speeding_counts_hour, speeding_counts_hour_speed_pivot, on='hour', how='outer')
speeding_counts_all = pd.merge(speeding_counts_all, speeding_counts_hour_road_pivot, on='hour', how='outer')

speeding_counts_all.to_csv(f"N:\\compass\\results_z1\\summary_regroup\\{region}\\speeding1_byhour_{region}.csv", index=False)


speeding_mask = df_data['speed'] > df_data['speedLimit_mph']
speeding_count = speeding_mask.sum()
# print(f"Total speeding count: {speeding_count}")

speeding_count_df = pd.DataFrame({'group': ['Total'], 'speeding': [speeding_count]})

speeding_counts_spl = df_data.groupby('speedLimit_group').apply(count_speeding_events).reset_index()
speeding_counts_spl.columns = ['group', 'speeding']
# print(speeding_counts_spl)

speeding_counts_road = df_data.groupby('routehierarchy_group').apply(count_speeding_events).reset_index()
# print(speeding_counts_road)

exist_levels = [level for level in road_levels if level in speeding_counts_road['routehierarchy_group'].unique()]
speeding_counts_road['routehierarchy_group'] = pd.Categorical(speeding_counts_road['routehierarchy_group'], categories=exist_levels, ordered=True)
speeding_counts_road = speeding_counts_road.sort_values('routehierarchy_group')
speeding_counts_road.columns = ['group', 'speeding']

speeding_counts_combined1 = pd.concat([speeding_count_df, speeding_counts_spl, speeding_counts_road], ignore_index=True)
speeding_counts_combined1['speeding_pct'] = (speeding_counts_combined1['speeding'] / speeding_count) * 100


speed_limit_pointcounts = df_data['speedLimit_group'].value_counts().reset_index(name='pointcount')
speed_limit_pointcounts = speed_limit_pointcounts.sort_values('speedLimit_group')
speed_limit_pointcounts.columns = ['group', 'pointcount']
# print(speed_limit_pointcounts)

total_pointcounts = len(df_data)
total_pointcounts_row = pd.DataFrame({'group': ['Total'], 'pointcount': [total_pointcounts]})

route_hierarchy_pointcounts = df_data['routehierarchy_group'].value_counts().reset_index(name='pointcount')
# print(route_hierarchy_pointcounts)

exist_levels = [level for level in road_levels if level in route_hierarchy_pointcounts['routehierarchy_group'].unique()]
route_hierarchy_pointcounts['routehierarchy_group'] = pd.Categorical(route_hierarchy_pointcounts['routehierarchy_group'], categories=exist_levels, ordered=True)
route_hierarchy_pointcounts = route_hierarchy_pointcounts.sort_values('routehierarchy_group')
route_hierarchy_pointcounts.columns = ['group', 'pointcount']

speed_limit_pointcounts_combined1 = pd.concat([total_pointcounts_row, speed_limit_pointcounts, 
                                              route_hierarchy_pointcounts], ignore_index=True)

speed_limit_pointcounts_combined1['point_pct'] = (speed_limit_pointcounts_combined1['pointcount'] / total_pointcounts) * 100
speed_limit_pointcounts_combined1['point_pct'] = round(speed_limit_pointcounts_combined1['point_pct'], 2)


combined_df = pd.merge(adherence_rates_combined, speeding_counts_combined, on='group', how='inner')
combined_df = pd.merge(combined_df, speed_limit_pointcounts_combined, on='group', how='inner')
combined_df = pd.merge(combined_df, linkpointcounts_combined, on='group', how='inner')
combined_df = pd.merge(combined_df, linkcount_combined, on='group', how='inner')
combined_df = pd.merge(combined_df, linklength_combined, on='group', how='inner')

combined_df['normalised_speeding'] = round((combined_df['speeding'] / combined_df['linklength']), 2)
combined_df['speeding_perlink'] = round((combined_df['speeding'] / combined_df['linkcount']), 2)
combined_df['length_perlink'] = round((combined_df['linklength'] / combined_df['linkcount']), 4)
combined_df.to_csv(f"N:\\compass\\results_z1\\summary_regroup\\{region}\\summary_regroup_{region}.csv", index=False)


combined_df1 = pd.merge(adherence_rates_combined1, speeding_counts_combined1, on='group', how='inner')
combined_df1 = pd.merge(combined_df1, speed_limit_pointcounts_combined1, on='group', how='inner')
combined_df1 = pd.merge(combined_df1, linkpointcounts_combined1, on='group', how='inner')
combined_df1 = pd.merge(combined_df1, linkcount_combined1, on='group', how='inner')
combined_df1 = pd.merge(combined_df1, linklength_combined1, on='group', how='inner')

combined_df1['normalised_speeding'] = round((combined_df1['speeding'] / combined_df1['linklength']), 2)
combined_df1['speeding_perlink'] = round((combined_df1['speeding'] / combined_df1['linkcount']), 2)
combined_df1['length_perlink'] = round((combined_df1['linklength'] / combined_df1['linkcount']), 4)
combined_df1.to_csv(f"N:\\compass\\results_z1\\summary_regroup\\{region}\\summary1_regroup_{region}.csv", index=False)





# re-group new 5, 10, 15, 20 -> 20 mph, including adherence rate and speeding. 
# and only include single and dual ways
#%%
import os
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, MetaData, select, text, func
import dask.dataframe as dd
import gc

# connect to postgresql database
dbname = "compass_db"
user = "compass_user"
password = "postgres"
host = "localhost"
port = "5432"

conn_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
db_engine = create_engine(conn_string)

# region = "London"
# region = "Oxford"
# region = "Cambridge"
# region = "WestEngland"
# region = "Cardiff"
# region = "SouthYorkshire"
# region = "Manchester"
# region = "WestYorkshire"
# region = "Glasgow"
# region = "Liverpool"
# region = "Newcastle"
region = "Edinburgh"
# region = "WestMidlands"

table_name = f'{region}_match'

RawLinkPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads.gpkg"
RawLinkLayer = "RoadLink"

gdflink_raw = gpd.read_file(filename=RawLinkPath, layer=RawLinkLayer)

print(gdflink_raw.shape)
print(gdflink_raw['TOID'].nunique())
print(gdflink_raw['formofway'].unique())

gdflink_rawdata = gdflink_raw[['TOID', 'formofway']]
print(gdflink_rawdata.isna().sum())

InputPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1.gpkg"
link_layer = "RoadLink1x"
gdflink = gpd.read_file(filename=InputPath, layer=link_layer)

print(gdflink.shape)

gdflink = gdflink.merge(gdflink_rawdata, on='TOID', how='left')

print(gdflink.shape)
print(gdflink['TOID'].nunique())
print(gdflink.columns)

# print(gdflink.isna().sum())

speed_limit_mapping = {
    5: '20',
    10: '20',
    15: '20',
    20: '20',
    30: '30',
    40: '40',
    50: '50',
    60: '60',
    70: '70'
    }

route_hierarchy_mapping = {
    'Motorway': 'Motorway', 
    'A Road Primary': 'A Road', 
    'A Road': 'A Road', 
    'B Road': 'B Road', 
    'Local Road': 'Local Road', 
    'Minor Road': 'Minor Road', 
    'Secondary Access Road': 'Others', 
    'Local Access Road': 'Others', 
    'Restricted Secondary Access Road': 'Others', 
    'Restricted Local Access Road': 'Others'
    }


gdflink['speedLimit_group'] = gdflink['speedLimit_mph'].map(speed_limit_mapping)
gdflink['routehierarchy_group'] = gdflink['routehierarchy'].map(route_hierarchy_mapping)

# print(gdflink.isna().sum())

out_path = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1_regroup.gpkg"
out_layer = "RoadLinkz2"
gdflink.to_file(filename=out_path, layer=out_layer, driver="GPKG")


gdflink = gdflink.dropna(subset=['speedLimit_mph']).reset_index(drop=True)
print(gdflink.shape)
print(gdflink['TOID'].nunique())
print(gdflink.columns)
print(gdflink['speedLimit_group'].unique())
print(gdflink['routehierarchy_group'].unique())

gdflink_m = gdflink[['TOID', 'speedLimit_mph', 'speedLimit_group', 'routehierarchy_group', 'formofway']]
print(gdflink_m.shape)

gdflink_m = gdflink_m[gdflink_m['formofway'].isin(['Single Carriageway', 'Dual Carriageway'])]
print(gdflink_m.shape)
gdflink_m = dd.from_pandas(gdflink_m, npartitions=1)


metadata = MetaData()
metadata.reflect(bind=db_engine)
table = metadata.tables[table_name]
columns = table.columns.keys()
print(columns)

query = select(
    table.c.agent_id,
    table.c.time,
    table.c.speed,
    table.c.acc_speed,
    table.c.TOID
    )

chunks = []
with db_engine.connect() as conn:
    for chunk in pd.read_sql(query, conn, chunksize=2000000):
        chunk['index_col'] = chunk.index
        chunks.append(chunk)
    
df_data_pd = pd.concat(chunks, ignore_index=True)
print(df_data_pd.shape)

df_data = dd.from_pandas(df_data_pd, npartitions=10)
print(df_data.shape[0].compute())

del chunks, df_data_pd
gc.collect()

df_data['time'] = dd.to_datetime(df_data['time'], format='ISO8601')
df_data['time'] = df_data['time'].dt.strftime("%Y-%m-%d %H:%M:%S")
df_data['hour'] = dd.to_datetime(df_data['time']).dt.hour

df_data = df_data.merge(gdflink_m, on='TOID', how='inner')
df_data = df_data.persist()

print(df_data.columns)
print(df_data.isna().sum().compute())
print(df_data.shape[0].compute())

df_data = df_data.compute()
print(df_data.shape)
print(df_data['hour'].unique())

with db_engine.connect() as conn:
    total_rows = conn.execute(select(func.count()).select_from(table)).scalar()
    
print("Total Rows:", total_rows)


csv_dir = f"N:\\compass\\results_z2\\summary_regroup\\{region}\\"
os.makedirs(csv_dir, exist_ok=True)


def calculate_adherence_rate(group):
    adherent_pt = group[group['speed'] <= group['speedLimit_mph']].shape[0]
    total_pt = group.shape[0]
    adherence_rate = (adherent_pt / total_pt if total_pt > 0 else 0) * 100
    adherence_rate = round(adherence_rate, 2)
    return adherence_rate


# adherence rates
adherence_rates_hour = df_data.groupby('hour').apply(calculate_adherence_rate).reset_index(name=f'adhrate_Total_{region}')
# print(adherence_rates_hour)

adherence_rates_hour_speed = df_data.groupby(['speedLimit_group', 'hour']).apply(calculate_adherence_rate).reset_index(name='adhrate')
# print(adherence_rates_hour_speed)

adherence_rates_hour_speed_pivot = adherence_rates_hour_speed.pivot(index='hour', columns='speedLimit_group', values='adhrate')
adherence_rates_hour_speed_pivot.columns = [f'adhrate_{col}_{region}' for col in adherence_rates_hour_speed_pivot.columns]             
# print(adherence_rates_hour_speed_pivot)

adherence_rates_hour_road = df_data.groupby(['routehierarchy_group', 'hour']).apply(calculate_adherence_rate).reset_index(name='adhrate')
# print(adherence_rates_hour_road)

adherence_rates_hour_road_pivot =adherence_rates_hour_road.pivot(index='hour', columns='routehierarchy_group', values='adhrate')
adherence_rates_hour_road_pivot.columns = [f'adhrate_{col}_{region}' for col in adherence_rates_hour_road_pivot.columns]
# print(adherence_rates_hour_road_pivot)

adherence_rates_all = pd.merge(adherence_rates_hour, adherence_rates_hour_speed_pivot, on='hour', how='outer')
adherence_rates_all = pd.merge(adherence_rates_all, adherence_rates_hour_road_pivot, on='hour', how='outer')

adherence_rates_all.to_csv(f"N:\\compass\\results_z2\\summary_regroup\\{region}\\adhrate_byhour_{region}.csv", index=False)


adherence_mask = df_data['speed'] < df_data['speedLimit_mph']
adherence_count = adherence_mask.sum()
adherence_rate = (adherence_count / len(df_data)) * 100
adherence_rate = round(adherence_rate, 2)
# print(f"Total adherence rate: {adherence_rate}")

adherence_rate_df = pd.DataFrame({'group': ['Total'], 'adhrate': [adherence_rate]})

adherence_rates_spl = df_data.groupby('speedLimit_group').apply(calculate_adherence_rate).reset_index()
adherence_rates_spl.columns = ['group', 'adhrate']
# print(adherence_rates_spl)

road_levels = ["Motorway", "A Road", "B Road", "Local Road", "Minor Road", "Others"]

adherence_rates_road = df_data.groupby('routehierarchy_group').apply(calculate_adherence_rate).reset_index()
# print(adherence_rates_road)

exist_levels = [level for level in road_levels if level in adherence_rates_road['routehierarchy_group'].unique()]
adherence_rates_road['routehierarchy_group'] = pd.Categorical(adherence_rates_road['routehierarchy_group'], categories=exist_levels, ordered=True)
adherence_rates_road = adherence_rates_road.sort_values('routehierarchy_group')
adherence_rates_road.columns = ['group', 'adhrate']

adherence_rates_combined = pd.concat([adherence_rate_df, adherence_rates_spl, adherence_rates_road], ignore_index=True)


def count_speeding_events(group):
    speeding_pt_count = group[group['speed'] > group['speedLimit_mph']].shape[0]
    return speeding_pt_count


# speeding counts
speeding_counts_hour = df_data.groupby('hour').apply(count_speeding_events).reset_index(name=f'speeding_Total_{region}')
# print(speeding_counts_hour)

speeding_counts_hour_speed = df_data.groupby(['speedLimit_group', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
# print(speeding_counts_hour_speed)

speeding_counts_hour_speed_pivot = speeding_counts_hour_speed.pivot(index='hour', columns='speedLimit_group', values='speeding')
speeding_counts_hour_speed_pivot.columns = [f'speeding_{col}_{region}' for col in speeding_counts_hour_speed_pivot.columns]             
# print(speeding_counts_hour_speed_pivot)

speeding_counts_hour_road = df_data.groupby(['routehierarchy_group', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
# print(speeding_counts_hour_road)

speeding_counts_hour_road_pivot = speeding_counts_hour_road.pivot(index='hour', columns='routehierarchy_group', values='speeding')
speeding_counts_hour_road_pivot.columns = [f'speeding_{col}_{region}' for col in speeding_counts_hour_road_pivot.columns]
# print(speeding_counts_hour_road_pivot)

speeding_counts_all = pd.merge(speeding_counts_hour, speeding_counts_hour_speed_pivot, on='hour', how='outer')
speeding_counts_all = pd.merge(speeding_counts_all, speeding_counts_hour_road_pivot, on='hour', how='outer')

speeding_counts_all.to_csv(f"N:\\compass\\results_z2\\summary_regroup\\{region}\\speeding_byhour_{region}.csv", index=False)

speeding_mask = df_data['speed'] > df_data['speedLimit_mph']
speeding_count = speeding_mask.sum()
# print(f"Total speeding count: {speeding_count}")

speeding_count_df = pd.DataFrame({'group': ['Total'], 'speeding': [speeding_count]})

speeding_counts_spl = df_data.groupby('speedLimit_group').apply(count_speeding_events).reset_index()
speeding_counts_spl.columns = ['group', 'speeding']
# print(speeding_counts_spl)

speeding_counts_road = df_data.groupby('routehierarchy_group').apply(count_speeding_events).reset_index()
# print(speeding_counts_road)

exist_levels = [level for level in road_levels if level in speeding_counts_road['routehierarchy_group'].unique()]
speeding_counts_road['routehierarchy_group'] = pd.Categorical(speeding_counts_road['routehierarchy_group'], categories=exist_levels, ordered=True)
speeding_counts_road = speeding_counts_road.sort_values('routehierarchy_group')
speeding_counts_road.columns = ['group', 'speeding']

speeding_counts_combined = pd.concat([speeding_count_df, speeding_counts_spl, speeding_counts_road], ignore_index=True)
speeding_counts_combined['speeding_pct'] = (speeding_counts_combined['speeding'] / speeding_count) * 100

# point counts
speed_limit_pointcounts = df_data['speedLimit_group'].value_counts().reset_index(name='pointcount')
speed_limit_pointcounts = speed_limit_pointcounts.sort_values('speedLimit_group')
speed_limit_pointcounts.columns = ['group', 'pointcount']
# print(speed_limit_pointcounts)

total_pointcounts = len(df_data)
total_pointcounts_row = pd.DataFrame({'group': ['Total'], 'pointcount': [total_pointcounts]})

route_hierarchy_pointcounts = df_data['routehierarchy_group'].value_counts().reset_index(name='pointcount')
# print(route_hierarchy_pointcounts)

exist_levels = [level for level in road_levels if level in route_hierarchy_pointcounts['routehierarchy_group'].unique()]
route_hierarchy_pointcounts['routehierarchy_group'] = pd.Categorical(route_hierarchy_pointcounts['routehierarchy_group'], categories=exist_levels, ordered=True)
route_hierarchy_pointcounts = route_hierarchy_pointcounts.sort_values('routehierarchy_group')
route_hierarchy_pointcounts.columns = ['group', 'pointcount']

speed_limit_pointcounts_combined = pd.concat([total_pointcounts_row, speed_limit_pointcounts, 
                                              route_hierarchy_pointcounts], ignore_index=True)

speed_limit_pointcounts_combined['point_pct'] = (speed_limit_pointcounts_combined['pointcount'] / total_pointcounts) * 100
speed_limit_pointcounts_combined['point_pct'] = round(speed_limit_pointcounts_combined['point_pct'], 2)

link_pointcountdf = df_data.groupby('TOID').size().reset_index(name='ptcount')
# print(link_pointcountdf.head())

gdflink = gdflink.merge(link_pointcountdf, on='TOID', how='left')

speeding_counts_roadid = df_data.groupby('TOID').apply(count_speeding_events).reset_index(name='link_speedingcount')
# print(speeding_counts_roadid.head())

gdflink = gdflink.merge(speeding_counts_roadid, on='TOID', how='left')
# print(gdflink.shape)
# print(gdflink.columns)

# print(gdflink['ptcount'].isnull().sum())
# print(gdflink['ptcount'].notnull().sum())
# print(gdflink[(gdflink['ptcount'] > 0) & (gdflink['ptcount'] < 5)].shape[0])

gdflink = gdflink.dropna(subset=['ptcount']).reset_index(drop=True)

out_path = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1_regroup_count.gpkg"
out_layer = "RoadLink1z2_q"
gdflink.to_file(filename=out_path, layer=out_layer, driver="GPKG")

gdflink1 = gdflink[(gdflink['ptcount'] >= 5)].reset_index(drop=True)
# print(gdflink1.shape[0])

out_path1 = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1_regroup_count.gpkg"
out_layer1 = "RoadLink1z2_q1"
gdflink1.to_file(filename=out_path1, layer=out_layer1, driver="GPKG")


# points count
total_ptcount = gdflink['ptcount'].sum()
total_ptcount_df = pd.DataFrame({'group': ['Total'], 'pointcount1': [total_ptcount]})

speedlimit_ptsum = gdflink.groupby('speedLimit_group')['ptcount'].sum().reset_index()
speedlimit_ptsum.columns = ['group', 'pointcount1']

routehierarchy_ptsum = gdflink.groupby('routehierarchy_group')['ptcount'].sum().reset_index()
routehierarchy_ptsum.columns = ['group', 'pointcount1']

exist_levels = [level for level in road_levels if level in routehierarchy_ptsum['group'].unique()]
routehierarchy_ptsum['group'] = pd.Categorical(routehierarchy_ptsum['group'], categories=exist_levels, ordered=True)
routehierarchy_ptsum = routehierarchy_ptsum.sort_values('group')

linkpointcounts_combined = pd.concat([total_ptcount_df, speedlimit_ptsum, routehierarchy_ptsum], ignore_index=True)
linkpointcounts_combined['point_pct1'] = (linkpointcounts_combined['pointcount1'] / total_ptcount) * 100
linkpointcounts_combined['point_pct1'] = round(linkpointcounts_combined['point_pct1'], 2)


total_ptcount1 = gdflink1['ptcount'].sum()
total_ptcount1_df = pd.DataFrame({'group': ['Total'], 'pointcount1': [total_ptcount1]})

speedlimit_ptsum1 = gdflink1.groupby('speedLimit_group')['ptcount'].sum().reset_index()
speedlimit_ptsum1.columns = ['group', 'pointcount1']

routehierarchy_ptsum1 = gdflink1.groupby('routehierarchy_group')['ptcount'].sum().reset_index()
routehierarchy_ptsum1.columns = ['group', 'pointcount1']

exist_levels = [level for level in road_levels if level in routehierarchy_ptsum1['group'].unique()]
routehierarchy_ptsum1['group'] = pd.Categorical(routehierarchy_ptsum1['group'], categories=exist_levels, ordered=True)
routehierarchy_ptsum1 = routehierarchy_ptsum1.sort_values('group')

linkpointcounts_combined1 = pd.concat([total_ptcount1_df, speedlimit_ptsum1, routehierarchy_ptsum1], ignore_index=True)
linkpointcounts_combined1['point_pct1'] = (linkpointcounts_combined1['pointcount1'] / total_ptcount1) * 100
linkpointcounts_combined1['point_pct1'] = round(linkpointcounts_combined1['point_pct1'], 2)


# count road link
# print(gdflink.shape)
# print(gdflink['TOID'].nunique())

total_toid_count = len(gdflink)
# print(total_toid_count)

toid_by_speedlimit = gdflink.groupby('speedLimit_group')['TOID'].count().reset_index()
toid_by_speedlimit.columns = ['group', 'linkcount']
toid_by_speedlimit['link_pct'] = (toid_by_speedlimit['linkcount'] / total_toid_count) * 100
toid_by_speedlimit['link_pct'] = round(toid_by_speedlimit['link_pct'], 2)

toid_by_route = gdflink.groupby('routehierarchy_group')['TOID'].count().reset_index()
toid_by_route.columns = ['group', 'linkcount']
toid_by_route['link_pct'] = (toid_by_route['linkcount'] / total_toid_count) * 100
toid_by_route['link_pct'] = round(toid_by_route['link_pct'], 2)

exist_levels = [level for level in road_levels if level in toid_by_route['group'].unique()]
toid_by_route['group'] = pd.Categorical(toid_by_route['group'], categories=exist_levels, ordered=True)
toid_by_route = toid_by_route.sort_values('group')

total_count_df = pd.DataFrame({'group': ['Total'], 'linkcount': total_toid_count, 'link_pct': 100.0})

linkcount_combined = pd.concat([total_count_df, toid_by_speedlimit, toid_by_route], ignore_index=True)

# print(gdflink1.shape)
# print(gdflink1['TOID'].nunique())

total_toid_count1 = len(gdflink1)
# print(total_toid_count1)

toid_by_speedlimit1 = gdflink1.groupby('speedLimit_group')['TOID'].count().reset_index()
toid_by_speedlimit1.columns = ['group', 'linkcount']
toid_by_speedlimit1['link_pct'] = (toid_by_speedlimit1['linkcount'] / total_toid_count1) * 100
toid_by_speedlimit1['link_pct'] = round(toid_by_speedlimit1['link_pct'], 2)

toid_by_route1 = gdflink1.groupby('routehierarchy_group')['TOID'].count().reset_index()
toid_by_route1.columns = ['group', 'linkcount']
toid_by_route1['link_pct'] = (toid_by_route1['linkcount'] / total_toid_count1) * 100
toid_by_route1['link_pct'] = round(toid_by_route1['link_pct'], 2)

exist_levels = [level for level in road_levels if level in toid_by_route1['group'].unique()]
toid_by_route1['group'] = pd.Categorical(toid_by_route1['group'], categories=exist_levels, ordered=True)
toid_by_route1 = toid_by_route1.sort_values('group')

total_count_df1 = pd.DataFrame({'group': ['Total'], 'linkcount': total_toid_count1, 'link_pct': 100.0})

linkcount_combined1 = pd.concat([total_count_df1, toid_by_speedlimit1, toid_by_route1], ignore_index=True)

# link length
gdflink['linklength'] = gdflink.geometry.length

lengthsum = gdflink['linklength'].sum()
linklength_total = pd.DataFrame({'group': ['Total'], 'linklength': [lengthsum], 'length_pct': 100.0})

speedlimit_lengthsum = gdflink.groupby('speedLimit_group')['linklength'].sum().reset_index()
routehierarchy_lengthsum = gdflink.groupby('routehierarchy_group')['linklength'].sum().reset_index()
# print(speedlimit_lengthsum)
# print(routehierarchy_lengthsum)

speedlimit_lengthsum.columns = ['group', 'linklength']
routehierarchy_lengthsum.columns = ['group', 'linklength']

exist_levels = [level for level in road_levels if level in routehierarchy_lengthsum['group'].unique()]
routehierarchy_lengthsum['group'] = pd.Categorical(routehierarchy_lengthsum['group'], categories=exist_levels, ordered=True)
routehierarchy_lengthsum = routehierarchy_lengthsum.sort_values('group')

speedlimit_lengthsum['length_pct'] = (speedlimit_lengthsum['linklength'] / lengthsum) * 100
speedlimit_lengthsum['length_pct'] = round(speedlimit_lengthsum['length_pct'], 2)
routehierarchy_lengthsum['length_pct'] = (routehierarchy_lengthsum['linklength'] / lengthsum) * 100
routehierarchy_lengthsum['length_pct'] = round(routehierarchy_lengthsum['length_pct'], 2)

linklength_combined = pd.concat([linklength_total, speedlimit_lengthsum, routehierarchy_lengthsum], ignore_index=True)
linklength_combined['linklength'] = linklength_combined['linklength'] / 1609.34
linklength_combined['linklength'] = round(linklength_combined['linklength'], 2)
# print(linklength_combined)

gdflink1['linklength'] = gdflink1.geometry.length

lengthsum = gdflink1['linklength'].sum()
linklength_total = pd.DataFrame({'group': ['Total'], 'linklength': [lengthsum], 'length_pct': 100.0})

speedlimit_lengthsum = gdflink1.groupby('speedLimit_group')['linklength'].sum().reset_index()
routehierarchy_lengthsum = gdflink1.groupby('routehierarchy_group')['linklength'].sum().reset_index()
# print(speedlimit_lengthsum)
# print(routehierarchy_lengthsum)

speedlimit_lengthsum.columns = ['group', 'linklength']
routehierarchy_lengthsum.columns = ['group', 'linklength']

exist_levels = [level for level in road_levels if level in routehierarchy_lengthsum['group'].unique()]
routehierarchy_lengthsum['group'] = pd.Categorical(routehierarchy_lengthsum['group'], categories=exist_levels, ordered=True)
routehierarchy_lengthsum = routehierarchy_lengthsum.sort_values('group')

speedlimit_lengthsum['length_pct'] = (speedlimit_lengthsum['linklength'] / lengthsum) * 100
speedlimit_lengthsum['length_pct'] = round(speedlimit_lengthsum['length_pct'], 2)
routehierarchy_lengthsum['length_pct'] = (routehierarchy_lengthsum['linklength'] / lengthsum) * 100
routehierarchy_lengthsum['length_pct'] = round(routehierarchy_lengthsum['length_pct'], 2)

linklength_combined1 = pd.concat([linklength_total, speedlimit_lengthsum, routehierarchy_lengthsum], ignore_index=True)
linklength_combined1['linklength'] = linklength_combined1['linklength'] / 1609.34
linklength_combined1['linklength'] = round(linklength_combined1['linklength'], 2)
# print(linklength_combined1)


# filtering df_data
df_data = dd.from_pandas(df_data, npartitions=10)

df_data = df_data[df_data['TOID'].isin(gdflink1['TOID'])]
df_data = df_data.persist()

print(df_data.columns)
print(df_data.isna().sum().compute())
print(df_data.shape[0].compute())

df_data = df_data.compute()
# print(df_data.shape)


adherence_rates_hour = df_data.groupby('hour').apply(calculate_adherence_rate).reset_index(name=f'adhrate_Total_{region}')
# print(adherence_rates_hour)

adherence_rates_hour_speed = df_data.groupby(['speedLimit_group', 'hour']).apply(calculate_adherence_rate).reset_index(name='adhrate')
# print(adherence_rates_hour_speed)

adherence_rates_hour_speed_pivot = adherence_rates_hour_speed.pivot(index='hour', columns='speedLimit_group', values='adhrate')
adherence_rates_hour_speed_pivot.columns = [f'adhrate_{col}_{region}' for col in adherence_rates_hour_speed_pivot.columns]             
# print(adherence_rates_hour_speed_pivot)

adherence_rates_hour_road = df_data.groupby(['routehierarchy_group', 'hour']).apply(calculate_adherence_rate).reset_index(name='adhrate')
# print(adherence_rates_hour_road)

adherence_rates_hour_road_pivot =adherence_rates_hour_road.pivot(index='hour', columns='routehierarchy_group', values='adhrate')
adherence_rates_hour_road_pivot.columns = [f'adhrate_{col}_{region}' for col in adherence_rates_hour_road_pivot.columns]
# print(adherence_rates_hour_road_pivot)

adherence_rates_all = pd.merge(adherence_rates_hour, adherence_rates_hour_speed_pivot, on='hour', how='outer')
adherence_rates_all = pd.merge(adherence_rates_all, adherence_rates_hour_road_pivot, on='hour', how='outer')

adherence_rates_all.to_csv(f"N:\\compass\\results_z2\\summary_regroup\\{region}\\adhrate1_byhour_{region}.csv", index=False)


adherence_mask = df_data['speed'] < df_data['speedLimit_mph']
adherence_count = adherence_mask.sum()
adherence_rate = (adherence_count / len(df_data)) * 100
adherence_rate = round(adherence_rate, 2)
# print(f"Total adherence rate: {adherence_rate}")

adherence_rate_df = pd.DataFrame({'group': ['Total'], 'adhrate': [adherence_rate]})

adherence_rates_spl = df_data.groupby('speedLimit_group').apply(calculate_adherence_rate).reset_index()
adherence_rates_spl.columns = ['group', 'adhrate']
# print(adherence_rates_spl)

adherence_rates_road = df_data.groupby('routehierarchy_group').apply(calculate_adherence_rate).reset_index()
# print(adherence_rates_road)

exist_levels = [level for level in road_levels if level in adherence_rates_road['routehierarchy_group'].unique()]
adherence_rates_road['routehierarchy_group'] = pd.Categorical(adherence_rates_road['routehierarchy_group'], categories=exist_levels, ordered=True)
adherence_rates_road = adherence_rates_road.sort_values('routehierarchy_group')
adherence_rates_road.columns = ['group', 'adhrate']

adherence_rates_combined1 = pd.concat([adherence_rate_df, adherence_rates_spl, adherence_rates_road], ignore_index=True)


speeding_counts_hour = df_data.groupby('hour').apply(count_speeding_events).reset_index(name=f'speeding_Total_{region}')
# print(speeding_counts_hour)

speeding_counts_hour_speed = df_data.groupby(['speedLimit_group', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
# print(speeding_counts_hour_speed)

speeding_counts_hour_speed_pivot = speeding_counts_hour_speed.pivot(index='hour', columns='speedLimit_group', values='speeding')
speeding_counts_hour_speed_pivot.columns = [f'speeding_{col}_{region}' for col in speeding_counts_hour_speed_pivot.columns]             
# print(speeding_counts_hour_speed_pivot)

speeding_counts_hour_road = df_data.groupby(['routehierarchy_group', 'hour']).apply(count_speeding_events).reset_index(name='speeding')
# print(speeding_counts_hour_road)

speeding_counts_hour_road_pivot = speeding_counts_hour_road.pivot(index='hour', columns='routehierarchy_group', values='speeding')
speeding_counts_hour_road_pivot.columns = [f'speeding_{col}_{region}' for col in speeding_counts_hour_road_pivot.columns]
# print(speeding_counts_hour_road_pivot)

speeding_counts_all = pd.merge(speeding_counts_hour, speeding_counts_hour_speed_pivot, on='hour', how='outer')
speeding_counts_all = pd.merge(speeding_counts_all, speeding_counts_hour_road_pivot, on='hour', how='outer')

speeding_counts_all.to_csv(f"N:\\compass\\results_z2\\summary_regroup\\{region}\\speeding1_byhour_{region}.csv", index=False)


speeding_mask = df_data['speed'] > df_data['speedLimit_mph']
speeding_count = speeding_mask.sum()
# print(f"Total speeding count: {speeding_count}")

speeding_count_df = pd.DataFrame({'group': ['Total'], 'speeding': [speeding_count]})

speeding_counts_spl = df_data.groupby('speedLimit_group').apply(count_speeding_events).reset_index()
speeding_counts_spl.columns = ['group', 'speeding']
# print(speeding_counts_spl)

speeding_counts_road = df_data.groupby('routehierarchy_group').apply(count_speeding_events).reset_index()
# print(speeding_counts_road)

exist_levels = [level for level in road_levels if level in speeding_counts_road['routehierarchy_group'].unique()]
speeding_counts_road['routehierarchy_group'] = pd.Categorical(speeding_counts_road['routehierarchy_group'], categories=exist_levels, ordered=True)
speeding_counts_road = speeding_counts_road.sort_values('routehierarchy_group')
speeding_counts_road.columns = ['group', 'speeding']

speeding_counts_combined1 = pd.concat([speeding_count_df, speeding_counts_spl, speeding_counts_road], ignore_index=True)
speeding_counts_combined1['speeding_pct'] = (speeding_counts_combined1['speeding'] / speeding_count) * 100


speed_limit_pointcounts = df_data['speedLimit_group'].value_counts().reset_index(name='pointcount')
speed_limit_pointcounts = speed_limit_pointcounts.sort_values('speedLimit_group')
speed_limit_pointcounts.columns = ['group', 'pointcount']
# print(speed_limit_pointcounts)

total_pointcounts = len(df_data)
total_pointcounts_row = pd.DataFrame({'group': ['Total'], 'pointcount': [total_pointcounts]})

route_hierarchy_pointcounts = df_data['routehierarchy_group'].value_counts().reset_index(name='pointcount')
# print(route_hierarchy_pointcounts)

exist_levels = [level for level in road_levels if level in route_hierarchy_pointcounts['routehierarchy_group'].unique()]
route_hierarchy_pointcounts['routehierarchy_group'] = pd.Categorical(route_hierarchy_pointcounts['routehierarchy_group'], categories=exist_levels, ordered=True)
route_hierarchy_pointcounts = route_hierarchy_pointcounts.sort_values('routehierarchy_group')
route_hierarchy_pointcounts.columns = ['group', 'pointcount']

speed_limit_pointcounts_combined1 = pd.concat([total_pointcounts_row, speed_limit_pointcounts, 
                                              route_hierarchy_pointcounts], ignore_index=True)

speed_limit_pointcounts_combined1['point_pct'] = (speed_limit_pointcounts_combined1['pointcount'] / total_pointcounts) * 100
speed_limit_pointcounts_combined1['point_pct'] = round(speed_limit_pointcounts_combined1['point_pct'], 2)


combined_df = pd.merge(adherence_rates_combined, speeding_counts_combined, on='group', how='inner')
combined_df = pd.merge(combined_df, speed_limit_pointcounts_combined, on='group', how='inner')
combined_df = pd.merge(combined_df, linkpointcounts_combined, on='group', how='inner')
combined_df = pd.merge(combined_df, linkcount_combined, on='group', how='inner')
combined_df = pd.merge(combined_df, linklength_combined, on='group', how='inner')

combined_df['normalised_speeding'] = round((combined_df['speeding'] / combined_df['linklength']), 2)
combined_df['speeding_perlink'] = round((combined_df['speeding'] / combined_df['linkcount']), 2)
combined_df['length_perlink'] = round((combined_df['linklength'] / combined_df['linkcount']), 4)
combined_df.to_csv(f"N:\\compass\\results_z2\\summary_regroup\\{region}\\summary_regroup_{region}.csv", index=False)


combined_df1 = pd.merge(adherence_rates_combined1, speeding_counts_combined1, on='group', how='inner')
combined_df1 = pd.merge(combined_df1, speed_limit_pointcounts_combined1, on='group', how='inner')
combined_df1 = pd.merge(combined_df1, linkpointcounts_combined1, on='group', how='inner')
combined_df1 = pd.merge(combined_df1, linkcount_combined1, on='group', how='inner')
combined_df1 = pd.merge(combined_df1, linklength_combined1, on='group', how='inner')

combined_df1['normalised_speeding'] = round((combined_df1['speeding'] / combined_df1['linklength']), 2)
combined_df1['speeding_perlink'] = round((combined_df1['speeding'] / combined_df1['linkcount']), 2)
combined_df1['length_perlink'] = round((combined_df1['linklength'] / combined_df1['linkcount']), 4)
combined_df1.to_csv(f"N:\\compass\\results_z2\\summary_regroup\\{region}\\summary1_regroup_{region}.csv", index=False)



#%%
import os
import time
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine, MetaData, select, func, text

# connect to postgresql database
dbname = "compass_db"
user = "compass_user"
password = "postgres"
host = "localhost"
port = "5432"

conn_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
db_engine = create_engine(conn_string)

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

table_name = f"{region}_match"

metadata = MetaData()
metadata.reflect(bind=db_engine)
table = metadata.tables[table_name]

columns = table.columns.keys()
print(columns)

with db_engine.connect() as conn:
    unique_trip_ids = conn.execute(select(table.c.agent_id).distinct()).fetchall()
    

unique_trip_ids = [row[0] for row in unique_trip_ids]
num_unique_trip = len(unique_trip_ids)
print(f"number of unique trips: {num_unique_trip}")












