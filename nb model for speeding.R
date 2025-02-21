library(openxlsx) 
library(sf)
library(dplyr)
library(lme4)
library(car)
library(glmmTMB)
library(sjPlot)
library(lmerTest)
library(effectsize)
library(ggplot2)
library(viridis)


colnames(data_combined)
nrow(data_combined)
sapply(data_combined, function(x) sum(is.na(x)))
sapply(data_combined, function(x) min(x, na.rm = T))
sapply(data_combined, function(x) max(x, na.rm = T))

table(data_combined$formofway)   
data_combined_x <- subset(data_combined, formofway %in% c("Dual Carriageway", "Single Carriageway"))

colnames(data_combined_x)
plot(density(data_combined_x$link_adhrate))
plot(density(data_combined_x$link_speedingcount))

table(data_combined_x$speedLimit_group)
table(data_combined_x$routehierarchy_group)

unique(data_combined_x$directionality_title)
data_combined_x$both_direction <- ifelse(data_combined_x$directionality_title == "both directions", 1, 0)
unique(data_combined_x$both_direction)
table(data_combined_x$both_direction)

colnames(data_combined_x)

data_combined_x <- st_drop_geometry(data_combined_x)

unique(data_combined_x$speedLimit_group)
unique(data_combined_x$routehierarchy_group)

data_combined_x$speedLimit_group <- relevel(factor(data_combined_x$speedLimit_group), ref = "70")
data_combined_x$routehierarchy_group <- relevel(factor(data_combined_x$routehierarchy_group), ref = "A Road")


levels(data_combined_x$speedLimit_group)
levels(data_combined_x$routehierarchy_group)

unique(data_combined_x$speedLimit_group)
unique(data_combined_x$speedLimit_mph)

data_combined_x$speedLimit_group_new <- ifelse(data_combined_x$speedLimit_mph %in% c(5, 10, 15), 20, data_combined_x$speedLimit_mph)
unique(data_combined_x$speedLimit_group_new)

data_combined_x$speedLimit_group_new <- relevel(factor(data_combined_x$speedLimit_group_new), ref = "70")
levels(data_combined_x$speedLimit_group_new)
unique(data_combined_x$speedLimit_group_new)



colnames(data_combined_x)
sapply(data_combined_x, function(x) sum(is.na(x)))

plot(density(data_combined_x$island_counts_100m, na.rm = TRUE))
plot(density(data_combined_x$crossing_island_counts_100m))
cor(data_combined_x$island_counts_100m, data_combined_x$crossing_island_counts_100m, use = "complete.obs")


data_combined_x$traffic_island_100m <- rowSums(
  cbind(data_combined_x$island_counts_100m, data_combined_x$crossing_island_counts_100m),
  na.rm = TRUE
)
range(data_combined_x$traffic_island_100m)

data_combined_x$signals_crossing_counts_100m <- data_combined_x$traffic_signals_counts_100m

save(data_combined_x, file = "/Users/longpc/Documents/Leeds/code/readdata2.RData")


# new merge variable
colnames(data_combined_x)

data_combined_x$traffic_calming_100m <- rowSums(
  cbind(data_combined_x$hump_counts_100m, data_combined_x$bump_counts_100m, data_combined_x$table_counts_100m, data_combined_x$cushion_counts_100m),
  na.rm = TRUE
)
range(data_combined_x$traffic_calming_100m)

data_combined_x$roundabout_new_100m <- rowSums(
  cbind(data_combined_x$roundabout_counts_100m, data_combined_x$circular_counts_100m),
  na.rm = TRUE
)
range(data_combined_x$roundabout_new_100m)



# Count rows where 'averagewidth' is not NA for each city
count_result <- data_combined_x %>%
  filter(!is.na(averagewidth)) %>%
  group_by(city) %>%
  summarise(count = n())

# View the result
print(count_result)


# new 
data_combined_x_mph20 <- subset(data_combined_x, speedLimit_group_new == 20)
data_combined_x_mph30 <- subset(data_combined_x, speedLimit_group_new == 30)
data_combined_x_mph40 <- subset(data_combined_x, speedLimit_group_new == 40)
data_combined_x_mph50 <- subset(data_combined_x, speedLimit_group_new == 50)
data_combined_x_mph60 <- subset(data_combined_x, speedLimit_group_new == 60)
data_combined_x_mph70 <- subset(data_combined_x, speedLimit_group_new == 70)

