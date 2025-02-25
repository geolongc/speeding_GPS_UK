# -*- coding: utf-8 -*-
"""
Created on Sun May  5 15:06:09 2024

@author: geolche
"""

# pre-processing road link
#%%

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
region = "WestMidlands"


InputPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads.gpkg"
RoadLink = "RoadLink"
RoadNode = "RoadNode"

gdflink = gpd.read_file(filename=InputPath, layer=RoadLink)
gdfnode = gpd.read_file(filename=InputPath, layer=RoadNode)

print(gdflink.crs)
print(gdfnode.crs)

print(gdflink.shape)
# print(gdflink.columns)
print(gdfnode.shape)
# print(gdfnode.columns)

gdflink = gdflink[['TOID', 'localid', 'startnode_href', 'endnode_href', 
                   'directionality_title', 'routehierarchy', 'geometry']]

gdfnode = gdfnode[['TOID', 'localid', 'geometry']]

valid_nodes = gdfnode['TOID'].unique()

gdflink1 = gdflink[(gdflink['startnode_href'].isin(valid_nodes)) & 
                   (gdflink['endnode_href'].isin(valid_nodes))].reset_index(drop=True)
print(gdflink1.shape)

valid_startnodes = gdflink1['startnode_href'].unique()
valid_endnodes = gdflink1['endnode_href'].unique()

gdfnode1 = gdfnode[(gdfnode['TOID'].isin(valid_startnodes)) | 
                   (gdfnode['TOID'].isin(valid_endnodes))].reset_index(drop=True)
print(gdfnode1.shape)

gdflink1 = gdflink1[gdflink1.geometry.type != 'MultiLineString']
print(gdflink1.shape)

OutPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1.gpkg"
OutLink = "RoadLink1"
gdflink1.to_file(OutPath, layer=OutLink, driver='GPKG')
OutNode = "RoadNode1"
gdfnode1.to_file(OutPath, layer=OutNode, driver='GPKG')



#%%

import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString

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


InputPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads1.gpkg"
link_layer = "RoadLink1"
node_layer = "RoadNode1"

gdflink = gpd.read_file(filename=InputPath, layer=link_layer)
gdfnode = gpd.read_file(filename=InputPath, layer=node_layer)

print(gdflink.isna().sum())
print(gdfnode.isna().sum())

node_map = {origin: new for origin, new in zip(gdfnode['TOID'], range(1, len(gdfnode)+1))}
gdfnode['node_id'] = gdfnode['TOID'].map(node_map)


print(gdflink['directionality_title'].unique())

gdflink['from_node'] = gdflink['startnode_href']
gdflink['to_node'] = gdflink['endnode_href']

gdflink['dir'] = gdflink['directionality_title']

# print(gdflink[['TOID', 'from_node', 'to_node']])
# print(gdflink[gdflink['dir']=='in opposite direction'][['TOID', 'from_node', 'to_node']])
# print(gdflink[gdflink['dir']=='in opposite direction']['geometry'])

# reverse geometry
def swap_and_reverse(row):
    if row['dir'] == 'in opposite direction':
        row[['from_node', 'to_node']] = row[['to_node', 'from_node']]
        row['geometry'] = LineString(row['geometry'].coords[::-1])
    return row

gdflink.loc[gdflink['dir']=='in opposite direction'] = gdflink.loc[gdflink['dir'] == 'in opposite direction'].apply(lambda row: swap_and_reverse(row), axis=1)

# print(gdflink[['TOID', 'from_node', 'to_node']])
# print(gdflink[gdflink['dir']=='in opposite direction'][['TOID', 'from_node', 'to_node']])
# print(gdflink[gdflink['dir']=='in opposite direction']['geometry'])

gdflink.loc[gdflink['dir']=='in opposite direction', 'dir'] = 'in direction'

print(gdflink['dir'].unique())

gdflink.loc[gdflink['dir']=='both directions', 'dir'] = 0
gdflink.loc[gdflink['dir']=='in direction', 'dir'] = 1
gdflink['dir'] = gdflink['dir'].astype(int)

gdflink['from_node'] = gdflink['from_node'].map(node_map)
gdflink['to_node'] = gdflink['to_node'].map(node_map)

gdflink['from_node'] = gdflink['from_node'].astype(int)
gdflink['to_node'] = gdflink['to_node'].astype(int)

print(gdflink[['from_node', 'to_node', 'dir']])

gdflink['link_id'] = [i for i in range(1, len(gdflink)+1)]

gdflink['length'] = gdflink['geometry'].length

print(gdflink.crs)
print(gdfnode.crs)

