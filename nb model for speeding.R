

#### new updated  causal analysis
library(openxlsx) 
library(sf)
library(dplyr)
library(lme4)
library(car)
library(Matrix)
library(glmmTMB)
library(TMB)
library(sjPlot)
library(lmerTest)
library(effectsize)
library(ggplot2)
library(viridis)


# # new updated
# colnames(data_combined_x)
# 
# plot(density(data_combined_x$link_adhrate))
# range(data_combined_x$link_adhrate)
# 
# data_combined_x$link_adherenceRate <- data_combined_x$link_adhrate / 100
# 
# data_combined_x$link_speedingRate <- 1 - data_combined_x$link_adherenceRate
# 
# plot(density(data_combined_x$link_speedingRate))
# range(data_combined_x$link_speedingRate)



# ### count certain variables
# colnames(data_combined_x)
# sapply(data_combined_x, function(x) sum(is.na(x)))
# 
# plot(density(data_combined_x$island_counts_50m, na.rm = TRUE))
# plot(density(data_combined_x$crossing_island_counts_50m))
# cor(data_combined_x$island_counts_50m, data_combined_x$crossing_island_counts_50m, use = "complete.obs")
# 
# 
# data_combined_x$traffic_island_50m <- rowSums(
#   cbind(data_combined_x$island_counts_50m, data_combined_x$crossing_island_counts_50m),
#   na.rm = TRUE
# )
# range(data_combined_x$traffic_island_50m)
# 
# data_combined_x$signals_crossing_counts_50m <- data_combined_x$traffic_signals_counts_50m
# 
# 
# # new merge variable
# colnames(data_combined_x)
# 
# data_combined_x$traffic_calming_50m <- rowSums(
#   cbind(data_combined_x$hump_counts_50m, data_combined_x$bump_counts_50m, data_combined_x$table_counts_50m, data_combined_x$cushion_counts_50m),
#   na.rm = TRUE
# )
# range(data_combined_x$traffic_calming_50m)
# 
# data_combined_x$roundabout_new_50m <- rowSums(
#   cbind(data_combined_x$roundabout_counts_50m, data_combined_x$circular_counts_50m),
#   na.rm = TRUE
# )
# range(data_combined_x$roundabout_new_50m)
# 
# 
# table(data_combined_x$traffic_calming_50m)
# table(data_combined_x$choker_counts_50m)      #  small observations
# table(data_combined_x$traffic_island_50m)
# table(data_combined_x$signals_crossing_counts_50m)
# table(data_combined_x$marked_counts_50m)
# table(data_combined_x$uncontrolled_counts_50m)
# table(data_combined_x$roundabout_new_50m)
# table(data_combined_x$mini_roundabout_counts_50m)
# table(data_combined_x$motorway_junction_counts_50m)
# table(data_combined_x$signal_new_counts_50m)
# table(data_combined_x$camera_new_counts_50m)   #  small observations
# table(data_combined_x$both_direction)
# 
# 
# 
# ### Treat certain variable as binary 0 or 1
# 
# data_combined_x$traffic_calming_50m01 <- ifelse(data_combined_x$traffic_calming_50m > 0, 1, 0)
# data_combined_x$choker_counts_50m01 <- ifelse(data_combined_x$choker_counts_50m > 0, 1, 0)
# data_combined_x$traffic_island_50m01 <- ifelse(data_combined_x$traffic_island_50m > 0, 1, 0)
# data_combined_x$signals_crossing_counts_50m01 <- ifelse(data_combined_x$signals_crossing_counts_50m > 0, 1, 0)
# data_combined_x$marked_counts_50m01 <- ifelse(data_combined_x$marked_counts_50m > 0, 1, 0)
# data_combined_x$uncontrolled_counts_50m01 <- ifelse(data_combined_x$uncontrolled_counts_50m > 0, 1, 0)
# data_combined_x$roundabout_new_50m01 <- ifelse(data_combined_x$roundabout_new_50m > 0, 1, 0)
# data_combined_x$mini_roundabout_counts_50m01 <- ifelse(data_combined_x$mini_roundabout_counts_50m > 0, 1, 0)
# data_combined_x$motorway_junction_counts_50m01 <- ifelse(data_combined_x$motorway_junction_counts_50m > 0, 1, 0)
# data_combined_x$signal_new_counts_50m01 <- ifelse(data_combined_x$signal_new_counts_50m > 0, 1, 0)
# data_combined_x$camera_new_counts_50m01 <- ifelse(data_combined_x$camera_new_counts_50m > 0, 1, 0)
# data_combined_x$both_direction01 <- ifelse(data_combined_x$both_direction > 0, 1, 0)
# 
# table(data_combined_x$traffic_calming_50m01)
# table(data_combined_x$choker_counts_50m01)      #  small observations
# table(data_combined_x$traffic_island_50m01)
# table(data_combined_x$signals_crossing_counts_50m01)
# table(data_combined_x$marked_counts_50m01)
# table(data_combined_x$uncontrolled_counts_50m01)
# table(data_combined_x$roundabout_new_50m01)
# table(data_combined_x$mini_roundabout_counts_50m01)
# table(data_combined_x$motorway_junction_counts_50m01)
# table(data_combined_x$signal_new_counts_50m01)
# table(data_combined_x$camera_new_counts_50m01)   #  small observations
# table(data_combined_x$both_direction01)
# 
# 
# colnames(data_combined_x)
# 
# data_combined_x_mph20 <- subset(data_combined_x, speedLimit_group_new == 20)
# data_combined_x_mph30 <- subset(data_combined_x, speedLimit_group_new == 30)
# data_combined_x_mph40 <- subset(data_combined_x, speedLimit_group_new == 40)
# data_combined_x_mph50 <- subset(data_combined_x, speedLimit_group_new == 50)
# data_combined_x_mph60 <- subset(data_combined_x, speedLimit_group_new == 60)
# data_combined_x_mph70 <- subset(data_combined_x, speedLimit_group_new == 70)




