library(ggplot2)
library(sf)
library(viridis)
library(dplyr)
library(classInt)
library(extrafont)

# Import system fonts
font_import(paths = "/System/Library/Fonts")  # This registers macOS system fonts
loadfonts(device = "pdf")  # Loads fonts for PDF output

# Check that Arial is available
fonts()  # Confirm Arial appears in the list


# Speeding events plot
# List of regions to loop through
regions <- c("London", "WestEngland", "Oxford", "Cambridge", "Newcastle", 
             "Edinburgh", "Glasgow", "WestYorkshire", "SouthYorkshire", 
             "Manchester", "Cardiff", "Liverpool", "WestMidlands")

# Create empty vector to store link_speedingcount values
all_speeding_counts <- c()

# Loop through each region and gather link_speedingcount values
for (region in regions) {
  
  # Construct the file path for the GeoPackage
  path_speedevents <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/export/highways_z/", region, "/Roads1_regroup_count.gpkg")
  layer_speedevents <- "RoadLink1y_q1"
  link_speedevents <- st_read(path_speedevents, layer = layer_speedevents)
  
  # Collect link_speedingcount values and store them in the all_speeding_counts vector
  all_speeding_counts <- c(all_speeding_counts, link_speedevents$link_speedingcount)
}

# Display summary statistics for link_speedingcount
summary(all_speeding_counts)
table(all_speeding_counts)
sum(all_speeding_counts >= 0)

sum(all_speeding_counts == 0)
sum(all_speeding_counts >= 1 & all_speeding_counts < 3)
sum(all_speeding_counts >= 3 & all_speeding_counts < 10)
sum(all_speeding_counts >= 10 & all_speeding_counts < 50)
sum(all_speeding_counts >= 50 & all_speeding_counts < 200)
sum(all_speeding_counts >= 200 & all_speeding_counts < 500)
sum(all_speeding_counts >= 500)


# Filter speeding counts greater than 0
speeding_counts_gt0 <- all_speeding_counts[all_speeding_counts > 0]
num_classes <- 6
# Calculate natural breaks (Jenks)
breaks <- classIntervals(speeding_counts_gt0, n = num_classes, style = "jenks")
break_points <- breaks$brks
print(break_points)
# Classify the speeding counts using the natural breaks
classified_speeding_counts <- cut(speeding_counts_gt0, breaks = break_points, include.lowest = TRUE)

# Display the classified speeding counts
table(classified_speeding_counts)




# final use
# List of regions to loop through
regions <- c("London", "WestEngland", "Oxford", "Cambridge", "Newcastle", 
             "Edinburgh", "Glasgow", "WestYorkshire", "SouthYorkshire", 
             "Manchester", "Cardiff", "Liverpool", "WestMidlands")

# Create empty vector to store link_speedingcount values
all_speeding_counts <- c()

# Loop through each region and gather link_speedingcount values
for (region in regions) {
  
  # Construct the file path for the GeoPackage
  path_speedevents <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/export/highways_z/", region, "/Roads1_regroup_count.gpkg")
  layer_speedevents <- "RoadLink1y_q1"
  link_speedevents <- st_read(path_speedevents, layer = layer_speedevents)
  
  # read highways, join formofway
  path_highway <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/digidown/highways_x/", region, "/Roads1.gpkg")
  # Define the layers
  layer_highway <- "RoadLink"
  
  data_highway <- st_read(path_highway, layer = layer_highway)
  data_highway <- st_drop_geometry(data_highway)
  
  # Select relevant columns from highway data
  data_highway <- data_highway %>%
    select(TOID, formofway, averagewidth, minimumwidth)
  
  # Merge speed limit and highway data by 'TOID'
  link_speedevents <- merge(link_speedevents, data_highway, by = "TOID", all.x = TRUE)
  
  link_speedevents <- subset(link_speedevents, formofway %in% c("Dual Carriageway", "Single Carriageway"))
  
  link_speedevents <- link_speedevents[!is.na(link_speedevents$averagewidth), ]
  
  # Collect link_speedingcount values and store them in the all_speeding_counts vector
  all_speeding_counts <- c(all_speeding_counts, link_speedevents$link_speedingcount)
}

# Display summary statistics for link_speedingcount
summary(all_speeding_counts)
table(all_speeding_counts)
sum(all_speeding_counts >= 0)

sum(all_speeding_counts == 0)
sum(all_speeding_counts >= 1 & all_speeding_counts < 3)
sum(all_speeding_counts >= 3 & all_speeding_counts < 10)
sum(all_speeding_counts >= 10 & all_speeding_counts < 50)
sum(all_speeding_counts >= 50 & all_speeding_counts < 200)
sum(all_speeding_counts >= 200 & all_speeding_counts < 500)
sum(all_speeding_counts >= 500)

# Update breaks and labels to match the new ranges
breaks <- c(0, 1, 2, 3, 4, 5, 6)
labels <- c("0", "1 - 3", "3 - 10", "10 - 50", "50 - 200", "200 - 500", "> 500")