gdflink1 = gdflink.to_crs('EPSG:4326')
gdfnode1 = gdfnode.to_crs('EPSG:4326')

print(gdflink1.dtypes)
print(gdfnode1.dtypes)

OutPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads2_wgs.gpkg"
OutLink = "RoadLink2"
gdflink1.to_file(OutPath, layer=OutLink, driver='GPKG')
OutNode = "RoadNode2"
gdfnode1.to_file(OutPath, layer=OutNode, driver='GPKG')



#%%

import geopandas as gpd
import gotrackit.netreverse.NetGen as ng

if __name__ == '__main__':
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
    
    # circle road process, the same startnode and endnode
    InputPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads2_wgs.gpkg"
    link_layer = "RoadLink2"
    node_layer = "RoadNode2"
    link = gpd.read_file(filename=InputPath, layer=link_layer)
    print(link.crs)
    node = gpd.read_file(filename=InputPath, layer=node_layer)
    print(node.crs)
    
    newlink, newnode = ng.NetReverse.circle_process(link_gdf=link, node_gdf=node)
    
    newlink = newlink.to_crs('EPSG:4326')
    newnode = newnode.to_crs('EPSG:4326')
    
    OutPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads2_wgs.gpkg"
    out_link = "RoadLink3"
    out_node = "RoadNode3"
    
    newlink.to_file(OutPath, layer=out_link, driver='GPKG')
    newnode.to_file(OutPath, layer=out_node, driver='GPKG')
    
    
    path_idmap = "N:\\compass\\compasspro\\matchpro\\idmap\\"

    node_id = newnode[['TOID', 'node_id']]   
    nodeid_csv = os.path.join(path_idmap, f"nodeid_{region}.csv")
    node_id.to_csv(nodeid_csv, index=False)

    link_id = newlink[['TOID', 'link_id']]   
    linkid_csv = os.path.join(path_idmap, f"linkid_{region}.csv")
    link_id.to_csv(linkid_csv, index=False)


#%%
import os
import pandas as pd
import geopandas as gpd
from gotrackit.map.Net import Net
from gotrackit.MapMatch import MapMatch


if __name__ == '__main__':
    # read gps data
    
    # region = "Cambridge"
    # region = "SouthYorkshire"
    # region = "Liverpool"
    # region = "Glasgow"
    
    parquet_folder = f"N:\\compass\\compasspro\\parquetdata\\{region}\\"
    
    InputPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads2_wgs.gpkg"
    link_layer = "RoadLink3"
    node_layer = "RoadNode3"
    link = gpd.read_file(filename=InputPath, layer=link_layer)
    print(link.crs)
    node = gpd.read_file(filename=InputPath, layer=node_layer)
    print(node.crs)

    for filename in os.listdir(parquet_folder):
        if filename.endswith('.parquet'):
            parquet_file = os.path.join(parquet_folder, filename)
            parquet_name = os.path.splitext(filename)[0]
            
            gps_df = pd.read_parquet(parquet_file)
            my_net = Net(link_gdf=link, node_gdf=node)
            my_net.init_net()
            
            # alter para: gps_buffer, beta - larger, gps_sigma - smaller, use_heading_inf, omitted_l - smaller    
            # instant export results, and geo results 
            
            results_path = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\{parquet_name}"
            os.makedirs(results_path, exist_ok=True)
        
            mpm = MapMatch(net=my_net, use_sub_net=True, gps_df=gps_df, time_format="%Y-%m-%d %H:%M:%S", 
                            time_unit='s', gps_buffer=15.0, gps_route_buffer_gap=10.0, max_increment_times=1, 
                            increment_buffer=10.0, beta=10.0, gps_sigma=5.0, top_k=10, dis_para=0.1, 
                            is_lower_f=False, is_rolling_average=False, use_heading_inf=True, omitted_l=2.0, 
                            dense_gps=False, del_dwell=False, instant_output=True, out_fldr=results_path, 
                            export_geo_res=True, export_html=False)
            
            # results, warnings, and error match
            match_res, may_error_info, error_info = mpm.execute()
            print(match_res)
            
            may_error_txt = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\may_error_{parquet_name}.txt"
            with open(may_error_txt, mode='w') as file:
                for key, value in may_error_info.items():
                    file.write(f'{key}: {value}\n')
                file.write('\n')
                
            error_list_txt = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\error_list_{parquet_name}.txt"
            with open(error_list_txt, mode='w') as filex:
                for item in error_info:
                    filex.write(f'{item}\n')

#%%
import os
import pandas as pd
import geopandas as gpd
from gotrackit.map.Net import Net
from gotrackit.MapMatch import MapMatch


