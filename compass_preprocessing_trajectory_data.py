# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 20:51:16 2024

@author: geolche
"""


#%%
# Use
import os
import pandas as pd
from sqlalchemy import create_engine

# connect to postgresql database
dbname = "compass_db"
user = "compass_user"
password = "postgres"
host = "localhost"
port = "5432"

engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")
db_connect = engine.connect()

def check_lengths(row):
    lengths = [len(item.split(',')) for item in row if isinstance(item, str)]
    return len(set(lengths)) == 1

data_path = "N:\\compass\\data\\cmpsdata\\data"

# namefile_txt = os.path.join("N:\\compass\\data\\", "namefile_LWOC.txt")
# errorfile_txt = os.path.join("N:\\compass\\data\\", "errorfile_LWOC.txt")
# exception_log_txt = os.path.join("N:\\compass\\data\\", "exception_log_LWOC.txt")

# namefile_txt = os.path.join("N:\\compass\\data\\", "namefile_NEG.txt")
# errorfile_txt = os.path.join("N:\\compass\\data\\", "errorfile_NEG.txt")
# exception_log_txt = os.path.join("N:\\compass\\data\\", "exception_log_NEG.txt")

# namefile_txt = os.path.join("N:\\compass\\data\\", "namefile_MWS.txt")
# errorfile_txt = os.path.join("N:\\compass\\data\\", "errorfile_MWS.txt")
# exception_log_txt = os.path.join("N:\\compass\\data\\", "exception_log_MWS.txt")

namefile_txt = os.path.join("N:\\compass\\data\\", "namefile_CWL.txt")
errorfile_txt = os.path.join("N:\\compass\\data\\", "errorfile_CWL.txt")
exception_log_txt = os.path.join("N:\\compass\\data\\", "exception_log_CWL.txt")


# regions_to_tables = {
#     "Greater_London" : "London",
#     "West of England" : "WestEngland",
#     "Oxford" : "Oxford",
#     "Cambridge" : "Cambridge"
#     }        

# regions_to_tables = {
#     "Tyne_and_Wear_(Newcastle)" : "Newcastle",
#     "Edinburgh" : "Edinburgh",
#     "Glasgow" : "Glasgow"
#     }       
        
# regions_to_tables = {
#     "Greater_Manchester" : "Manchester",
#     "West_Yorkshire_Combined_Authority" : "WestYorkshire",
#     "South Yorkshire" : "SouthYorkshire"
#     }    
        
regions_to_tables = {
    "Cardiff" : "Cardiff",
    "West_Midlands_Combined_Authority" : "WestMidlands",
    "Liverpool_City_Region" : "Liverpool"
    }         

# data_df = data_df[['VehicleID', 'TripID', 'VehicleType', 'AreaName', 'TimestampPath', 'SnappedPath', 
#                    'SpeedPath', 'XAccPath', 'YAccPath', 'SpeedAvg', 'SpeedMedian', 
#                    'TravelTimeMinutes', 'TravelDistanceMiles', 'Make', 'Model']]        

regions_row_counts = {region: 0 for region in regions_to_tables.keys()}

for folder in os.listdir(data_path):
    folder_path = os.path.join(data_path, folder)
    
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        
        print(folder, file)
        
        try:
            data_df = pd.read_parquet(file_path)            
            data_df = data_df[['TripID', 'VehicleType', 'AreaName', 'TimestampPath', 'SnappedPath', 
                               'SpeedPath', 'XAccPath', 'YAccPath', 'Make', 'Model', 'VehicleID']]
            
            data_df = data_df[data_df['VehicleType'].isin(['HCV', 'LCV'])].reset_index(drop=True)
            
            consistent_lengths = data_df[['TimestampPath', 'SnappedPath', 'SpeedPath', 'XAccPath', 
                                          'YAccPath']].apply(check_lengths, axis=1)
            
            with open(namefile_txt, 'a') as namefile:
                if not consistent_lengths.all():
                    error_message = f"Not all rows have the same length in list columns of {file}"
                    namefile.write(f"{folder}_{file}: {error_message}\n")
                    raise ValueError(error_message)
                else:
                    namefile.write(f"{folder}_{file}\n")                                        
            
            df_new = data_df.apply(lambda x: x.str.split(',').explode() if x.name in 
                                   ['TimestampPath', 'SnappedPath', 'SpeedPath', 'XAccPath', 
                                    'YAccPath'] else x).reset_index(drop=True)
            
            for region, table_name in regions_to_tables.items():
                try:
                    df_region = df_new[df_new['AreaName'] == region].reset_index(drop=True)
                    
                    df_region = df_region[['TripID', 'TimestampPath', 'SnappedPath', 'SpeedPath', 
                                           'XAccPath', 'YAccPath', 'VehicleType', 'Make', 'Model', 'VehicleID']]
                    
                    print(f"processing file: {file}, region: {region}, shape: {df_region.shape}")
                    
                    row_count = len(df_region)
                    regions_row_counts[region] += row_count
                    
                    df_region.to_sql(table_name, db_connect, if_exists='append', index=False)
                    
                except ValueError as ve:
                    print(ve)
                    with open(exception_log_txt, 'a') as exception_file:
                        exception_file.write(f"ValueError for {folder}_{file} in region {region}: {ve}\n")
                except Exception as ex:
                    print(ex)
                    with open(exception_log_txt, 'a') as exception_file:
                        exception_file.write(f"Exception for {folder}_{file} in region {region}: {ex}\n")
                else:
                    print(f"{folder} {file} for {region} added successfully to {table_name}")
                    
        except ValueError as ve:
            print(ve)
            with open(errorfile_txt, 'a') as errorfile:
                errorfile.write(f"error processing {folder}_{file}: {ve}\n")
        except Exception as ex:
            print(ex)
            with open(errorfile_txt, 'a') as errorfile:
                errorfile.write(f"unexpected error processing {folder}_{file}: {ex}\n")
                
for region, count in regions_row_counts.items():
    print(f"{region}: {count} rows")
    

#%%
# create a column of PointIDinTrip within each TripID
from sqlalchemy import create_engine, text, MetaData, select, func
from sqlalchemy.exc import SQLAlchemyError

# connect to postgresql database
dbname = "compass_db"
user = "compass_user"
password = "postgres"
host = "localhost"
port = "5432"

# table_name = "London"
# table_name = "WestEngland"
# table_name = "Oxford"
# table_name = "Cambridge"

# table_name = "Newcastle"
# table_name = "Edinburgh"
# table_name = "Glasgow"

# table_name = "WestYorkshire"
# table_name = "SouthYorkshire"
# table_name = "Manchester"

# table_name = "Cardiff"
# table_name = "Liverpool"
# table_name = "WestMidlands"

conn_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
db_engine = create_engine(conn_string)


sql_create_index = f"""
CREATE INDEX IF NOT EXISTS idtrip_{table_name} ON "{table_name}"("TripID");
"""

def create_index():
    try:
        with db_engine.connect() as conn:
            conn.execute(text(sql_create_index))
            conn.commit()
            print("index created")
            
    except SQLAlchemyError as e:
        print(f"an error occurred: {e}")


create_index()


metadata = MetaData()
metadata.reflect(bind=db_engine)
table = metadata.tables[table_name]

columns = table.columns.keys()
print(columns)

with db_engine.connect() as conn:
    total_rows = conn.execute(select(func.count()).select_from(table)).scalar()
    
print("Total Rows:", total_rows)


with db_engine.connect() as conn:
    unique_trip_ids = conn.execute(select(table.c.TripID).distinct()).fetchall()
    
print(f"Unique Trips: {len(unique_trip_ids)}")

with db_engine.connect() as conn:
    tripids_query = f'SELECT DISTINCT "TripID" FROM "{table_name}"'
    unique_trip_ids = conn.execute(text(tripids_query)).fetchall()
    print(len(unique_trip_ids))
    
# unique_trip_ids = [row[0] for row in unique_trip_ids]
# print(len(unique_trip_ids))


#%%

import pandas as pd
from sqlalchemy import create_engine, MetaData, select

# connect to postgresql database
dbname = "compass_db"
user = "compass_user"
password = "postgres"
host = "localhost"
port = "5432"

# table_name = "London"
# table_name = "WestEngland"
# table_name = "Oxford"
# table_name = "Cambridge"

# table_name = "Newcastle"
# table_name = "Edinburgh"
# table_name = "Glasgow"

# table_name = "WestYorkshire"
# table_name = "SouthYorkshire"
# table_name = "Manchester"

# table_name = "Cardiff"
# table_name = "Liverpool"
table_name = "WestMidlands"

conn_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
db_engine = create_engine(conn_string)

metadata = MetaData()
metadata.reflect(bind=db_engine)
table = metadata.tables[table_name]

query = select(table.c.VehicleType, table.c.Make, table.c.Model).distinct()

with db_engine.connect() as conn:
    results = conn.execute(query)
    unique_makemodels = results.fetchall()

df = pd.DataFrame(unique_makemodels, columns=['VehicleType', 'Make', 'Model'])

for index, row in df.iterrows():
    print(index, row)

df.to_csv(f"N:\\compass\\compasspro\\makemodels\\MakeModels_{table_name}.csv", index=False)


#%%
import os
import pandas as pd

csv_path = "N:\\compass\\compasspro\\makemodels\\"

MakeModels_df = []

for filename in os.listdir(csv_path):
    if filename.endswith('.csv'):
        print(filename)
        filepath = os.path.join(csv_path, filename)
        df = pd.read_csv(filepath)
        MakeModels_df.append(df)
        
MakeModels_dfx = pd.concat(MakeModels_df, ignore_index=True)

MakeModels_dfx = MakeModels_dfx.drop_duplicates(subset=['VehicleType', 'Make', 'Model']).reset_index(drop=True)

MakeModels_dfx.to_csv("N:\\compass\\compasspro\\MakeModels.csv", index=False)


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

# table_name = "London"
# table_name = "WestEngland"
# table_name = "Oxford"
# table_name = "Cambridge"

# table_name = "Newcastle"
# table_name = "Edinburgh"
# table_name = "Glasgow"

# table_name = "WestYorkshire"
# table_name = "SouthYorkshire"
# table_name = "Manchester"

# table_name = "Cardiff"
# table_name = "Liverpool"
# table_name = "WestMidlands"


metadata = MetaData()
metadata.reflect(bind=db_engine)
table = metadata.tables[table_name]

columns = table.columns.keys()
print(columns)

with db_engine.connect() as conn:
    total_rows = conn.execute(select(func.count()).select_from(table)).scalar()
    unique_trip_ids = conn.execute(select(table.c.TripID).distinct()).fetchall()
    
print("Total Rows:", total_rows)

unique_trip_ids = [row[0] for row in unique_trip_ids]
num_chunks = 99
num_unique_trip = len(unique_trip_ids)
print(f"number of unique trips: {num_unique_trip}")
chunk_size = max(1, len(unique_trip_ids) // num_chunks)
trip_id_chunks = [unique_trip_ids[i:i+chunk_size] 
                  for i in range(0, len(unique_trip_ids), chunk_size)]

num_chunks_x = len(trip_id_chunks)
print(f"region: {table_name}, number of chunks: {num_chunks_x}")

parquet_folder = f"N:\\compass\\compasspro\\parquetdata\\{table_name}\\"
if not os.path.exists(parquet_folder):
    os.makedirs(parquet_folder)

roadlink_file = f"N:\\compass\\data\\geodata\\highways\\{table_name}\\Roads1.gpkg"
roadlink_layer = "RoadLink1"

gdflink = gpd.read_file(filename=roadlink_file, layer=roadlink_layer)
print(gdflink.crs)

rowcount_raw = 0
rowcount_pro = 0

def calculate_accelerated_speed(group):
    group['dif_speed'] = group['speed'].diff()
    group['dif_time'] = group['time'].diff().dt.total_seconds()
    group['acc_speed'] = group['dif_speed'] / group['dif_time']
    group['acc_speed'] = group['acc_speed'].shift(-1)
    return group

def spatial_join_within_distance(gdfp, gdfl):
    gdfjoin = gpd.sjoin_nearest(gdfp, gdfl, how='inner', distance_col='distance')
    gdf_filtered = gdfjoin[gdfjoin['distance'] <= 10]
    return gdf_filtered

for chunk_index, trip_id_chunk in enumerate(trip_id_chunks):
    print(f"processing chunk {chunk_index+1}/{num_chunks_x}")
    
    stmt = select(table.c.TripID,
                  table.c.TimestampPath, 
                  table.c.SnappedPath, 
                  table.c.SpeedPath,
                  table.c.XAccPath,
                  table.c.YAccPath,
                  table.c.VehicleType,
                  table.c.Make,
                  table.c.Model,
                  table.c.VehicleID
        ).where(table.c.TripID.in_(trip_id_chunk))
    
    with db_engine.connect() as conn:
        start_time = time.time()
        df_chunk = pd.read_sql(stmt, conn)
        count_raw = df_chunk.shape[0]
        rowcount_raw += count_raw
        print(f"chunk {chunk_index+1} rows: {count_raw}")
        
        df_chunk['agent_id'] = df_chunk['TripID']
        df_chunk['speed'] = pd.to_numeric(df_chunk['SpeedPath'])
        df_chunk.loc[:, 'time'] = pd.to_datetime(df_chunk['TimestampPath'], format='ISO8601')
        
        grouped = df_chunk.groupby('agent_id')
        processed_groups = []

        for name, group in grouped:
            processed_group = calculate_accelerated_speed(group)
            processed_groups.append(processed_group)
            
        df_chunk = pd.concat(processed_groups).reset_index(drop=True)
        # print(df_chunk.columns)
        
        df_chunk['time'] = df_chunk['time'].dt.strftime("%Y-%m-%d %H:%M:%S")
        df_chunk[['lng', 'lat']] = df_chunk['SnappedPath'].str.split(' ', expand=True)
        
        df_chunk = df_chunk[~(df_chunk['speed']==0)].reset_index(drop=True)
        print(f"chunk {chunk_index+1} rows exclude speed equal zero: {df_chunk.shape[0]}")
        # print(df_chunk.columns)

        df_chunk = df_chunk[['agent_id', 'lng', 'lat', 'time', 'speed', 'dif_time', 
                             'dif_speed', 'acc_speed', 'XAccPath', 'YAccPath', 
                             'VehicleType', 'Make', 'Model', 'VehicleID']]
          
        gdf_chunk = gpd.GeoDataFrame(df_chunk, 
                                     geometry=gpd.points_from_xy(df_chunk['lng'], df_chunk['lat']), 
                                     crs='EPSG:4326')

        gdf_chunk = gdf_chunk.to_crs('EPSG:27700')
        
        gdf_chunk = spatial_join_within_distance(gdf_chunk, gdflink)
        print(gdf_chunk.columns)
        
        df_chunk = gdf_chunk[['agent_id', 'lng', 'lat', 'time', 'speed', 'dif_time', 
                              'dif_speed', 'acc_speed', 'XAccPath', 'YAccPath', 
                              'VehicleType', 'Make', 'Model', 'VehicleID', 'distance']]
        
        print(f"chunk {chunk_index+1} rows exclude distance up 15m: {df_chunk.shape[0]}")
        
        df_chunk = df_chunk.drop_duplicates(subset=['agent_id', 'time']).reset_index(drop=True)
        print(f"chunk {chunk_index+1} rows exclude duplicate points: {df_chunk.shape[0]}")
        
        mask = df_chunk['agent_id'].map(df_chunk['agent_id'].value_counts()) == 1
        df_chunk = df_chunk[~mask].reset_index(drop=True)
        
        count_pro = df_chunk.shape[0]
        rowcount_pro += count_pro
        print(f"chunk {chunk_index+1} rows exclude one point trips: {count_pro}")
  
        parquet_name = f"chunk_{chunk_index+1}"  
        parquet_path = os.path.join(parquet_folder, parquet_name + '.parquet')
        df_chunk.to_parquet(parquet_path, index=False)    
        print(f"add {parquet_name} parquet to folder")
        end_time = time.time()
        time_cost = end_time - start_time
        print(f"chunk {chunk_index+1} time cost {time_cost}")
            
print(f"{table_name}: raw rows {rowcount_raw}, processed rows {rowcount_pro}")
print(f"region: {table_name}, number of chunks: {num_chunks_x}")



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

# table_name = "London"

metadata = MetaData()
metadata.reflect(bind=db_engine)
table = metadata.tables[table_name]

columns = table.columns.keys()
print(columns)

with db_engine.connect() as conn:
    total_rows = conn.execute(select(func.count()).select_from(table)).scalar()
    unique_trip_ids = conn.execute(select(table.c.TripID).distinct()).fetchall()
    
print("Total Rows:", total_rows)

unique_trip_ids = [row[0] for row in unique_trip_ids]
num_chunks = 99
num_unique_trip = len(unique_trip_ids)
print(f"number of unique trips: {num_unique_trip}")
chunk_size = max(1, len(unique_trip_ids) // num_chunks)
trip_id_chunks = [unique_trip_ids[i:i+chunk_size] 
                  for i in range(0, len(unique_trip_ids), chunk_size)]

num_chunks_x = len(trip_id_chunks)
print(f"region: {table_name}, number of chunks: {num_chunks_x}")

gpkg_file = f"N:\\compass\\compasspro\\geodata\\{table_name}\\{table_name}_Pt.gpkg"
# gpkg_file = f"N:\\compass\\compasspro\\geodata\\{table_name}\\{table_name}_Pt_disex.gpkg"

if os.path.exists(gpkg_file):
    os.remove(gpkg_file)
    
gpkg_dir = os.path.dirname(gpkg_file)
os.makedirs(gpkg_dir, exist_ok=True)


roadlink_file = f"N:\\compass\\data\\geodata\\highways\\{table_name}\\Roads1.gpkg"
roadlink_layer = "RoadLink1"

gdflink = gpd.read_file(filename=roadlink_file, layer=roadlink_layer)
print(gdflink.crs)

rowcount_raw = 0
rowcount_pro = 0

def calculate_accelerated_speed(group):
    group['dif_speed'] = group['speed'].diff()
    group['dif_time'] = group['time'].diff().dt.total_seconds()
    group['acc_speed'] = group['dif_speed'] / group['dif_time']
    group['acc_speed'] = group['acc_speed'].shift(-1)
    return group

def spatial_join_within_distance(gdfp, gdfl):
    gdfjoin = gpd.sjoin_nearest(gdfp, gdfl, how='inner', distance_col='distance')
    gdf_filtered = gdfjoin[gdfjoin['distance'] <= 10]
    # gdf_filtered = gdfjoin[gdfjoin['distance'] > 15]
    return gdf_filtered

for chunk_index, trip_id_chunk in enumerate(trip_id_chunks):
    print(f"processing chunk {chunk_index+1}/{num_chunks_x}")
    
    stmt = select(table.c.TripID,
                  table.c.TimestampPath, 
                  table.c.SnappedPath, 
                  table.c.SpeedPath,
                  table.c.XAccPath,
                  table.c.YAccPath,
                  table.c.VehicleType,
                  table.c.Make,
                  table.c.Model,
                  table.c.VehicleID
        ).where(table.c.TripID.in_(trip_id_chunk))
    
    with db_engine.connect() as conn:
        start_time = time.time()
        df_chunk = pd.read_sql(stmt, conn)
        count_raw = df_chunk.shape[0]
        rowcount_raw += count_raw
        print(f"chunk {chunk_index+1} rows: {count_raw}")
        
        df_chunk['agent_id'] = df_chunk['TripID']
        df_chunk['speed'] = pd.to_numeric(df_chunk['SpeedPath'])
        df_chunk.loc[:, 'time'] = pd.to_datetime(df_chunk['TimestampPath'], format='ISO8601')
        
        grouped = df_chunk.groupby('agent_id')
        processed_groups = []

        for name, group in grouped:
            processed_group = calculate_accelerated_speed(group)
            processed_groups.append(processed_group)
            
        df_chunk = pd.concat(processed_groups).reset_index(drop=True)
        print(df_chunk.columns)
        
        df_chunk['time'] = df_chunk['time'].dt.strftime("%Y-%m-%d %H:%M:%S")
        df_chunk[['lng', 'lat']] = df_chunk['SnappedPath'].str.split(' ', expand=True)
        
        df_chunk = df_chunk[~(df_chunk['speed']==0)].reset_index(drop=True)
        print(f"chunk {chunk_index+1} rows exclude speed equal zero: {df_chunk.shape[0]}")
        print(df_chunk.columns)

        df_chunk = df_chunk[['agent_id', 'lng', 'lat', 'time', 'speed', 'dif_time', 
                             'dif_speed', 'acc_speed', 'XAccPath', 'YAccPath', 
                             'VehicleType', 'Make', 'Model', 'VehicleID']]
                
        gdf_chunk = gpd.GeoDataFrame(df_chunk, 
                                     geometry=gpd.points_from_xy(df_chunk['lng'], df_chunk['lat']), 
                                     crs='EPSG:4326')

        gdf_chunk = gdf_chunk.to_crs('EPSG:27700')
        
        gdf_chunk = spatial_join_within_distance(gdf_chunk, gdflink)
        print(gdf_chunk.columns)
        
        gdf_chunk = gdf_chunk[['agent_id', 'lng', 'lat', 'time', 'speed', 'dif_time', 
                               'dif_speed', 'acc_speed', 'XAccPath', 'YAccPath', 
                               'VehicleType', 'Make', 'Model', 'VehicleID', 'distance', 'geometry']]
        
        print(f"chunk {chunk_index+1} rows exclude distance less 15m: {gdf_chunk.shape[0]}")
        
        gdf_chunk = gdf_chunk.drop_duplicates(subset=['agent_id', 'time']).reset_index(drop=True)
        print(f"chunk {chunk_index+1} rows exclude duplicate points: {df_chunk.shape[0]}")
        
        mask = gdf_chunk['agent_id'].map(gdf_chunk['agent_id'].value_counts()) == 1
        gdf_chunk = gdf_chunk[~mask].reset_index(drop=True)
        
        count_pro = gdf_chunk.shape[0]
        rowcount_pro += count_pro
        print(f"chunk {chunk_index+1} rows exclude one point trips: {count_pro}")
  
        layer_name = f"chunk_{chunk_index+1}"   
        gdf_chunk.to_file(filename=gpkg_file, layer=layer_name, driver='GPKG')           
        print(f"add layer {layer_name} to gpkg")
        end_time = time.time()
        time_cost = end_time - start_time
        print(f"chunk {chunk_index+1} time cost {time_cost}")
            
print(f"{table_name}: raw rows {rowcount_raw}, processed rows {rowcount_pro}")


#%%