library(glmmTMB)
library(sjPlot)



# speeding events
# 2km 
mod01_speeding_50m2km <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + speedLimit_group_new + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod01_speeding_50m2km)
sjPlot::tab_model(mod01_speeding_50m2km)
AIC(mod01_speeding_50m2km)  
# nbinom2 is lower AIC, better;  ziformula = ~ 0, zero non-inflated 

mod01_speeding_50m2km_mph20 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph20)
summary(mod01_speeding_50m2km_mph20)
sjPlot::tab_model(mod01_speeding_50m2km_mph20)

mod01_speeding_50m2km_mph30 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph30)
summary(mod01_speeding_50m2km_mph30)
sjPlot::tab_model(mod01_speeding_50m2km_mph30)

mod01_speeding_50m2km_mph40 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph40)
summary(mod01_speeding_50m2km_mph40)
sjPlot::tab_model(mod01_speeding_50m2km_mph40)

mod01_speeding_50m2km_mph50 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph50)
summary(mod01_speeding_50m2km_mph50)
sjPlot::tab_model(mod01_speeding_50m2km_mph50)

mod01_speeding_50m2km_mph60 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph60)
summary(mod01_speeding_50m2km_mph60)
sjPlot::tab_model(mod01_speeding_50m2km_mph60)

mod01_speeding_50m2km_mph70 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph70)
summary(mod01_speeding_50m2km_mph70)
sjPlot::tab_model(mod01_speeding_50m2km_mph70)


# 400m
mod01_speeding_50m400m <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con400) + scale(BtHWl400) + scale(InvMHDWl400) + scale(MGLHWl400) + scale(DivHWl400) + speedLimit_group_new + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod01_speeding_50m400m)
sjPlot::tab_model(mod01_speeding_50m400m)

