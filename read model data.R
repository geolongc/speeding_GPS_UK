library(sf)
library(dplyr)



# Define the list of regions
regions_list <- c("London", "WestEngland", "Oxford", "Cambridge", "Newcastle", 
                  "Edinburgh", "Glasgow", "WestYorkshire", "SouthYorkshire", 
                  "Manchester", "Cardiff", "Liverpool", "WestMidlands")

# Loop through each region
for (region in regions_list) {
  
  # Define the paths for speed limit and highway data
  path_speedlimit <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/export/RoadLinks/", region, "/Roads1_regroup.gpkg")
  
  # Define the layers
  layer_speedlimit <- "RoadLink1y_q1"
  
  # Read the speed limit data
  data_speedlimit <- st_read(path_speedlimit, layer = layer_speedlimit)
  
  # Select relevant columns from speed limit data
  data_speedlimit <- data_speedlimit %>%
    select(TOID, localid, roadLinkID, startnode_href, endnode_href, directionality_title,
           routehierarchy, routehierarchy_group, speedLimit_mph, speedLimit_group,
           link_adhrate, avg_speed, geom)
  
  # Calculate the length of each road link
  data_speedlimit$length_meters <- st_length(data_speedlimit)
  data_speedlimit$length_meters_numeric <- as.numeric(st_length(data_speedlimit))
  
  # data_speedlimit_x <- data_speedlimit[!is.na(data_speedlimit$link_adhrate), ]
  # print(nrow(data_speedlimit_x))
  
  # Add a new column with the region name
  data_speedlimit$city <- region
  
  # speed events
  path_speedevents <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/export/highways_z/", region, "/Roads1_regroup_count.gpkg")
  layer_speedevents <- "RoadLink1y_q1"
  
  data_speedevents <- st_read(path_speedevents, layer = layer_speedevents)
  data_speedevents <- st_drop_geometry(data_speedevents)
  
  data_speedevents <- data_speedevents %>%
    select(TOID, ptcount, link_speedingcount)
  
  data_merged <- merge(data_speedlimit, data_speedevents, by = "TOID", all.x = TRUE)
  
  # Read the highway data
  # Define the paths for highway data
  path_highway <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/digidown/highways_x/", region, "/Roads1.gpkg")
  # Define the layers
  layer_highway <- "RoadLink"
  
  data_highway <- st_read(path_highway, layer = layer_highway)
  data_highway <- st_drop_geometry(data_highway)
  
  # Select relevant columns from highway data
  data_highway <- data_highway %>%
    select(TOID, formofway, trunkroad, primaryroute, length, formspartof_role,
           averagewidth, minimumwidth)
  
  # Merge speed limit and highway data by 'TOID'
  data_merged <- merge(data_merged, data_highway, by = "TOID", all.x = TRUE)
  
  # data_merged_temp <- subset(data_merged, formofway %in% c("Dual Carriageway", "Single Carriageway"))
  # print(paste("Number of rows/carriageway:", nrow(data_merged_temp)))
  
  # roadlink_trafficcalming
  path_calming <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/", region, "/roadlink_trafficcalming.gpkg")
  layer_calming <- "roadlink_trafficcalming"
  
  data_calming <- st_read(path_calming, layer = layer_calming)
  data_calming <- st_drop_geometry(data_calming)
  # print(colnames(data_calming))
  data_calming <- data_calming %>% select(-directionality_title, -edge_id)
  data_merged <- merge(data_merged, data_calming, by = "TOID", all.x = TRUE)
  
  # roadlink_crossing
  path_crossing <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/", region, "/roadlink_crossing.gpkg")
  layer_crossing <- "roadlink_crossing"

  data_crossing <- st_read(path_crossing, layer = layer_crossing)
  data_crossing <- st_drop_geometry(data_crossing)
  # print(colnames(data_crossing))
  data_crossing <- data_crossing %>% select(-directionality_title, -edge_id)
  data_merged <- merge(data_merged, data_crossing, by = "TOID", all.x = TRUE)
  
  # roadlink_crossing_island
  path_crossing_island <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/", region, "/roadlink_crossing_island.gpkg")
  layer_crossing_island <- "roadlink_crossing_island"
  
  data_crossing_island <- st_read(path_crossing_island, layer = layer_crossing_island)
  data_crossing_island <- st_drop_geometry(data_crossing_island)
  # print(colnames(data_crossing_island))
  data_crossing_island <- data_crossing_island %>% select(-directionality_title, -edge_id)
  data_merged <- merge(data_merged, data_crossing_island, by = "TOID", all.x = TRUE)
  
  # roadlink_junction
  path_junction <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/", region, "/roadlink_junction.gpkg")
  layer_junction <- "roadlink_junction"
  
  data_junction <- st_read(path_junction, layer = layer_junction)
  data_junction <- st_drop_geometry(data_junction)
  # print(colnames(data_junction))
  data_junction <- data_junction %>% select(-directionality_title, -edge_id)
  data_merged <- merge(data_merged, data_junction, by = "TOID", all.x = TRUE)
  
  # roadlink_speedcamera
  path_camera <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/", region, "/roadlink_speedcamera.gpkg")
  layer_camera <- "roadlink_speedcamera"

  data_camera <- st_read(path_camera, layer = layer_camera)
  data_camera <- st_drop_geometry(data_camera)
  # print(colnames(data_camera))
  data_camera <- data_camera %>% select(-directionality_title, -edge_id)
  data_merged <- merge(data_merged, data_camera, by = "TOID", all.x = TRUE)
  
  # roadlink_trafficsignal
  path_signal <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/OSM/osmpro_undirect_snapped/", region, "/roadlink_trafficsignal.gpkg")
  layer_signal <- "roadlink_trafficsignal"
  
  data_signal <- st_read(path_signal, layer = layer_signal)
  data_signal <- st_drop_geometry(data_signal)
  # print(colnames(data_signal))
  data_signal <- data_signal %>% select(-directionality_title, -traffic_signals_counts, -traffic_signals_counts_50m, -traffic_signals_counts_100m, -traffic_signals_counts_200m, -edge_id)
  data_merged <- merge(data_merged, data_signal, by = "TOID", all.x = TRUE)
  
  # sDNA
  path_sdna <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/highways_sDNA_new/", region, "/Roads_sDNA.gpkg")
  
  layer_sdna <- "sDNA_join_toid"
  
  data_sdna <- st_read(path_sdna, layer = layer_sdna)
  data_sdna <- st_drop_geometry(data_sdna)
  
  data_sdna <- data_sdna %>% select(-ID, -index_right)
  data_merged <- merge(data_merged, data_sdna, by = "TOID", all.x = TRUE)
  
  # Dynamically create a variable to store the merged data
  # For example, for London, it will create a variable called 'data_merged_London'
  assign(paste0("data_merged_", region), data_merged)
  
  # Print some info for debugging
  print(paste("Region:", region))
  print(paste("Number of rows:", nrow(data_merged)))
  print(paste("Number of distinct TOIDs:", n_distinct(data_merged$TOID)))
}