sum(!is.na(data_combined_x_mph20$averagewidth))
sum(!is.na(data_combined_x_mph30$averagewidth))
sum(!is.na(data_combined_x_mph40$averagewidth))
sum(!is.na(data_combined_x_mph50$averagewidth))
sum(!is.na(data_combined_x_mph60$averagewidth))
sum(!is.na(data_combined_x_mph70$averagewidth))


#### new updated
library(openxlsx) 
library(sf)
library(dplyr)
library(lme4)
library(car)
library(glmmTMB)
library(sjPlot)
library(lmerTest)
library(effectsize)
library(ggplot2)
library(viridis)

data_combined_x$InvMHDWl200 <- 1 / data_combined_x$MHDWl200
data_combined_x$NegMHDWl200 <- - data_combined_x$MHDWl200

data_combined_x$InvMHDWl400 <- 1 / data_combined_x$MHDWl400
data_combined_x$NegMHDWl400 <- - data_combined_x$MHDWl400

data_combined_x$InvMHDWl800 <- 1 / data_combined_x$MHDWl800
data_combined_x$NegMHDWl800 <- - data_combined_x$MHDWl800

data_combined_x$InvMHDWl2000 <- 1 / data_combined_x$MHDWl2000
data_combined_x$NegMHDWl2000 <- - data_combined_x$MHDWl2000

data_combined_x$InvMHDWl5000 <- 1 / data_combined_x$MHDWl5000
data_combined_x$NegMHDWl5000 <- - data_combined_x$MHDWl5000

data_combined_x$InvMHDWl10000 <- 1 / data_combined_x$MHDWl10000
data_combined_x$NegMHDWl10000 <- - data_combined_x$MHDWl10000

unique(data_combined_x$speedLimit_group_new)

data_combined_x_mph20 <- subset(data_combined_x, speedLimit_group_new == 20)
data_combined_x_mph30 <- subset(data_combined_x, speedLimit_group_new == 30)
data_combined_x_mph40 <- subset(data_combined_x, speedLimit_group_new == 40)
data_combined_x_mph50 <- subset(data_combined_x, speedLimit_group_new == 50)
data_combined_x_mph60 <- subset(data_combined_x, speedLimit_group_new == 60)
data_combined_x_mph70 <- subset(data_combined_x, speedLimit_group_new == 70)

sum(!is.na(data_combined_x_mph20$averagewidth))
sum(!is.na(data_combined_x_mph30$averagewidth))
sum(!is.na(data_combined_x_mph40$averagewidth))
sum(!is.na(data_combined_x_mph50$averagewidth))
sum(!is.na(data_combined_x_mph60$averagewidth))
sum(!is.na(data_combined_x_mph70$averagewidth))

# test vif
#  + scale(NQPDHWl800) + scale(NQPDHWl2_2)   + scale(AngD5000)
# 400m
mod_adherence_all <- lmer(link_adhrate ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con400) + scale(InvMHDWl400) + scale(BtHWl400) + scale(MGLHWl400) + scale(DivHWl400) + scale(AngD400) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + speedLimit_group_new + (1 | city), data = data_combined_x)
vif(mod_adherence_all)

mod_adherence_all <- lmer(link_adhrate ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con400) + scale(InvMHDWl400) + scale(BtHWl400) + scale(MGLHWl400) + scale(DivHWl400) + scale(AngD400) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), data = data_combined_x_mph60)
vif(mod_adherence_all)

mod_adherence_all <- lmer(link_adhrate ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con400) + scale(InvMHDWl400) + scale(BtHWl400) + scale(MGLHWl400) + scale(DivHWl400) + scale(AngD400) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + (1 | city), data = data_combined_x_mph70)
vif(mod_adherence_all)

# data = data_combined_x_mph20
# data = data_combined_x_mph30
# data = data_combined_x_mph40
# data = data_combined_x_mph50
# data = data_combined_x_mph60
# data = data_combined_x_mph70


##  Final updated models
colnames(data_combined_x)

