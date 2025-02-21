

library(readxl)
library(dplyr)
library(ggplot2)
# year 2025 modified
# for all models
# Define network distances and speed limits
network_distances <- c("400m", "800m", "2km", "5km", "10km")
speed_limits <- c("mph20", "mph30", "mph40", "mph50", "mph60", "mph70")

# Initialize an empty list to collect data
model_data <- list()

# Functions to clean p-values and extract significance levels
clean_p_value <- function(p_value) {
  as.numeric(gsub("[^0-9.]", "", p_value))
}

extract_significance <- function(p_value) {
  gsub("[0-9.]", "", p_value)  # Extract non-numeric characters
}

# Loop through each distance and speed limit to read data
for (dist in network_distances) {
  # Read the "Total" model sheet for each distance
  file_path <- paste0("/Users/longpc/Documents/Leeds/plot2/mod_speeding_100m", dist, ".xlsx")
  total_data <- read_excel(file_path, sheet = dist) %>%
    select(Parameter, IRR, p_sig) %>%
    mutate(
      IRR = as.numeric(IRR),
      p_value_clean = clean_p_value(p_sig),                   # Clean numeric p-values
      IRR_sig = paste0(IRR, extract_significance(p_sig)),     # Create IRR_sig with significance level
      Network_Distance = dist,
      Speed_Limit = "Total"
    )
  
  model_data[[paste(dist, "Total", sep = "_")]] <- total_data
  
  # Read the individual speed limit sheets
  for (speed in speed_limits) {
    # Construct the sheet name
    sheet_name <- paste0(dist, "_", speed)
    
    # Read data from the specific sheet
    data <- read_excel(file_path, sheet = sheet_name) %>%
      select(Parameter, IRR, p_sig) %>%
      mutate(
        IRR = as.numeric(IRR),
        p_value_clean = clean_p_value(p_sig),                   # Clean numeric p-values
        IRR_sig = paste0(IRR, extract_significance(p_sig)),     # Create IRR_sig with significance level
        Network_Distance = dist,
        Speed_Limit = speed
      )
    
    # Append to list
    model_data[[sheet_name]] <- data
  }
}

# Combine all data into one data frame
combined_data <- bind_rows(model_data)

unique(combined_data$Parameter)

# Define the mapping of technical names to true names
variable_mapping <- c(
  "scale(traffic_calming_100m)" = "Traffic Calming",
  "scale(choker_counts_100m)" = "Choker",
  "scale(traffic_island_100m)" = "Island",
  "scale(signals_crossing_counts_100m)" = "Signalised Crossing",
  "scale(marked_counts_100m)" = "Marked Crossing",
  "scale(uncontrolled_counts_100m)" = "Uncontrolled Crossing",
  "scale(roundabout_new_100m)" = "Roundabout",
  "scale(mini_roundabout_counts_100m)" = "Mini Roundabout",
  "scale(motorway_junction_counts_100m)" = "Motorway Junction",
  "scale(signal_new_counts_100m)" = "Traffic Signal",
  "scale(camera_new_counts_100m)" = "Speed Camera",
  "scale(LConn)" = "Link Degree",
  "scale(LAC)" = "Link Angularity",
  "scale(LLen)" = "Link Length",
  "scale(averagewidth)" = "Link Average Width",
  "scale(both_direction)" = "Link Bidirection",
  "scale(Con400)" = "Connectivity",
  "scale(InvMHDWl400)" = "Closeness",
  "scale(BtHWl400)" = "Betweenness",
  "scale(MGLHWl400)" = "Average Shortest Path",
  "scale(DivHWl400)" = "Diversion Ratio",
  "scale(Con800)" = "Connectivity",
  "scale(InvMHDWl800)" = "Closeness",
  "scale(BtHWl800)" = "Betweenness",
  "scale(MGLHWl800)" = "Average Shortest Path",
  "scale(DivHWl800)" = "Diversion Ratio",
  "scale(Con2000)" = "Connectivity",
  "scale(InvMHDWl2000)" = "Closeness",
  "scale(BtHWl2000)" = "Betweenness",
  "scale(MGLHWl2000)" = "Average Shortest Path",
  "scale(DivHWl2000)" = "Diversion Ratio",
  "scale(Con5000)" = "Connectivity",
  "scale(InvMHDWl5000)" = "Closeness",
  "scale(MGLHWl5000)" = "Average Shortest Path",
  "scale(BtHWl5000)" = "Betweenness",
  "scale(DivHWl5000)" = "Diversion Ratio",
  "scale(Con10000)" = "Connectivity",
  "scale(InvMHDWl10000)" = "Closeness",
  "scale(BtHWl10000)" = "Betweenness",
  "scale(MGLHWl1000)" = "Average Shortest Path",
  "scale(DivHWl1000)" = "Diversion Ratio",
  "speedLimit_group_new20" = "Speed Limit 20 mph",
  "speedLimit_group_new30" = "Speed Limit 30 mph",
  "speedLimit_group_new40" = "Speed Limit 40 mph",
  "speedLimit_group_new50" = "Speed Limit 50 mph",
  "speedLimit_group_new60" = "Speed Limit 60 mph"
)

