# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 22:49:04 2024

@author: geolche
"""


#%%
# post process of map-matching results
import os
import pandas as pd
import geopandas as gpd

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
# region = "London"
# region = "WestMidlands"


data_folder = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\"
linkidmap = pd.read_csv(f"N:\\compass\\compasspro\\matchpro\\idmap\\linkid_{region}.csv")

data_folder_new = f"N:\\compass\\compasspro\\matchpro\\linkid_{region}_match\\"
os.makedirs(data_folder_new, exist_ok=True)


for chunk_folder in os.listdir(data_folder):    
    chunk_path = os.path.join(data_folder, chunk_folder)
    
    df_chunk = []
    
    if os.path.isdir(chunk_path):
        save_chunk_parquet = os.path.join(data_folder_new, f"{chunk_folder}.parquet")
        
        for file in os.listdir(chunk_path):
            if file.endswith('.csv'):
                file_path = os.path.join(chunk_path, file)
                
                df_csv = pd.read_csv(file_path)
                                
                df_csv = df_csv[['agent_id', 'time', 'link_id', 'seq', 'sub_seq', 
                                 'from_node', 'to_node', 'lng', 'lat']]
                print(df_csv.shape)
                
                merged_df = pd.merge(df_csv, linkidmap, on='link_id', how='inner')
                print(merged_df.shape)
                
                df_chunk.append(merged_df)
        
        combined_df = pd.concat(df_chunk, ignore_index=True)
        combined_df.to_parquet(save_chunk_parquet, index=False)

# results store to folder matchpro

#%%
# post process of map-matching results
import os

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
region = "London"


data_folder = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\"
# extensions_to_keep = ['link.geojson']
extensions_to_keep = ['gps.geojson', 'link.geojson']

def cleanup_files(folder):
    files = os.listdir(folder)
    for file in files:
        if not any(file.endswith(ext) for ext in extensions_to_keep):
            file_path = os.path.join(folder, file)
            os.remove(file_path)            
    print(f"cleanup for folder: {folder}")


for item in os.listdir(data_folder):
    item_path = os.path.join(data_folder, item)
    if os.path.isdir(item_path):
        cleanup_files(item_path)


#%%
# post process of map-matching results
import os

# region = "London"

data_folder = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\"
# extensions_to_keep = ['res.csv', 'gps.geojson', 'link.geojson']
extensions_to_keep = ['gps.geojson', 'link.geojson']

def cleanup_files(folder):
    files = os.listdir(folder)
    for file in files:
        if not any(file.endswith(ext) for ext in extensions_to_keep):
            file_path = os.path.join(folder, file)
            os.remove(file_path)            
    print(f"cleanup for folder: {folder}")

partitions = [
    range(1, 21), # chunk1 - chunk20
    range(21, 41), # chunk21 - chunk40
    range(41, 61), # chunk41 - chunk60
    range(61, 81), # chunk61 - chunk80
    range(81, 101), # chunk81 - chunk101
    ]

# partition_to_process = partitions[0]
# partition_to_process = partitions[1]
# partition_to_process = partitions[2]
# partition_to_process = partitions[3]
partition_to_process = partitions[4]

for folder_index in partition_to_process:
    folder_name = f'chunk_{folder_index}'
    folder_path = os.path.join(data_folder, folder_name)
    cleanup_files(folder_path)
    

#%%
# post process of map-matching results
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
# region = "London"

data_folder = f"N:\\compass\\compasspro\\matchpro\\linkid_{region}_match\\"
exception_log_txt = f"N:\\compass\\compasspro\\matchpro\\exception_linkid_{region}.txt"

for file in os.listdir(data_folder):
    if file.endswith('.parquet'):
        file_path = os.path.join(data_folder, file)
        
        df_chunk = pd.read_parquet(file_path)
        df_chunk = df_chunk[df_chunk['sub_seq'] == 0].reset_index(drop=True)
        
        df_chunk = df_chunk[['agent_id', 'time', 'link_id', 'TOID']]
        
        try:
            table_name = f"{region}_TOID"
            df_chunk.to_sql(table_name, db_connect, if_exists='append', index=False)
            
        except ValueError as ve:
            print(ve)
            with open(exception_log_txt, 'a') as exception_file:
                exception_file.write(f"ValueError for {file} in region {region}: {ve}\n")
        except Exception as ex:
            print(ex)
            with open(exception_log_txt, 'a') as exception_file:
                exception_file.write(f"Exception for {file} in region {region}: {ex}\n")
        else:
            print(f"{file} for {region} added successfully to {table_name}")



# write matchpro to sql database

#%%            
from sqlalchemy import create_engine, MetaData, select, text, func
from sqlalchemy.exc import SQLAlchemyError

# connect to postgresql database
dbname = "compass_db"
user = "compass_user"
password = "postgres"
host = "localhost"
port = "5432"

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
# region = "London"

table_name = f"{region}_TOID"

conn_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
db_engine = create_engine(conn_string)


sql_create_index = f"""
CREATE INDEX IF NOT EXISTS id_{region} ON "{table_name}"("agent_id");
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
    unique_trip_ids = conn.execute(select(table.c.agent_id).distinct()).fetchall()