# 400m   + scale(AngD400)
mod_speeding_100m400m <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con400) + scale(InvMHDWl400) + scale(BtHWl400) + scale(MGLHWl400) + scale(DivHWl400) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + speedLimit_group_new + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod_speeding_100m400m)
sjPlot::tab_model(mod_speeding_100m400m)

mod_speeding_100m400m_mph20 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con400) + scale(InvMHDWl400) + scale(BtHWl400) + scale(MGLHWl400) + scale(DivHWl400) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph20)
summary(mod_speeding_100m400m_mph20)
sjPlot::tab_model(mod_speeding_100m400m_mph20)

mod_speeding_100m400m_mph30 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con400) + scale(InvMHDWl400) + scale(BtHWl400) + scale(MGLHWl400) + scale(DivHWl400) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph30)
summary(mod_speeding_100m400m_mph30)
sjPlot::tab_model(mod_speeding_100m400m_mph30)

mod_speeding_100m400m_mph40 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con400) + scale(InvMHDWl400) + scale(BtHWl400) + scale(MGLHWl400) + scale(DivHWl400) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph40)
summary(mod_speeding_100m400m_mph40)
sjPlot::tab_model(mod_speeding_100m400m_mph40)

mod_speeding_100m400m_mph50 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con400) + scale(InvMHDWl400) + scale(BtHWl400) + scale(MGLHWl400) + scale(DivHWl400) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph50)
summary(mod_speeding_100m400m_mph50)
sjPlot::tab_model(mod_speeding_100m400m_mph50)

# mod_speeding_100m400m_mph60 <- glmmTMB(
#   link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con400) + scale(InvMHDWl400) + scale(BtHWl400) + scale(MGLHWl400) + scale(DivHWl400) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph60)
# summary(mod_speeding_100m400m_mph60)
# sjPlot::tab_model(mod_speeding_100m400m_mph60)

mod_speeding_100m400m_mph60 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con400) + scale(InvMHDWl400) + scale(BtHWl400) + scale(MGLHWl400) + scale(DivHWl400) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control=glmmTMBControl(optimizer=optim, optArgs=list(method="L-BFGS-B")), data = data_combined_x_mph60)
summary(mod_speeding_100m400m_mph60)
sjPlot::tab_model(mod_speeding_100m400m_mph60)

mod_speeding_100m400m_mph70 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con400) + scale(InvMHDWl400) + scale(BtHWl400) + scale(MGLHWl400) + scale(DivHWl400) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph70)
summary(mod_speeding_100m400m_mph70)
sjPlot::tab_model(mod_speeding_100m400m_mph70)



# 800m   + scale(AngD800)
mod_speeding_100m800m <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con800) + scale(InvMHDWl800) + scale(BtHWl800) + scale(MGLHWl800) + scale(DivHWl800) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + speedLimit_group_new + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod_speeding_100m800m)
sjPlot::tab_model(mod_speeding_100m800m)

mod_speeding_100m800m_mph20 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con800) + scale(InvMHDWl800) + scale(BtHWl800) + scale(MGLHWl800) + scale(DivHWl800) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph20)
summary(mod_speeding_100m800m_mph20)
sjPlot::tab_model(mod_speeding_100m800m_mph20)

mod_speeding_100m800m_mph30 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con800) + scale(InvMHDWl800) + scale(BtHWl800) + scale(MGLHWl800) + scale(DivHWl800) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph30)
summary(mod_speeding_100m800m_mph30)
sjPlot::tab_model(mod_speeding_100m800m_mph30)

mod_speeding_100m800m_mph40 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con800) + scale(InvMHDWl800) + scale(BtHWl800) + scale(MGLHWl800) + scale(DivHWl800) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph40)
summary(mod_speeding_100m800m_mph40)
sjPlot::tab_model(mod_speeding_100m800m_mph40)

mod_speeding_100m800m_mph50 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con800) + scale(InvMHDWl800) + scale(BtHWl800) + scale(MGLHWl800) + scale(DivHWl800) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph50)
summary(mod_speeding_100m800m_mph50)
sjPlot::tab_model(mod_speeding_100m800m_mph50)

# mod_speeding_100m800m_mph60 <- glmmTMB(
#   link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con800) + scale(InvMHDWl800) + scale(BtHWl800) + scale(MGLHWl800) + scale(DivHWl800) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph60)
# summary(mod_speeding_100m800m_mph60)
# sjPlot::tab_model(mod_speeding_100m800m_mph60)