# Apply variable mapping to the 'Parameter' column without setting factor levels yet
combined_data <- combined_data %>%
  filter(!Parameter %in% c("(Intercept)")) %>%
  mutate(
    Parameter = recode(Parameter, !!!variable_mapping)
  )

unique(combined_data$Parameter)

# Define the desired order of variables for the y-axis
desired_order <- c(
  "Traffic Calming",
  "Choker",
  "Island",
  "Signalised Crossing",
  "Marked Crossing",
  "Uncontrolled Crossing",
  "Roundabout",
  "Mini Roundabout",
  "Motorway Junction",
  "Traffic Signal",
  "Speed Camera",
  "Link Degree",
  "Link Angularity",
  "Link Length",
  "Link Average Width",
  "Link Bidirection",
  "Connectivity",
  "Closeness",
  "Betweenness",
  "Average Shortest Path",
  "Diversion Ratio",
  "Speed Limit 20 mph",
  "Speed Limit 30 mph",
  "Speed Limit 40 mph",
  "Speed Limit 50 mph",
  "Speed Limit 60 mph"
)


# Set 'Parameter' as a factor with the reversed order of levels
combined_data <- combined_data %>%
  mutate(
    Parameter = factor(Parameter, levels = rev(desired_order))
  )

combined_data <- combined_data %>%
  filter(p_value_clean < 0.05)  # Filter only significant results

# Apply custom color and IRR band mapping
cutoff_values <- c(-Inf, 0.5, 0.7, 0.8, 0.9, 0.95, 1, 1.05, 1.1, 1.25, 2, 5, Inf)
labels <- c("< 0.5", "0.5 - 0.7", "0.7 - 0.8", "0.8 - 0.9", "0.9 - 0.95", "0.95 - 1",
            "1 - 1.05", "1.05 - 1.1", "1.1 - 1.25", "1.25 - 2", "2 - 5", "> 5")

# Define the custom ordering for `Model_Distance` by expanding each Speed_Limit over all Network_Distances
# Apply the custom order to `Model_Distance`
combined_data <- combined_data %>%
  mutate(
    Model_Distance = paste(Speed_Limit, Network_Distance, sep = "_")
  )

colnames(combined_data)
unique(combined_data$Model_Distance)

# Create a copy of Model_Distance column
combined_data$Model_Distance_new <- combined_data$Model_Distance