mod01_speeding_50m400m_mph20 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con400) + scale(BtHWl400) + scale(InvMHDWl400) + scale(MGLHWl400) + scale(DivHWl400) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph20)
summary(mod01_speeding_50m400m_mph20)
sjPlot::tab_model(mod01_speeding_50m400m_mph20)

mod01_speeding_50m400m_mph30 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con400) + scale(BtHWl400) + scale(InvMHDWl400) + scale(MGLHWl400) + scale(DivHWl400) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph30)
summary(mod01_speeding_50m400m_mph30)
sjPlot::tab_model(mod01_speeding_50m400m_mph30)

mod01_speeding_50m400m_mph40 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con400) + scale(BtHWl400) + scale(InvMHDWl400) + scale(MGLHWl400) + scale(DivHWl400) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph40)
summary(mod01_speeding_50m400m_mph40)
sjPlot::tab_model(mod01_speeding_50m400m_mph40)

mod01_speeding_50m400m_mph50 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con400) + scale(BtHWl400) + scale(InvMHDWl400) + scale(MGLHWl400) + scale(DivHWl400) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph50)
summary(mod01_speeding_50m400m_mph50)
sjPlot::tab_model(mod01_speeding_50m400m_mph50)

mod01_speeding_50m400m_mph60 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con400) + scale(BtHWl400) + scale(InvMHDWl400) + scale(MGLHWl400) + scale(DivHWl400) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph60)
summary(mod01_speeding_50m400m_mph60)
sjPlot::tab_model(mod01_speeding_50m400m_mph60)


mod01_speeding_50m400m_mph70 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con400) + scale(BtHWl400) + scale(InvMHDWl400) + scale(MGLHWl400) + scale(DivHWl400) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph70)
summary(mod01_speeding_50m400m_mph70)
sjPlot::tab_model(mod01_speeding_50m400m_mph70)


# 800m
mod01_speeding_50m800m <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con800) + scale(BtHWl800) + scale(InvMHDWl800) + scale(MGLHWl800) + scale(DivHWl800) + speedLimit_group_new + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod01_speeding_50m800m)
sjPlot::tab_model(mod01_speeding_50m800m)

mod01_speeding_50m800m_mph20 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con800) + scale(BtHWl800) + scale(InvMHDWl800) + scale(MGLHWl800) + scale(DivHWl800) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph20)
summary(mod01_speeding_50m800m_mph20)
sjPlot::tab_model(mod01_speeding_50m800m_mph20)

mod01_speeding_50m800m_mph30 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con800) + scale(BtHWl800) + scale(InvMHDWl800) + scale(MGLHWl800) + scale(DivHWl800) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph30)
summary(mod01_speeding_50m800m_mph30)
sjPlot::tab_model(mod01_speeding_50m800m_mph30)

mod01_speeding_50m800m_mph40 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con800) + scale(BtHWl800) + scale(InvMHDWl800) + scale(MGLHWl800) + scale(DivHWl800) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph40)
summary(mod01_speeding_50m800m_mph40)
sjPlot::tab_model(mod01_speeding_50m800m_mph40)

mod01_speeding_50m800m_mph50 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con800) + scale(BtHWl800) + scale(InvMHDWl800) + scale(MGLHWl800) + scale(DivHWl800) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph50)
summary(mod01_speeding_50m800m_mph50)
sjPlot::tab_model(mod01_speeding_50m800m_mph50)

mod01_speeding_50m800m_mph60 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con800) + scale(BtHWl800) + scale(InvMHDWl800) + scale(MGLHWl800) + scale(DivHWl800) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph60)
summary(mod01_speeding_50m800m_mph60)
sjPlot::tab_model(mod01_speeding_50m800m_mph60)

mod01_speeding_50m800m_mph70 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con800) + scale(BtHWl800) + scale(InvMHDWl800) + scale(MGLHWl800) + scale(DivHWl800) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph70)
summary(mod01_speeding_50m800m_mph70)
sjPlot::tab_model(mod01_speeding_50m800m_mph70)