# List of variables to keep
keep_vars <- c("data_merged_London", 
               "data_merged_WestEngland", 
               "data_merged_Oxford", 
               "data_merged_Cambridge", 
               "data_merged_Newcastle", 
               "data_merged_Edinburgh", 
               "data_merged_Glasgow", 
               "data_merged_WestYorkshire", 
               "data_merged_SouthYorkshire", 
               "data_merged_Manchester", 
               "data_merged_Cardiff", 
               "data_merged_Liverpool", 
               "data_merged_WestMidlands")

# Remove all objects except those in 'keep_vars'
rm(list = setdiff(ls(), keep_vars))

# Create a vector of variable names dynamically based on the regions
regions_list <- c("London", "WestEngland", "Oxford", "Cambridge", "Newcastle", 
                  "Edinburgh", "Glasgow", "WestYorkshire", "SouthYorkshire", 
                  "Manchester", "Cardiff", "Liverpool", "WestMidlands")

merged_var_names <- paste0("data_merged_", regions_list)

# Use mget() to retrieve all the dynamically created data frames and store them in a list
merged_data_list <- mget(merged_var_names)

# Bind all the data frames together into one
data_combined <- bind_rows(merged_data_list)

keep_vars <- c("data_merged_London", 
               "data_merged_WestYorkshire", 
               "data_combined")

rm(list = setdiff(ls(), keep_vars))

colnames(data_combined)
sapply(data_combined, function(x) sum(is.na(x)))
print(nrow(data_combined))
print(n_distinct(data_combined$TOID))


path_speedlimit_London <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/export/RoadLinks/", region, "/Roads1_regroup.gpkg")
layer_speedlimit_London <- "RoadLink1y_q1"



st_write(data_merged_Cambridge, "/Users/longpc/Documents/Leeds/data/geocompass/geodata_r/data_Cambridge.gpkg", layer = "Cambridge", driver = "GPKG")

st_write(data_merged_Cardiff, "/Users/longpc/Documents/Leeds/data/geocompass/geodata_r/data_Cardiff.gpkg", layer = "Cardiff", driver = "GPKG")

st_write(data_merged_Edinburgh, "/Users/longpc/Documents/Leeds/data/geocompass/geodata_r/data_Edinburgh.gpkg", layer = "Edinburgh", driver = "GPKG")

st_write(data_merged_Glasgow, "/Users/longpc/Documents/Leeds/data/geocompass/geodata_r/data_Glasgow.gpkg", layer = "Glasgow", driver = "GPKG")

st_write(data_merged_Liverpool, "/Users/longpc/Documents/Leeds/data/geocompass/geodata_r/data_Liverpool.gpkg", layer = "Liverpool", driver = "GPKG")

st_write(data_merged_London, "/Users/longpc/Documents/Leeds/data/geocompass/geodata_r/data_London.gpkg", layer = "London", driver = "GPKG")

st_write(data_merged_Manchester, "/Users/longpc/Documents/Leeds/data/geocompass/geodata_r/data_Manchester.gpkg", layer = "Manchester", driver = "GPKG")

st_write(data_merged_Newcastle, "/Users/longpc/Documents/Leeds/data/geocompass/geodata_r/data_Newcastle.gpkg", layer = "Newcastle", driver = "GPKG")

st_write(data_merged_Oxford, "/Users/longpc/Documents/Leeds/data/geocompass/geodata_r/data_Oxford.gpkg", layer = "Oxford", driver = "GPKG")

st_write(data_merged_SouthYorkshire, "/Users/longpc/Documents/Leeds/data/geocompass/geodata_r/data_SouthYorkshire.gpkg", layer = "SouthYorkshire", driver = "GPKG")

st_write(data_merged_WestEngland, "/Users/longpc/Documents/Leeds/data/geocompass/geodata_r/data_WestEngland.gpkg", layer = "WestEngland", driver = "GPKG")

st_write(data_merged_WestMidlands, "/Users/longpc/Documents/Leeds/data/geocompass/geodata_r/data_WestMidlands.gpkg", layer = "WestMidlands", driver = "GPKG")

st_write(data_merged_WestYorkshire, "/Users/longpc/Documents/Leeds/data/geocompass/geodata_r/data_WestYorkshire.gpkg", layer = "WestYorkshire", driver = "GPKG")