# Define custom colors for the specific ranges
custom_colors <- c("#ffffe5", "#fee8c8", "#FECC8FFF", "#F4685CFF", "#C03A76FF", "#802582FF", "#29115AFF")


regions <- c("London", "WestEngland", "Oxford", "Cambridge", "Newcastle", 
             "Edinburgh", "Glasgow", "WestYorkshire", "SouthYorkshire", 
             "Manchester", "Cardiff", "Liverpool", "WestMidlands")


regions <- c("Oxford", "Cambridge", "Cardiff") 

regions <- c("London", "Newcastle", "Edinburgh", "Glasgow", "Manchester", "Liverpool")

regions <- c("WestEngland", "WestYorkshire", "SouthYorkshire", "WestMidlands")
regions_name <- c("West of England", "West Yorkshire", "South Yorkshire", "West Midlands")
regions_map <- setNames(regions_name, regions)

# Loop through each region
for (region in regions) {
  
  # Construct the file path for the GeoPackage
  path_speedevents <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/export/highways_z/", region, "/Roads1_regroup_count.gpkg")
  layer_speedevents <- "RoadLink1y_q1"
  link_speedevents <- st_read(path_speedevents, layer = layer_speedevents)
  
  # read highways, join formofway
  path_highway <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/digidown/highways_x/", region, "/Roads1.gpkg")
  # Define the layers
  layer_highway <- "RoadLink"
  
  data_highway <- st_read(path_highway, layer = layer_highway)
  data_highway <- st_drop_geometry(data_highway)
  
  # Select relevant columns from highway data
  data_highway <- data_highway %>%
    select(TOID, formofway, averagewidth, minimumwidth)
  
  # Merge speed limit and highway data by 'TOID'
  link_speedevents <- merge(link_speedevents, data_highway, by = "TOID", all.x = TRUE)
  
  link_speedevents <- subset(link_speedevents, formofway %in% c("Dual Carriageway", "Single Carriageway"))
  
  link_speedevents <- link_speedevents[!is.na(link_speedevents$averagewidth), ]
  
  # Construct the file path for the region boundary data
  path_Boundary <- paste0("/Users/longpc/Documents/Leeds/data/geocompass/digidown/polygon_x/", region, ".shp")
  region_Boundary <- st_read(path_Boundary)
  
  link_speedevents$link_speedingcount <- ifelse(link_speedevents$link_speedingcount == 0, 0,
                                                ifelse(link_speedevents$link_speedingcount >= 1 & link_speedevents$link_speedingcount < 3, 1, ifelse(link_speedevents$link_speedingcount >= 3 & link_speedevents$link_speedingcount < 10, 2, ifelse(link_speedevents$link_speedingcount >= 10 & link_speedevents$link_speedingcount < 50, 3, ifelse(link_speedevents$link_speedingcount >= 50 & link_speedevents$link_speedingcount < 200, 4, ifelse(link_speedevents$link_speedingcount >= 200 & link_speedevents$link_speedingcount < 500, 5, ifelse(link_speedevents$link_speedingcount >= 500, 6, link_speedevents$link_speedingcount)))))))
  
  # arrange speeding counts
  link_speedevents <- link_speedevents %>%
    arrange(link_speedingcount)
  
  # Plot the 'link_speedingcount' values using ggplot2
  plot <- ggplot() +
    # geom_sf(data = link_speedevents, aes(color = link_speedingcount), linewidth = 0.34) +
    geom_sf(data = link_speedevents, aes(color = link_speedingcount), linewidth = 0.26) +
    geom_sf(data = region_Boundary, fill = NA, color = "black", linewidth = 0.32) + 
    scale_color_stepsn(
      colors = custom_colors,
      breaks = breaks, 
      labels = labels,
      limits = c(0, 7),
      oob = scales::squish,
      name = NULL
    ) + 
    theme_minimal() +
    labs(
      title = NULL, 
      # caption = paste("Speeding events on road links in", region) 
      caption = paste("Speeding events on road links in", regions_map[region])
    ) +
    theme(
      panel.background = element_blank(), 
      plot.background = element_rect(fill = "white", color = NA),
      panel.grid = element_blank(),
      plot.title = element_blank(),
      plot.caption = element_text(family = "Arial", hjust = 0.45, size = 14),
      plot.caption.position = "plot", 
      legend.text = element_text(family = "Arial", hjust = 0.5, vjust = -2.0),
      axis.text = element_blank(),
      axis.title = element_blank(), 
      legend.key.height = unit(2, "cm"),
      legend.key.width = unit(0.5, "cm")
    )
  
  # Display the plot
  # print(plot)
  
  # Save the plot as a PNG file
  ggsave(filename = paste0("/Users/longpc/Documents/Leeds/data/geocompass/plots/", region, "_RoadLinkSpeedingEvents.png"), 
         plot = plot, width = 10, height = 8, dpi = 600, device = "png")
  
  # Save the plot as an EPS file
  # ggsave(filename = paste0("/Users/longpc/Documents/Leeds/data/geocompass/plots/", region, "_RoadLinkSpeedingEvents.eps"), 
  #        plot = plot, width = 10, height = 8, dpi = 600, device = "eps")
}