# 5km
mod01_speeding_50m5km <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con5000) + scale(BtHWl5000) + scale(InvMHDWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + speedLimit_group_new + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod01_speeding_50m5km)
sjPlot::tab_model(mod01_speeding_50m5km)

mod01_speeding_50m5km_mph20 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con5000) + scale(BtHWl5000) + scale(InvMHDWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph20)
summary(mod01_speeding_50m5km_mph20)
sjPlot::tab_model(mod01_speeding_50m5km_mph20)

mod01_speeding_50m5km_mph30 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con5000) + scale(BtHWl5000) + scale(InvMHDWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph30)
summary(mod01_speeding_50m5km_mph30)
sjPlot::tab_model(mod01_speeding_50m5km_mph30)

mod01_speeding_50m5km_mph40 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con5000) + scale(BtHWl5000) + scale(InvMHDWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph40)
summary(mod01_speeding_50m5km_mph40)
sjPlot::tab_model(mod01_speeding_50m5km_mph40)

mod01_speeding_50m5km_mph50 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con5000) + scale(BtHWl5000) + scale(InvMHDWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph50)
summary(mod01_speeding_50m5km_mph50)
sjPlot::tab_model(mod01_speeding_50m5km_mph50)

mod01_speeding_50m5km_mph60 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con5000) + scale(BtHWl5000) + scale(InvMHDWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph60)
summary(mod01_speeding_50m5km_mph60)
sjPlot::tab_model(mod01_speeding_50m5km_mph60)

mod01_speeding_50m5km_mph70 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con5000) + scale(BtHWl5000) + scale(InvMHDWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph70)
summary(mod01_speeding_50m5km_mph70)
sjPlot::tab_model(mod01_speeding_50m5km_mph70)




# 10km
mod01_speeding_50m10km <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con10000) + scale(BtHWl10000) + scale(InvMHDWl10000) + scale(MGLHWl1000) + scale(DivHWl1000) + speedLimit_group_new + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod01_speeding_50m10km)
sjPlot::tab_model(mod01_speeding_50m10km)

mod01_speeding_50m10km_mph20 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con10000) + scale(BtHWl10000) + scale(InvMHDWl10000) + scale(MGLHWl1000) + scale(DivHWl1000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph20)
summary(mod01_speeding_50m10km_mph20)
sjPlot::tab_model(mod01_speeding_50m10km_mph20)

mod01_speeding_50m10km_mph30 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con10000) + scale(BtHWl10000) + scale(InvMHDWl10000) + scale(MGLHWl1000) + scale(DivHWl1000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph30)
summary(mod01_speeding_50m10km_mph30)
sjPlot::tab_model(mod01_speeding_50m10km_mph30)

mod01_speeding_50m10km_mph40 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con10000) + scale(BtHWl10000) + scale(InvMHDWl10000) + scale(MGLHWl1000) + scale(DivHWl1000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph40)
summary(mod01_speeding_50m10km_mph40)
sjPlot::tab_model(mod01_speeding_50m10km_mph40)

mod01_speeding_50m10km_mph50 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con10000) + scale(BtHWl10000) + scale(InvMHDWl10000) + scale(MGLHWl1000) + scale(DivHWl1000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph50)
summary(mod01_speeding_50m10km_mph50)
sjPlot::tab_model(mod01_speeding_50m10km_mph50)

mod01_speeding_50m10km_mph60 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con10000) + scale(BtHWl10000) + scale(InvMHDWl10000) + scale(MGLHWl1000) + scale(DivHWl1000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph60)
summary(mod01_speeding_50m10km_mph60)
sjPlot::tab_model(mod01_speeding_50m10km_mph60)

mod01_speeding_50m10km_mph70 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con10000) + scale(BtHWl10000) + scale(InvMHDWl10000) + scale(MGLHWl1000) + scale(DivHWl1000) + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph70)
summary(mod01_speeding_50m10km_mph70)
sjPlot::tab_model(mod01_speeding_50m10km_mph70)