if __name__ == '__main__':
    # read gps data
    
    # region = "Oxford"
    # region = "Cardiff"
    # region = "Newcastle"
    region = "Edinburgh"
        
    parquet_folder = f"N:\\compass\\compasspro\\parquetdata\\{region}\\"
    
    InputPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads2_wgs.gpkg"
    link_layer = "RoadLink3"
    node_layer = "RoadNode3"
    link = gpd.read_file(filename=InputPath, layer=link_layer)
    print(link.crs)
    node = gpd.read_file(filename=InputPath, layer=node_layer)
    print(node.crs)

    for filename in os.listdir(parquet_folder):
        if filename.endswith('.parquet'):
            parquet_file = os.path.join(parquet_folder, filename)
            parquet_name = os.path.splitext(filename)[0]
            
            gps_df = pd.read_parquet(parquet_file)
            my_net = Net(link_gdf=link, node_gdf=node)
            my_net.init_net()
            
            # alter para: gps_buffer, beta - larger, gps_sigma - smaller, use_heading_inf, omitted_l - smaller    
            # instant export results, and geo results 
            
            results_path = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\{parquet_name}"
            os.makedirs(results_path, exist_ok=True)
        
            mpm = MapMatch(net=my_net, use_sub_net=True, gps_df=gps_df, time_format="%Y-%m-%d %H:%M:%S", 
                            time_unit='s', gps_buffer=15.0, gps_route_buffer_gap=10.0, max_increment_times=1, 
                            increment_buffer=10.0, beta=10.0, gps_sigma=5.0, top_k=10, dis_para=0.1, 
                            is_lower_f=False, is_rolling_average=False, use_heading_inf=True, omitted_l=2.0, 
                            dense_gps=False, del_dwell=False, instant_output=True, out_fldr=results_path, 
                            export_geo_res=True, export_html=False)
            
            # results, warnings, and error match
            match_res, may_error_info, error_info = mpm.execute()
            print(match_res)
            
            may_error_txt = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\may_error_{parquet_name}.txt"
            with open(may_error_txt, mode='w') as file:
                for key, value in may_error_info.items():
                    file.write(f'{key}: {value}\n')
                file.write('\n')
                
            error_list_txt = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\error_list_{parquet_name}.txt"
            with open(error_list_txt, mode='w') as filex:
                for item in error_info:
                    filex.write(f'{item}\n')


#%%
import os
import pandas as pd
import geopandas as gpd
from gotrackit.map.Net import Net
from gotrackit.MapMatch import MapMatch


if __name__ == '__main__':
    # read gps data
    partitions = [
        range(1, 21), # chunk1 - chunk20
        range(21, 41), # chunk21 - chunk40
        range(41, 61), # chunk41 - chunk60
        range(61, 81), # chunk61 - chunk80
        range(81, 101) # chunk81 - chunk101
        ]
    
    # partition_to_process = partitions[0]
    # partition_to_process = partitions[1]
    # partition_to_process = partitions[2]
    # partition_to_process = partitions[3]
    partition_to_process = partitions[4]
    
    # region = "WestEngland"
    region = "WestMidlands"
        
    parquet_folder = f"N:\\compass\\compasspro\\parquetdata\\{region}\\"
    
    InputPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads2_wgs.gpkg"
    link_layer = "RoadLink3"
    node_layer = "RoadNode3"
    link = gpd.read_file(filename=InputPath, layer=link_layer)
    print(link.crs)
    node = gpd.read_file(filename=InputPath, layer=node_layer)
    print(node.crs)

    for parquet_index in partition_to_process:
        parquet_name = f'chunk_{parquet_index}.parquet'
        parquet_file = os.path.join(parquet_folder, parquet_name)
        
        # gps_df = pd.read_csv(csv_file)
        gps_df = pd.read_parquet(parquet_file)
        my_net = Net(link_gdf=link, node_gdf=node)
        my_net.init_net()
        
        # alter para: gps_buffer, beta - larger, gps_sigma - smaller, use_heading_inf, omitted_l - smaller    
        # instant export results, and geo results 
        
        results_path = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\chunk_{parquet_index}"
        os.makedirs(results_path, exist_ok=True)
    
        mpm = MapMatch(net=my_net, use_sub_net=True, gps_df=gps_df, time_format="%Y-%m-%d %H:%M:%S", 
                        time_unit='s', gps_buffer=15.0, gps_route_buffer_gap=10.0, max_increment_times=1, 
                        increment_buffer=10.0, beta=10.0, gps_sigma=5.0, top_k=10, dis_para=0.1, 
                        is_lower_f=False, is_rolling_average=False, use_heading_inf=True, omitted_l=2.0, 
                        dense_gps=False, del_dwell=False, instant_output=True, out_fldr=results_path, 
                        export_geo_res=True, export_html=False)
        
        # results, warnings, and error match
        match_res, may_error_info, error_info = mpm.execute()
        print(match_res)
        
        may_error_txt = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\may_error_chunk_{parquet_index}.txt"
        with open(may_error_txt, mode='w') as file:
            for key, value in may_error_info.items():
                file.write(f'{key}: {value}\n')
            file.write('\n')
            
        error_list_txt = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\error_list_chunk_{parquet_index}.txt"
        with open(error_list_txt, mode='w') as filex:
            for item in error_info:
                filex.write(f'{item}\n')