mod_speeding_100m800m_mph60 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con800) + scale(InvMHDWl800) + scale(BtHWl800) + scale(MGLHWl800) + scale(DivHWl800) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control=glmmTMBControl(optimizer=optim, optArgs=list(method="L-BFGS-B")), data = data_combined_x_mph60)
summary(mod_speeding_100m800m_mph60)
sjPlot::tab_model(mod_speeding_100m800m_mph60)

mod_speeding_100m800m_mph70 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con800) + scale(InvMHDWl800) + scale(BtHWl800) + scale(MGLHWl800) + scale(DivHWl800) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph70)
summary(mod_speeding_100m800m_mph70)
sjPlot::tab_model(mod_speeding_100m800m_mph70)


# 2km    + scale(AngD2000)
mod_speeding_100m2km <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con2000) + scale(InvMHDWl2000) + scale(BtHWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + speedLimit_group_new + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod_speeding_100m2km)
sjPlot::tab_model(mod_speeding_100m2km)
AIC(mod_speeding_100m2km)  
# nbinom2 is lower AIC > better;  ziformula = ~ 0 similar with 1

mod_speeding_100m2km_mph20 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con2000) + scale(InvMHDWl2000) + scale(BtHWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph20)
summary(mod_speeding_100m2km_mph20)
sjPlot::tab_model(mod_speeding_100m2km_mph20)

mod_speeding_100m2km_mph30 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con2000) + scale(InvMHDWl2000) + scale(BtHWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph30)
summary(mod_speeding_100m2km_mph30)
sjPlot::tab_model(mod_speeding_100m2km_mph30)

mod_speeding_100m2km_mph40 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con2000) + scale(InvMHDWl2000) + scale(BtHWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph40)
summary(mod_speeding_100m2km_mph40)
sjPlot::tab_model(mod_speeding_100m2km_mph40)

mod_speeding_100m2km_mph50 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con2000) + scale(InvMHDWl2000) + scale(BtHWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph50)
summary(mod_speeding_100m2km_mph50)
sjPlot::tab_model(mod_speeding_100m2km_mph50)

# mod_speeding_100m2km_mph60 <- glmmTMB(
#   link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con2000) + scale(InvMHDWl2000) + scale(BtHWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph60)
# summary(mod_speeding_100m2km_mph60)
# sjPlot::tab_model(mod_speeding_100m2km_mph60)

mod_speeding_100m2km_mph60 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con2000) + scale(InvMHDWl2000) + scale(BtHWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control=glmmTMBControl(optimizer=optim, optArgs=list(method="L-BFGS-B")), data = data_combined_x_mph60)
summary(mod_speeding_100m2km_mph60)
sjPlot::tab_model(mod_speeding_100m2km_mph60)

mod_speeding_100m2km_mph70 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con2000) + scale(InvMHDWl2000) + scale(BtHWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph70)
summary(mod_speeding_100m2km_mph70)
sjPlot::tab_model(mod_speeding_100m2km_mph70)


# 5km
mod_speeding_100m5km <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con5000) + scale(InvMHDWl5000) + scale(BtHWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + speedLimit_group_new + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod_speeding_100m5km)
sjPlot::tab_model(mod_speeding_100m5km)

mod_speeding_100m5km_mph20 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con5000) + scale(InvMHDWl5000) + scale(BtHWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph20)
summary(mod_speeding_100m5km_mph20)
sjPlot::tab_model(mod_speeding_100m5km_mph20)

mod_speeding_100m5km_mph30 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con5000) + scale(InvMHDWl5000) + scale(BtHWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph30)
summary(mod_speeding_100m5km_mph30)
sjPlot::tab_model(mod_speeding_100m5km_mph30)

mod_speeding_100m5km_mph40 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con5000) + scale(InvMHDWl5000) + scale(BtHWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph40)
summary(mod_speeding_100m5km_mph40)
sjPlot::tab_model(mod_speeding_100m5km_mph40)

mod_speeding_100m5km_mph50 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con5000) + scale(InvMHDWl5000) + scale(BtHWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph50)
summary(mod_speeding_100m5km_mph50)
sjPlot::tab_model(mod_speeding_100m5km_mph50)