# Define the mapping of levels for renaming
level_mapping <- c(
  "Total_400m" = "400m All Links",
  "mph20_400m" = "400m 20 mph",
  "mph30_400m" = "400m 30 mph",
  "mph40_400m" = "400m 40 mph",
  "mph50_400m" = "400m 50 mph",
  "mph60_400m" = "400m 60 mph",
  "mph70_400m" = "400m 70 mph",
  "Total_800m" = "800m All Links",
  "mph20_800m" = "800m 20 mph",
  "mph30_800m" = "800m 30 mph",
  "mph40_800m" = "800m 40 mph",
  "mph50_800m" = "800m 50 mph",
  "mph60_800m" = "800m 60 mph",
  "mph70_800m" = "800m 70 mph",
  "Total_2km" = "2km All Links",
  "mph20_2km" = "2km 20 mph",
  "mph30_2km" = "2km 30 mph",
  "mph40_2km" = "2km 40 mph",
  "mph50_2km" = "2km 50 mph",
  "mph60_2km" = "2km 60 mph",
  "mph70_2km" = "2km 70 mph",
  "Total_5km" = "5km All Links",
  "mph20_5km" = "5km 20 mph",
  "mph30_5km" = "5km 30 mph",
  "mph40_5km" = "5km 40 mph",
  "mph50_5km" = "5km 50 mph",
  "mph60_5km" = "5km 60 mph",
  "mph70_5km" = "5km 70 mph",
  "Total_10km" = "10km All Links",
  "mph20_10km" = "10km 20 mph",
  "mph30_10km" = "10km 30 mph",
  "mph40_10km" = "10km 40 mph",
  "mph50_10km" = "10km 50 mph",
  "mph60_10km" = "10km 60 mph",
  "mph70_10km" = "10km 70 mph"
)

# Apply the mapping to rename levels
combined_data$Model_Distance_new <- recode(combined_data$Model_Distance_new, !!!level_mapping)

# Verify the changes
unique(combined_data$Model_Distance_new)

model_distance_order_new <- unlist(lapply(c("All Links", "20 mph", "30 mph", "40 mph", "50 mph", "60 mph", "70 mph"), function(speed) {
  paste(network_distances, speed, sep = " ")
}))

# Set 'Model_Distance_new' as a factor with the reversed order of levels
combined_data <- combined_data %>%
  mutate(
    IRR_band = cut(IRR, breaks = cutoff_values, labels = labels, right = FALSE),
    Model_Distance_new = factor(Model_Distance_new, levels = model_distance_order_new)
  )

# Define color scheme
colors_below_1 <- c("#236da9", "#4a91c7", "#76afdb", "#a6cbea", "#d0e1f4", "#ebf3fc")
colors_above_1 <- c("#fde0e6", "#f9b8cd", "#f598c1", "#f47ab5", "#f05ca9", "#e63d9d")
all_colors <- c(colors_below_1, colors_above_1)


# Plot heatmap
heatmap_plot <- ggplot(combined_data, aes(x = Model_Distance_new, y = Parameter, fill = IRR_band)) +
  geom_tile(color = "white", linewidth = 0.2) +
  geom_text(aes(label = IRR_sig), color = "black", size = 1.6, family = "Arial") +
  scale_fill_manual(
    values = setNames(all_colors, labels),  # Map colors to IRR bands
    name = "IRR"
  ) +
  scale_x_discrete(expand = c(0.02, 0.02), labels = model_distance_order_new) +  # Align x-axis labels with custom order
  scale_y_discrete(expand = c(0.03, 0.03)) +  # Remove y-axis padding
  labs(
    x = "Models for road links with varying speed limits across different network distances",
    # y = "Independent variables",
    y = NULL,
    title = "Incidence Rate Ratio in Models by Speed Limits and Network Distances"
  ) +
  theme_linedraw(base_size = 14, base_family = "Arial") +
  theme(
    panel.grid = element_blank(), 
    axis.line = element_blank(),
    panel.border = element_rect(color = "black", fill = NA, linewidth = 0.8),
    axis.ticks = element_line(color = "black", linewidth = 0.4),
    axis.ticks.length = unit(0.16, "cm"),
    axis.text = element_text(color = "black", family = "Arial"),
    axis.text.x = element_text(size = 10, angle = 45, hjust = 1, color = "black", family = "Arial"),  # Angled x-axis text for readability
    axis.text.y = element_text(size = 12, color = "black", family = "Arial"),
    plot.title = element_text(size = 14, color = "black", margin = margin(b = 5), family = "Arial"), 
    axis.title.x = element_text(size = 14, color = "black", margin = margin(t = 6), family = "Arial"), 
    axis.title.y = element_text(size = 14, color = "black", margin = margin(r = 6), family = "Arial"),
    legend.position = "right",
    legend.spacing.x = unit(0.3, "cm"),  # Space between legend keys horizontally
    legend.spacing.y = unit(0.5, "cm"),  # Space between legend keys vertically
    legend.title = element_text(size = 12, family = "Arial"),  
    legend.text = element_text(size = 12, family = "Arial"),  
    legend.margin = margin(t = 0, r = 0, b = 0, l = 0),  
    plot.margin = margin(t = 2, r = 2, b = 2, l = 2)
  )