#%%
import os
import pandas as pd
import geopandas as gpd
from gotrackit.map.Net import Net
from gotrackit.MapMatch import MapMatch


if __name__ == '__main__':
    # read gps data
    partitions = [
        range(1, 21), # chunk1 - chunk20
        range(21, 41), # chunk21 - chunk40
        range(41, 61), # chunk41 - chunk60
        range(61, 81), # chunk61 - chunk80
        range(81, 101) # chunk81 - chunk101
        ]
    
    # partition_to_process = partitions[0]
    # partition_to_process = partitions[1]
    # partition_to_process = partitions[2]
    # partition_to_process = partitions[3]
    partition_to_process = partitions[4]
    
    # region = "Manchester"
        
    parquet_folder = f"N:\\compass\\compasspro\\parquetdata\\{region}\\"
    
    InputPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads2_wgs.gpkg"
    link_layer = "RoadLink3"
    node_layer = "RoadNode3"
    link = gpd.read_file(filename=InputPath, layer=link_layer)
    print(link.crs)
    node = gpd.read_file(filename=InputPath, layer=node_layer)
    print(node.crs)

    for parquet_index in partition_to_process:
        parquet_name = f'chunk_{parquet_index}.parquet'
        parquet_file = os.path.join(parquet_folder, parquet_name)
        
        # gps_df = pd.read_csv(csv_file)
        gps_df = pd.read_parquet(parquet_file)
        my_net = Net(link_gdf=link, node_gdf=node)
        my_net.init_net()
        
        # alter para: gps_buffer, beta - larger, gps_sigma - smaller, use_heading_inf, omitted_l - smaller    
        # instant export results, and geo results 
        
        results_path = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\chunk_{parquet_index}"
        os.makedirs(results_path, exist_ok=True)
    
        mpm = MapMatch(net=my_net, use_sub_net=True, gps_df=gps_df, time_format="%Y-%m-%d %H:%M:%S", 
                        time_unit='s', gps_buffer=15.0, gps_route_buffer_gap=10.0, max_increment_times=1, 
                        increment_buffer=10.0, beta=10.0, gps_sigma=5.0, top_k=10, dis_para=0.1, 
                        is_lower_f=False, is_rolling_average=False, use_heading_inf=True, omitted_l=2.0, 
                        dense_gps=False, del_dwell=False, instant_output=True, out_fldr=results_path, 
                        export_geo_res=True, export_html=False)
        
        # results, warnings, and error match
        match_res, may_error_info, error_info = mpm.execute()
        print(match_res)
        
        may_error_txt = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\may_error_chunk_{parquet_index}.txt"
        with open(may_error_txt, mode='w') as file:
            for key, value in may_error_info.items():
                file.write(f'{key}: {value}\n')
            file.write('\n')
            
        error_list_txt = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\error_list_chunk_{parquet_index}.txt"
        with open(error_list_txt, mode='w') as filex:
            for item in error_info:
                filex.write(f'{item}\n')


#%%
import os
import pandas as pd
import geopandas as gpd
from gotrackit.map.Net import Net
from gotrackit.MapMatch import MapMatch