# mod_speeding_100m5km_mph60 <- glmmTMB(
#   link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con5000) + scale(InvMHDWl5000) + scale(BtHWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph60)
# summary(mod_speeding_100m5km_mph60)
# sjPlot::tab_model(mod_speeding_100m5km_mph60)

mod_speeding_100m5km_mph60 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con5000) + scale(InvMHDWl5000) + scale(BtHWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control=glmmTMBControl(optimizer=optim, optArgs=list(method="L-BFGS-B")), data = data_combined_x_mph60)
summary(mod_speeding_100m5km_mph60)
sjPlot::tab_model(mod_speeding_100m5km_mph60)

mod_speeding_100m5km_mph70 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con5000) + scale(InvMHDWl5000) + scale(BtHWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph70)
summary(mod_speeding_100m5km_mph70)
sjPlot::tab_model(mod_speeding_100m5km_mph70)


# 10km
mod_speeding_100m10km <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con10000) + scale(InvMHDWl10000) + scale(BtHWl10000) + scale(MGLHWl1000) + scale(DivHWl1000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + speedLimit_group_new + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod_speeding_100m10km)
sjPlot::tab_model(mod_speeding_100m10km)

mod_speeding_100m10km_mph20 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con10000) + scale(InvMHDWl10000) + scale(BtHWl10000) + scale(MGLHWl1000) + scale(DivHWl1000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph20)
summary(mod_speeding_100m10km_mph20)
sjPlot::tab_model(mod_speeding_100m10km_mph20)

mod_speeding_100m10km_mph30 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con10000) + scale(InvMHDWl10000) + scale(BtHWl10000) + scale(MGLHWl1000) + scale(DivHWl1000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph30)
summary(mod_speeding_100m10km_mph30)
sjPlot::tab_model(mod_speeding_100m10km_mph30)

mod_speeding_100m10km_mph40 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con10000) + scale(InvMHDWl10000) + scale(BtHWl10000) + scale(MGLHWl1000) + scale(DivHWl1000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph40)
summary(mod_speeding_100m10km_mph40)
sjPlot::tab_model(mod_speeding_100m10km_mph40)

mod_speeding_100m10km_mph50 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con10000) + scale(InvMHDWl10000) + scale(BtHWl10000) + scale(MGLHWl1000) + scale(DivHWl1000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph50)
summary(mod_speeding_100m10km_mph50)
sjPlot::tab_model(mod_speeding_100m10km_mph50)

# mod_speeding_100m10km_mph60 <- glmmTMB(
#   link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con10000) + scale(InvMHDWl10000) + scale(BtHWl10000) + scale(MGLHWl1000) + scale(DivHWl1000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph60)
# summary(mod_speeding_100m10km_mph60)
# sjPlot::tab_model(mod_speeding_100m10km_mph60)

mod_speeding_100m10km_mph60 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con10000) + scale(InvMHDWl10000) + scale(BtHWl10000) + scale(MGLHWl1000) + scale(DivHWl1000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + scale(both_direction) + (1 | city), family = nbinom2, ziformula = ~ 0, control=glmmTMBControl(optimizer=optim, optArgs=list(method="L-BFGS-B")), data = data_combined_x_mph60)
summary(mod_speeding_100m10km_mph60)
sjPlot::tab_model(mod_speeding_100m10km_mph60)

mod_speeding_100m10km_mph70 <- glmmTMB(
  link_speedingcount ~ scale(traffic_calming_100m) + scale(choker_counts_100m) + scale(traffic_island_100m) + scale(signals_crossing_counts_100m) + scale(marked_counts_100m) + scale(uncontrolled_counts_100m) + scale(roundabout_new_100m) + scale(mini_roundabout_counts_100m) + scale(motorway_junction_counts_100m) + scale(signal_new_counts_100m) + scale(camera_new_counts_100m) + scale(Con10000) + scale(InvMHDWl10000) + scale(BtHWl10000) + scale(MGLHWl1000) + scale(DivHWl1000) + scale(LConn) + scale(LAC) + scale(LLen) + scale(averagewidth) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph70)
summary(mod_speeding_100m10km_mph70)
sjPlot::tab_model(mod_speeding_100m10km_mph70)