# Display the heatmap plot
print(heatmap_plot)

ggsave(filename = "/Users/longpc/Documents/Leeds/plot2/fig/IRR_Speed_Limits_all.png", plot = heatmap_plot, width = 12.8, height = 8.8, dpi = 600)




# Example positions for adding vertical and horizontal lines
vline_positions <- c(5, 10, 15, 20, 25, 30)  # Positions for vertical lines (between columns)
hline_positions <- c(5, 10, 15)  # Positions for horizontal lines (between rows)

# Create the heatmap plot with additional lines
heatmap_plot <- ggplot(combined_data, aes(x = Model_Distance_new, y = Parameter, fill = IRR_band)) +
  geom_tile(color = "white", linewidth = 0.2) +
  geom_text(aes(label = IRR_sig), color = "black", size = 1.6, family = "Arial") +
  scale_fill_manual(
    values = setNames(all_colors, labels),  # Map colors to IRR bands
    name = "IRR"
  ) +
  scale_x_discrete(expand = c(0.02, 0.02), labels = model_distance_order_new) +  # Align x-axis labels with custom order
  scale_y_discrete(expand = c(0.03, 0.03)) +  # Remove y-axis padding
  labs(
    x = "Models for road links with varying speed limits across different network distances",
    y = NULL,
    title = "Incidence Rate Ratio in Models by Speed Limits and Network Distances"
  ) +
  theme_linedraw(base_size = 14, base_family = "Arial") +
  theme(
    panel.grid = element_blank(), 
    axis.line = element_blank(),
    panel.border = element_rect(color = "black", fill = NA, linewidth = 0.8),
    axis.ticks = element_line(color = "black", linewidth = 0.4),
    axis.ticks.length = unit(0.16, "cm"),
    axis.text = element_text(color = "black", family = "Arial"),
    axis.text.x = element_text(size = 10, angle = 45, hjust = 1, color = "black", family = "Arial"),  # Angled x-axis text for readability
    axis.text.y = element_text(size = 12, color = "black", family = "Arial"),
    plot.title = element_text(size = 14, color = "black", margin = margin(b = 5), family = "Arial"), 
    axis.title.x = element_text(size = 14, color = "black", margin = margin(t = 6), family = "Arial"), 
    axis.title.y = element_text(size = 14, color = "black", margin = margin(r = 6), family = "Arial"),
    legend.position = "right",
    legend.spacing.x = unit(0.3, "cm"),  # Space between legend keys horizontally
    legend.spacing.y = unit(0.5, "cm"),  # Space between legend keys vertically
    legend.title = element_text(size = 12, family = "Arial"),  
    legend.text = element_text(size = 12, family = "Arial"),  
    legend.margin = margin(t = 0, r = 0, b = 0, l = 0),  
    plot.margin = margin(t = 2, r = 2, b = 2, l = 2)
  ) +
  # Add vertical lines between specific columns
  geom_vline(xintercept = vline_positions + 0.5, color = "white", linewidth = 1) +
  # Add horizontal lines between specific rows
  geom_hline(yintercept = hline_positions + 0.5, color = "white", linewidth = 1)

# Display the heatmap plot
print(heatmap_plot)

ggsave(filename = "/Users/longpc/Documents/Leeds/plot2/fig/IRR_Speed_Limits_all.png", plot = heatmap_plot, width = 12.8, height = 8.8, dpi = 600)