if __name__ == '__main__':
    # read gps data
    partitions = [
        range(1, 21), # chunk1 - chunk20
        range(21, 41), # chunk21 - chunk40
        range(41, 61), # chunk41 - chunk60
        range(61, 81), # chunk61 - chunk80
        range(81, 101) # chunk81 - chunk101
        ]
    
    # partition_to_process = partitions[0]
    # partition_to_process = partitions[1]
    # partition_to_process = partitions[2]
    # partition_to_process = partitions[3]
    # partition_to_process = partitions[4]
    
    # region = "WestYorkshire"
    
    parquet_folder = f"N:\\compass\\compasspro\\parquetdata\\{region}\\"
    
    InputPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads2_wgs.gpkg"
    link_layer = "RoadLink3"
    node_layer = "RoadNode3"
    link = gpd.read_file(filename=InputPath, layer=link_layer)
    print(link.crs)
    node = gpd.read_file(filename=InputPath, layer=node_layer)
    print(node.crs)

    for parquet_index in partition_to_process:
        parquet_name = f'chunk_{parquet_index}.parquet'
        parquet_file = os.path.join(parquet_folder, parquet_name)
        
        # gps_df = pd.read_csv(csv_file)
        gps_df = pd.read_parquet(parquet_file)
        my_net = Net(link_gdf=link, node_gdf=node)
        my_net.init_net()
        
        # alter para: gps_buffer, beta - larger, gps_sigma - smaller, use_heading_inf, omitted_l - smaller    
        # instant export results, and geo results 
        
        results_path = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\chunk_{parquet_index}"
        os.makedirs(results_path, exist_ok=True)
    
        mpm = MapMatch(net=my_net, use_sub_net=True, gps_df=gps_df, time_format="%Y-%m-%d %H:%M:%S", 
                        time_unit='s', gps_buffer=15.0, gps_route_buffer_gap=10.0, max_increment_times=1, 
                        increment_buffer=10.0, beta=10.0, gps_sigma=5.0, top_k=10, dis_para=0.1, 
                        is_lower_f=False, is_rolling_average=False, use_heading_inf=True, omitted_l=2.0, 
                        dense_gps=False, del_dwell=False, instant_output=True, out_fldr=results_path, 
                        export_geo_res=True, export_html=False)
        
        # results, warnings, and error match
        match_res, may_error_info, error_info = mpm.execute()
        print(match_res)
        
        may_error_txt = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\may_error_chunk_{parquet_index}.txt"
        with open(may_error_txt, mode='w') as file:
            for key, value in may_error_info.items():
                file.write(f'{key}: {value}\n')
            file.write('\n')
            
        error_list_txt = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\error_list_chunk_{parquet_index}.txt"
        with open(error_list_txt, mode='w') as filex:
            for item in error_info:
                filex.write(f'{item}\n')


#%%
import os
import pandas as pd
import geopandas as gpd
from gotrackit.map.Net import Net
from gotrackit.MapMatch import MapMatch


if __name__ == '__main__':
    # read gps data
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
    # partition_to_process = partitions[4]
    
    region = "London"
    
    parquet_folder = f"N:\\compass\\compasspro\\parquetdata\\{region}\\"
    
    InputPath = f"N:\\compass\\data\\geodata\\highways\\{region}\\Roads2_wgs.gpkg"
    link_layer = "RoadLink3"
    node_layer = "RoadNode3"
    link = gpd.read_file(filename=InputPath, layer=link_layer)
    print(link.crs)
    node = gpd.read_file(filename=InputPath, layer=node_layer)
    print(node.crs)

    for parquet_index in partition_to_process:
        parquet_name = f'chunk_{parquet_index}.parquet'
        parquet_file = os.path.join(parquet_folder, parquet_name)
        
        # gps_df = pd.read_csv(csv_file)
        gps_df = pd.read_parquet(parquet_file)
        my_net = Net(link_gdf=link, node_gdf=node)
        my_net.init_net()
        
        # alter para: gps_buffer, beta - larger, gps_sigma - smaller, use_heading_inf, omitted_l - smaller    
        # instant export results, and geo results 
        
        results_path = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\chunk_{parquet_index}"
        os.makedirs(results_path, exist_ok=True)
    
        mpm = MapMatch(net=my_net, use_sub_net=True, gps_df=gps_df, time_format="%Y-%m-%d %H:%M:%S", 
                        time_unit='s', gps_buffer=15.0, gps_route_buffer_gap=10.0, max_increment_times=1, 
                        increment_buffer=10.0, beta=10.0, gps_sigma=5.0, top_k=10, dis_para=0.1, 
                        is_lower_f=False, is_rolling_average=False, use_heading_inf=True, omitted_l=2.0, 
                        dense_gps=False, del_dwell=False, instant_output=True, out_fldr=results_path, 
                        export_geo_res=True, export_html=False)
        
        # results, warnings, and error match
        match_res, may_error_info, error_info = mpm.execute()
        print(match_res)
        
        may_error_txt = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\may_error_chunk_{parquet_index}.txt"
        with open(may_error_txt, mode='w') as file:
            for key, value in may_error_info.items():
                file.write(f'{key}: {value}\n')
            file.write('\n')
            
        error_list_txt = f"N:\\compass\\compasspro\\gpsmatch\\{region}\\error_list_chunk_{parquet_index}.txt"
        with open(error_list_txt, mode='w') as filex:
            for item in error_info:
                filex.write(f'{item}\n')