# new test with offset of  traffic volume
library(glmmTMB)
library(sjPlot)

colnames(data_combined_x)

# speeding events, offset traffic volume
# 2km 
mod01_speeding_50m2km <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + speedLimit_group_new + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod01_speeding_50m2km)
sjPlot::tab_model(mod01_speeding_50m2km)
AIC(mod01_speeding_50m2km)  
# nbinom2 is lower AIC, better;  ziformula = ~ 0, zero non-inflated 

mod01_speeding_50m2km_mph20 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph20)
summary(mod01_speeding_50m2km_mph20)
sjPlot::tab_model(mod01_speeding_50m2km_mph20)

mod01_speeding_50m2km_mph30 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph30)
summary(mod01_speeding_50m2km_mph30)
sjPlot::tab_model(mod01_speeding_50m2km_mph30)

mod01_speeding_50m2km_mph40 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph40)
summary(mod01_speeding_50m2km_mph40)
sjPlot::tab_model(mod01_speeding_50m2km_mph40)

mod01_speeding_50m2km_mph50 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph50)
summary(mod01_speeding_50m2km_mph50)
sjPlot::tab_model(mod01_speeding_50m2km_mph50)

mod01_speeding_50m2km_mph60 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph60)
summary(mod01_speeding_50m2km_mph60)
sjPlot::tab_model(mod01_speeding_50m2km_mph60)

mod01_speeding_50m2km_mph70 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph70)
summary(mod01_speeding_50m2km_mph70)
sjPlot::tab_model(mod01_speeding_50m2km_mph70)


# 400m
mod01_speeding_50m400m <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con400) + scale(BtHWl400) + scale(InvMHDWl400) + scale(MGLHWl400) + scale(DivHWl400) + speedLimit_group_new + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod01_speeding_50m400m)
sjPlot::tab_model(mod01_speeding_50m400m)

mod01_speeding_50m400m_mph20 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con400) + scale(BtHWl400) + scale(InvMHDWl400) + scale(MGLHWl400) + scale(DivHWl400) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph20)
summary(mod01_speeding_50m400m_mph20)
sjPlot::tab_model(mod01_speeding_50m400m_mph20)

mod01_speeding_50m400m_mph30 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con400) + scale(BtHWl400) + scale(InvMHDWl400) + scale(MGLHWl400) + scale(DivHWl400) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph30)
summary(mod01_speeding_50m400m_mph30)
sjPlot::tab_model(mod01_speeding_50m400m_mph30)

mod01_speeding_50m400m_mph40 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con400) + scale(BtHWl400) + scale(InvMHDWl400) + scale(MGLHWl400) + scale(DivHWl400) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph40)
summary(mod01_speeding_50m400m_mph40)
sjPlot::tab_model(mod01_speeding_50m400m_mph40)

mod01_speeding_50m400m_mph50 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con400) + scale(BtHWl400) + scale(InvMHDWl400) + scale(MGLHWl400) + scale(DivHWl400) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph50)
summary(mod01_speeding_50m400m_mph50)
sjPlot::tab_model(mod01_speeding_50m400m_mph50)

mod01_speeding_50m400m_mph60 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con400) + scale(BtHWl400) + scale(InvMHDWl400) + scale(MGLHWl400) + scale(DivHWl400) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph60)
summary(mod01_speeding_50m400m_mph60)
sjPlot::tab_model(mod01_speeding_50m400m_mph60)


mod01_speeding_50m400m_mph70 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con400) + scale(BtHWl400) + scale(InvMHDWl400) + scale(MGLHWl400) + scale(DivHWl400) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph70)
summary(mod01_speeding_50m400m_mph70)
sjPlot::tab_model(mod01_speeding_50m400m_mph70)