print("Total Rows:", total_rows)    
print(f"Unique Trips: {len(unique_trip_ids)}")

with db_engine.connect() as conn:
    tripids_query = f'SELECT DISTINCT "agent_id" FROM "{table_name}"'
    unique_trip_ids = conn.execute(text(tripids_query)).fetchall()
    print(len(unique_trip_ids))


#%%
import os
import time
import pandas as pd
from sqlalchemy import create_engine, MetaData, select

# connect to postgresql database
dbname = "compass_db"
user = "compass_user"
password = "postgres"
host = "localhost"
port = "5432"

conn_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
db_engine = create_engine(conn_string)
db_connect = db_engine.connect()

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
# region = "London"

table_toid = f"{region}_TOID"
metadata = MetaData()
metadata.reflect(bind=db_engine)
table = metadata.tables[table_toid]
columns = table.columns.keys()
print(columns)

table_match = f"{region}_match"

parquet_folder = f"N:\\compass\\compasspro\\parquetdata\\{region}\\"
exception_log_txt = f"N:\\compass\\compasspro\\matchpro\\exception_match_{region}.txt"

for file in os.listdir(parquet_folder):
    if file.endswith('.parquet'):
        file_path = os.path.join(parquet_folder, file)
        
        start_time = time.time()
        df_chunk = pd.read_parquet(file_path)
        
        df_chunk['time'] = pd.to_datetime(df_chunk['time'], format='ISO8601')
        df_chunk['time'] = df_chunk['time'].dt.strftime("%Y-%m-%d %H:%M:%S")
        df_chunk['agent_id'] = df_chunk['agent_id'].astype('int64')
        print(df_chunk.shape)
        # print(df_chunk.dtypes)
        
        try:
            unique_agent_ids = df_chunk['agent_id'].unique().tolist()
            
            with db_engine.connect() as conn:
                query = select(
                    table.c.agent_id, 
                    table.c.time, 
                    table.c.TOID
                ).where(table.c.agent_id.in_(unique_agent_ids))
                
                toid_data = pd.read_sql(query, conn)
                toid_data['time'] = pd.to_datetime(toid_data['time'], format='ISO8601')
                toid_data['time'] = toid_data['time'].dt.strftime("%Y-%m-%d %H:%M:%S")
                print(toid_data.shape)
                # print(toid_data.dtypes)
                                   
            merged_df = pd.merge(df_chunk, toid_data, on=['agent_id', 'time'], how='inner')
            print(merged_df.shape)
                
            merged_df.to_sql(table_match, db_connect, if_exists='append', index=False)
            
            end_time = time.time()
            time_cost = end_time - start_time
            print(f"file {file} time cost {time_cost}")
            
        except ValueError as ve:
            print(ve)
            with open(exception_log_txt, 'a') as exception_file:
                exception_file.write(f"ValueError for {file} in region {region}: {ve}\n")
        except Exception as ex:
            print(ex)
            with open(exception_log_txt, 'a') as exception_file:
                exception_file.write(f"Exception for {file} in region {region}: {ex}\n")
        else:
            print(f"{file} for {region} added successfully to {table_match}")


# join matchpro with parquetdata and save to sql database

#%%            
from sqlalchemy import create_engine, MetaData, select, text, func
from sqlalchemy.exc import SQLAlchemyError

# connect to postgresql database
dbname = "compass_db"
user = "compass_user"
password = "postgres"
host = "localhost"
port = "5432"

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
# region = "London"

table_name = f"{region}_match"

conn_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
db_engine = create_engine(conn_string)

sql_create_index = f"""
CREATE INDEX IF NOT EXISTS idm_{region} ON "{table_name}"("agent_id");
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
    unique_trip_ids = conn.execute(select(table.c.agent_id).distinct()).fetchall()

print("Total Rows:", total_rows)    
print(f"Unique Trips: {len(unique_trip_ids)}")

with db_engine.connect() as conn:
    tripids_query = f'SELECT DISTINCT "agent_id" FROM "{table_name}"'
    unique_trip_ids = conn.execute(text(tripids_query)).fetchall()
    print(len(unique_trip_ids))




#%%
import pandas as pd
import geopandas as gpd

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

InputPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1.gpkg"
link_layer = "RoadLink1"
gdflink = gpd.read_file(filename=InputPath, layer=link_layer)    
print(gdflink.shape)

speedlimit_df = pd.read_csv("N:\\compass\\data\\geodata\\SpeedLimits\\Speed_Limit.csv")
print(speedlimit_df.columns)

gdflink = gdflink.merge(speedlimit_df, left_on='TOID', right_on='roadLinkID', how='left')
print(gdflink.columns)
print(gdflink.shape)

OutPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1.gpkg"
OutLink = "RoadLink1x"
gdflink.to_file(OutPath, layer=OutLink, driver='GPKG')

            