# 800m
mod01_speeding_50m800m <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con800) + scale(BtHWl800) + scale(InvMHDWl800) + scale(MGLHWl800) + scale(DivHWl800) + speedLimit_group_new + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod01_speeding_50m800m)
sjPlot::tab_model(mod01_speeding_50m800m)

mod01_speeding_50m800m_mph20 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con800) + scale(BtHWl800) + scale(InvMHDWl800) + scale(MGLHWl800) + scale(DivHWl800) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph20)
summary(mod01_speeding_50m800m_mph20)
sjPlot::tab_model(mod01_speeding_50m800m_mph20)

mod01_speeding_50m800m_mph30 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con800) + scale(BtHWl800) + scale(InvMHDWl800) + scale(MGLHWl800) + scale(DivHWl800) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph30)
summary(mod01_speeding_50m800m_mph30)
sjPlot::tab_model(mod01_speeding_50m800m_mph30)

mod01_speeding_50m800m_mph40 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con800) + scale(BtHWl800) + scale(InvMHDWl800) + scale(MGLHWl800) + scale(DivHWl800) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph40)
summary(mod01_speeding_50m800m_mph40)
sjPlot::tab_model(mod01_speeding_50m800m_mph40)

mod01_speeding_50m800m_mph50 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con800) + scale(BtHWl800) + scale(InvMHDWl800) + scale(MGLHWl800) + scale(DivHWl800) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph50)
summary(mod01_speeding_50m800m_mph50)
sjPlot::tab_model(mod01_speeding_50m800m_mph50)

mod01_speeding_50m800m_mph60 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con800) + scale(BtHWl800) + scale(InvMHDWl800) + scale(MGLHWl800) + scale(DivHWl800) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph60)
summary(mod01_speeding_50m800m_mph60)
sjPlot::tab_model(mod01_speeding_50m800m_mph60)

mod01_speeding_50m800m_mph70 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con800) + scale(BtHWl800) + scale(InvMHDWl800) + scale(MGLHWl800) + scale(DivHWl800) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph70)
summary(mod01_speeding_50m800m_mph70)
sjPlot::tab_model(mod01_speeding_50m800m_mph70)



# 5km
mod01_speeding_50m5km <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con5000) + scale(BtHWl5000) + scale(InvMHDWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + speedLimit_group_new + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod01_speeding_50m5km)
sjPlot::tab_model(mod01_speeding_50m5km)

mod01_speeding_50m5km_mph20 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con5000) + scale(BtHWl5000) + scale(InvMHDWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph20)
summary(mod01_speeding_50m5km_mph20)
sjPlot::tab_model(mod01_speeding_50m5km_mph20)

mod01_speeding_50m5km_mph30 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con5000) + scale(BtHWl5000) + scale(InvMHDWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph30)
summary(mod01_speeding_50m5km_mph30)
sjPlot::tab_model(mod01_speeding_50m5km_mph30)

mod01_speeding_50m5km_mph40 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con5000) + scale(BtHWl5000) + scale(InvMHDWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph40)
summary(mod01_speeding_50m5km_mph40)
sjPlot::tab_model(mod01_speeding_50m5km_mph40)

mod01_speeding_50m5km_mph50 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con5000) + scale(BtHWl5000) + scale(InvMHDWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph50)
summary(mod01_speeding_50m5km_mph50)
sjPlot::tab_model(mod01_speeding_50m5km_mph50)

mod01_speeding_50m5km_mph60 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con5000) + scale(BtHWl5000) + scale(InvMHDWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph60)
summary(mod01_speeding_50m5km_mph60)
sjPlot::tab_model(mod01_speeding_50m5km_mph60)

mod01_speeding_50m5km_mph70 <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con5000) + scale(BtHWl5000) + scale(InvMHDWl5000) + scale(MGLHWl5000) + scale(DivHWl5000) + (1 | city), offset = log(ptcount), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x_mph70)
summary(mod01_speeding_50m5km_mph70)
sjPlot::tab_model(mod01_speeding_50m5km_mph70)




