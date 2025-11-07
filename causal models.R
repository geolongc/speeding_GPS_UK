# cross-sectional speeding event model

mod01_speeding_50m2km <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + speedLimit_group_new + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod01_speeding_50m2km)
sjPlot::tab_model(mod01_speeding_50m2km)



data_combined_x <- data_combined_x %>%
  mutate(
    speed_limit_factor = case_when(
      speedLimit_group_new == 20 ~ "mph20",
      speedLimit_group_new == 30 ~ "mph30",
      speedLimit_group_new == 40 ~ "mph40",
      speedLimit_group_new == 50 ~ "mph50",
      speedLimit_group_new == 60 ~ "mph60",
      speedLimit_group_new == 70 ~ "mph70",
      TRUE ~ NA_character_
    ),
    speed_limit_factor = factor(speed_limit_factor, levels = c("mph70", "mph60", "mph50", "mph40", "mph30", "mph20")) # optional: relevel to mph70 as baseline
  )



# causal inference for binary variables, PSM
# 50m
# ════════════════════════════════════════════════════════════════
# 0  Libraries
# ════════════════════════════════════════════════════════════════
library(MatchIt)
library(cobalt)
library(WeightIt)
library(glmmTMB)
library(dplyr)
library(ggplot2)


# ════════════════════════════════════════════════════════════════
# 1  Settings (change only treat_var if you reuse the script)
# ════════════════════════════════════════════════════════════════

# set treatment variable
treat_var   <- "traffic_calming_50m01"        # <-- REPLACE for other features
treat_var   <- "choker_counts_50m01"
treat_var   <- "traffic_island_50m01"
treat_var   <- "signals_crossing_counts_50m01"
treat_var   <- "marked_counts_50m01"
treat_var   <- "uncontrolled_counts_50m01"
treat_var   <- "roundabout_new_50m01"
treat_var   <- "mini_roundabout_counts_50m01"
treat_var   <- "motorway_junction_counts_50m01"
treat_var   <- "signal_new_counts_50m01"
treat_var   <- "camera_new_counts_50m01"
treat_var   <- "both_direction01"

# covariates
# continuous vars
raw_cont   <- c("averagewidth","LLen","LAC","LConn",
                "Con400","BtHWl400","InvMHDWl400",
                "MGLHWl400","DivHWl400")

raw_cont   <- c("averagewidth","LLen","LAC","LConn",
                "Con800","BtHWl800","InvMHDWl800",
                "MGLHWl800","DivHWl800")

raw_cont   <- c("averagewidth","LLen","LAC","LConn",
                "Con2000","BtHWl2000","InvMHDWl2000",
                "MGLHWl2000","DivHWl2000")

raw_cont   <- c("averagewidth","LLen","LAC","LConn",
                "Con5000","BtHWl5000","InvMHDWl5000",
                "MGLHWl5000","DivHWl5000")


# binary vars
# 50m
binary_cov <- c("traffic_calming_50m01","choker_counts_50m01",
                "traffic_island_50m01","signals_crossing_counts_50m01",
                "marked_counts_50m01","uncontrolled_counts_50m01",
                "roundabout_new_50m01","mini_roundabout_counts_50m01",
                "motorway_junction_counts_50m01","signal_new_counts_50m01",
                "camera_new_counts_50m01","both_direction01")


# binary covars
binary_cov <- setdiff(binary_cov, treat_var)   # drop the treatment


# outcome variable, speeding count
outcome_var <- "link_speedingcount"


# ════════════════════════════════════════════════════════════════
# 2  Data prep
# ════════════════════════════════════════════════════════════════

df <- data_combined_x |>
  select(all_of(c(treat_var, outcome_var, "speed_limit_factor",
                  binary_cov, raw_cont))) |>
  na.omit()


# subset data
df <- data_combined_x_mph |>
  select(all_of(c(treat_var, outcome_var,
                  binary_cov, raw_cont))) |>
  na.omit()


# scale data
scaled <- paste0(raw_cont, "_z")
df[scaled] <- scale(df[raw_cont])

covars <- c(binary_cov, scaled, "speed_limit_factor") # fix "speed limit"

df$speed_limit_factor <- relevel(factor(df$speed_limit_factor), ref = "mph70")


cat("N =", nrow(df),
    "| treated prevalence =", round(mean(df[[treat_var]]), 3), "\n")


# ════════════════════════════════════════════════════════════════
# 3  MatchIt PSM (nearest, 1:1, caliper 0.20 SD)
# ════════════════════════════════════════════════════════════════
ps_form <- reformulate(covars, response = treat_var)
ps_form

m.out <- matchit(ps_form, data = df,
                 method   = "nearest",
                 distance = "glm",
                 estimand = "ATT",
                 caliper  = 0.20, 
                 std.caliper = TRUE,
                 ratio = 1)


# ── Balance check
bal <- bal.tab(m.out, m.threshold = .10, un = TRUE)
print(bal)

# Extract and sort balance table
imbal <- bal$Balance
imbal$abs_std_diff <- abs(imbal$Diff.Adj)
imbal_sorted <- imbal[order(-imbal$abs_std_diff), ]

# # Print top 5 imbalanced covariates
# print(head(imbal_sorted, 5)[, c("Diff.Adj", "abs_std_diff")], digits = 3)

# Stop if imbalance exceeds threshold
if (any(imbal$abs_std_diff > 0.10, na.rm = TRUE)) {
  stop("Balance > 0.10, revise matching.")
}


love.plot(
  m.out,
  stats     = "mean.diffs",
  abs       = TRUE,
  threshold = 0.10,
  var.order = "unadjusted",
  stars     = "std"          # <- show only standardized MDs
)


# ════════════════════════════════════════════════════════════════
# 4  Matched outcome NB-GLMM
# ════════════════════════════════════════════════════════════════

mdata <- match.data(m.out)
nrow(mdata)


# For ATT (after matching, or ATT-weighted sample)
E_Y0 <- mean(mdata[[outcome_var]][mdata[[treat_var]] == 0])
round(E_Y0, 3)

E_Y1 <- mean(mdata[[outcome_var]][mdata[[treat_var]] == 1])
round(E_Y1, 3)

ATT <- E_Y1 - E_Y0
cat("ATT (difference):", round(ATT, 3), "\n")


# sensitive test
# ════════════════════════════════════════════════════════════════
# 5  Caliper-sweep sensitivity (0.10–0.40)
# ════════════════════════════════════════════════════════════════

calipers <- seq(0.10, 0.40, by = 0.10)

sens_list <- lapply(calipers, function(cal) {
  
  # 5-A: Matching
  m <- matchit(
    formula = ps_form,
    data = df,
    method = "nearest",
    distance = "glm",
    caliper = cal,
    std.caliper = TRUE
  )
  
  d <- match.data(m)
  if (nrow(d) < 100) {
    cat("Caliper", cal, "→ too few matched rows (", nrow(d), "), skipped.\n")
    return(NULL)
  }
  
  # 5-B: Compute max SMD safely
  smd_vec <- bal.tab(m)$Balance$Diff.Adj
  max_smd <- suppressWarnings(max(abs(smd_vec), na.rm = TRUE))
  if (is.infinite(max_smd) || is.nan(max_smd)) max_smd <- NA_real_
  
  cat("Caliper =", cal, "| N =", nrow(d), "| Max |SMD| =", round(max_smd, 3), "\n")
  
  # 5-C: Return as data frame
  data.frame(
    Caliper = cal,
    N = nrow(d),
    MaxSMD = round(max_smd, 3)
  )
})

# 5-E: Combine non-null results
sens <- bind_rows(Filter(Negate(is.null), sens_list))

# 5-F: Show result
print(sens, digits = 3)






# causal model for continuous variables, GPS
# speeding event model

mod01_speeding_50m2km <- glmmTMB(
  link_speedingcount ~ traffic_calming_50m01 + choker_counts_50m01 + traffic_island_50m01 + signals_crossing_counts_50m01 + marked_counts_50m01 + uncontrolled_counts_50m01 + roundabout_new_50m01 + mini_roundabout_counts_50m01 + motorway_junction_counts_50m01 + signal_new_counts_50m01 + camera_new_counts_50m01 + both_direction01 + scale(averagewidth) + scale(LLen) + scale(LAC) + scale(LConn) + scale(Con2000) + scale(BtHWl2000) + scale(InvMHDWl2000) + scale(MGLHWl2000) + scale(DivHWl2000) + speedLimit_group_new + (1 | city), family = nbinom2, ziformula = ~ 0, control = glmmTMBControl(optCtrl = list(iter.max = 10000, eval.max = 10000)), data = data_combined_x)
summary(mod01_speeding_50m2km)
sjPlot::tab_model(mod01_speeding_50m2km)



# 50m
# ════════════════════════════════════════════════════════════════
# 0  Packages & helpers
# ════════════════════════════════════════════════════════════════
library(CausalGPS)   #   kernel-GPS  + SuperLearner
library(SuperLearner)
library(glmmTMB)     #   weighted NB-GLMM
library(data.table)  #   fast dplyr verbs
library(dplyr)
library(rlang)       # for `sym()`


data_combined_x <- data_combined_x %>%
  mutate(
    speed_limit_factor = case_when(
      speedLimit_group_new == 20 ~ "mph20",
      speedLimit_group_new == 30 ~ "mph30",
      speedLimit_group_new == 40 ~ "mph40",
      speedLimit_group_new == 50 ~ "mph50",
      speedLimit_group_new == 60 ~ "mph60",
      speedLimit_group_new == 70 ~ "mph70",
      TRUE ~ NA_character_
    ),
    speed_limit_factor = factor(speed_limit_factor, levels = c("mph70", "mph60", "mph50", "mph40", "mph30", "mph20")) # optional: relevel to mph70 as baseline
  )


get_ess <- function(w) (sum(w)^2) / sum(w^2)


# ════════════════════════════════════════════════════════════════
# 1  Settings  –––  change just these two lines for a new analysis
# ════════════════════════════════════════════════════════════════

# set the treatment variable

treat_var   <- "averagewidth"
treat_var   <- "LLen"
treat_var   <- "LAC"
treat_var   <- "LConn"
treat_var   <- "Con400"
treat_var   <- "BtHWl400"
treat_var   <- "InvMHDWl400"
treat_var   <- "MGLHWl400"
treat_var   <- "DivHWl400"

# treat_var   <- "averagewidth"
# treat_var   <- "LLen"
# treat_var   <- "LAC"
# treat_var   <- "LConn"
# treat_var   <- "Con800"
# treat_var   <- "BtHWl800"
# treat_var   <- "InvMHDWl800"
# treat_var   <- "MGLHWl800"
# treat_var   <- "DivHWl800"

# treat_var   <- "averagewidth"
# treat_var   <- "LLen"
# treat_var   <- "LAC" 
# treat_var   <- "LConn"
# treat_var   <- "Con2000" 
# treat_var   <- "BtHWl2000"
# treat_var   <- "InvMHDWl2000"  
# treat_var   <- "MGLHWl2000"  
# treat_var   <- "DivHWl2000"

# treat_var   <- "averagewidth"
# treat_var   <- "LLen"
# treat_var   <- "LAC" 
# treat_var   <- "LConn"
# treat_var   <- "Con5000"      
# treat_var   <- "BtHWl5000"
# treat_var   <- "InvMHDWl5000"  
# treat_var   <- "MGLHWl5000"  
# treat_var   <- "DivHWl5000"  


# fixed covariate lists (edit only if your data changes)
# continuous variables

cont_cov <- c("averagewidth","LLen","LAC","LConn","Con400",
              "InvMHDWl400","BtHWl400","MGLHWl400","DivHWl400")

cont_cov <- c("averagewidth","LLen","LAC","LConn","Con800",
              "InvMHDWl800","BtHWl800","MGLHWl800","DivHWl800")

cont_cov <- c("averagewidth","LLen","LAC","LConn","Con2000",
              "InvMHDWl2000","BtHWl2000","MGLHWl2000","DivHWl2000")

cont_cov <- c("averagewidth","LLen","LAC","LConn","Con5000",
              "InvMHDWl5000","BtHWl5000","MGLHWl5000","DivHWl5000")


# ── drop the *current* treatment so it isn’t in the covariate set
cont_cov_nomix <- setdiff(cont_cov, treat_var)

# binary variables
bin_cov <- c("traffic_calming_50m01","choker_counts_50m01",
             "traffic_island_50m01","signals_crossing_counts_50m01",
             "marked_counts_50m01","uncontrolled_counts_50m01",
             "roundabout_new_50m01","mini_roundabout_counts_50m01",
             "motorway_junction_counts_50m01","signal_new_counts_50m01",
             "camera_new_counts_50m01","both_direction01")


# outcome variable
outcome_var <- "link_speedingcount"   # outcome, speeding event count


# ════════════════════════════════════════════════════════════════
# 2  Clean data  (scale treatment & continuous covariates)
# ════════════════════════════════════════════════════════════════

gps_df_raw <- data_combined_x %>%
  select(all_of(c(outcome_var, treat_var, "speed_limit_factor",
                  bin_cov, cont_cov_nomix))) %>%
  na.omit() %>%
  mutate(
    id = row_number(),
    speed_limit_factor = relevel(factor(speed_limit_factor), ref = "mph70"),
  )

cat("N before trimming =", nrow(gps_df_raw), "\n")


# Trim treat variable before scale
gps_df_trimmed <- trim_it(
  data_obj       = gps_df_raw,
  trim_quantiles = c(0.05, 0.95),
  variable       = treat_var
)

cat("N after trimming =", nrow(gps_df_trimmed), "\n")


gps_df_trimmed <- gps_df_trimmed %>%
  mutate(
    treat = scale(.data[[treat_var]])[,1],
    across(all_of(cont_cov_nomix), ~ scale(.)[,1], .names = "{.col}_z")
  ) %>%
  select(id,
         treat,
         all_of(bin_cov),
         all_of(paste0(cont_cov_nomix, "_z")),
         speed_limit_factor,
         outcome = !!sym(outcome_var))


# final covariate list
covars <- c(bin_cov, paste0(cont_cov_nomix, "_z"), "speed_limit_factor")
covars


# Output check
str(gps_df_trimmed)
colnames(gps_df_trimmed)
cat("Final N =", nrow(gps_df_trimmed), "\n")


# ════════════════════════════════════════════════════════════════
# 3  Estimate generalized propensity score
# ════════════════════════════════════════════════════════════════

# set the treatment variable

treat_var   <- "averagewidth"
treat_var   <- "LLen"
treat_var   <- "LAC"
treat_var   <- "LConn"
treat_var   <- "Con400"
treat_var   <- "BtHWl400"
treat_var   <- "InvMHDWl400"
treat_var   <- "MGLHWl400"
treat_var   <- "DivHWl400"

# treat_var   <- "averagewidth"
# treat_var   <- "LLen"
# treat_var   <- "LAC"
# treat_var   <- "LConn"
# treat_var   <- "Con800"
# treat_var   <- "BtHWl800"
# treat_var   <- "InvMHDWl800"
# treat_var   <- "MGLHWl800"
# treat_var   <- "DivHWl800"

# treat_var   <- "averagewidth"
# treat_var   <- "LLen"
# treat_var   <- "LAC" 
# treat_var   <- "LConn"
# treat_var   <- "Con2000" 
# treat_var   <- "BtHWl2000"
# treat_var   <- "InvMHDWl2000"  
# treat_var   <- "MGLHWl2000"  
# treat_var   <- "DivHWl2000"

# treat_var   <- "averagewidth"
# treat_var   <- "LLen"
# treat_var   <- "LAC"
# treat_var   <- "LConn"
# treat_var   <- "Con5000"
# treat_var   <- "BtHWl5000"
# treat_var   <- "InvMHDWl5000"
# treat_var   <- "MGLHWl5000"
# treat_var   <- "DivHWl5000"

# normal
set.seed(123)
gps_obj_normal <- estimate_gps(
  .data       = gps_df_trimmed,
  .formula    = reformulate(covars, response = "treat"),
  gps_density = "normal",
  sl_lib      = "SL.xgboost"         # flexible learner
)

plot(gps_obj_normal)
nrow(gps_obj_normal$.data)


# Trim the gps_obj_normal using trim_it(), for certain marginal balance vars
gps_obj_normal_trimmed <- trim_it(
  data_obj = gps_obj_normal,
  trim_quantiles = c(0.01, 0.99),   # trims bottom 1% and top 1% of the treatment
  variable = "gps"                # gps value
)

nrow(gps_obj_normal$.data)
nrow(gps_obj_normal_trimmed$.data)
plot(gps_obj_normal_trimmed)


# Trim the gps_obj_normal using trim_it(), for certain marginal balance vars
gps_obj_normal_trimmed <- trim_it(
  data_obj = gps_obj_normal,
  trim_quantiles = c(0.005, 0.995),   # trims bottom 1% and top 1% of the treatment
  variable = "gps"                # gps value
)

nrow(gps_obj_normal$.data)
nrow(gps_obj_normal_trimmed$.data)
plot(gps_obj_normal_trimmed)


# Trim the gps_obj_normal using trim_it(), for certain marginal balance vars
gps_obj_normal_trimmed <- trim_it(
  data_obj = gps_obj_normal,
  trim_quantiles = c(0.001, 0.999),   # trims bottom 1% and top 1% of the treatment
  variable = "gps"                # gps value
)

nrow(gps_obj_normal$.data)
nrow(gps_obj_normal_trimmed$.data)
plot(gps_obj_normal_trimmed)


# ═════════════════════════════════════════
# 4  Compute counter-weights 
# ═════════════════════════════════════════

# weight, normal
# using trimmed gps object
cw_weight_trimmed <- compute_counter_weight(
  gps_obj_normal_trimmed,
  ci_appr = "weighting",
  nthread = 4,
  delta_n = 0.10,
  dist_measure = "l1",
  scale = 0.5)

range(cw_weight_trimmed$.data$counter_weight)
table(cw_weight_trimmed$.data$counter_weight > 0)  # TRUE = matched
cat("Overall ESS =", round(get_ess(cw_weight_trimmed$.data$counter_weight)), "\n")


# match, normal
cw_match <- compute_counter_weight(
  gps_obj_normal,
  ci_appr = "matching",
  nthread = 4,
  delta_n = 0.10, 
  dist_measure = "l1",
  scale = 0.5)

range(cw_match$.data$counter_weight)
table(cw_match$.data$counter_weight == 0)  # TRUE = unmatched
cat("Overall ESS =", round(get_ess(cw_match$.data$counter_weight)), "\n")



# ════════════════════════════════════════════════════════════════
# 5  Generate pseudo-population & check covariate balance (|corr| ≤ .10)
# ════════════════════════════════════════════════════════════════

# weight, normal, trimmed
pseudo_weight_trimmed <- generate_pseudo_pop(
  .data               = gps_df_trimmed,
  cw_obj              = cw_weight_trimmed,
  covariate_col_names = covars,
  covar_bl_trs        = 0.10,
  covar_bl_trs_type   = "maximal",  # "maximal" or "mean"
  covar_bl_method     = "absolute"
)

plot(pseudo_weight_trimmed)


# match, normal
pseudo_match <- generate_pseudo_pop(
  .data               = gps_df_trimmed,
  cw_obj              = cw_match,
  covariate_col_names = covars,
  covar_bl_trs        = 0.10,
  covar_bl_trs_type   = "maximal",  # or "mean"
  covar_bl_method     = "absolute"
)

plot(pseudo_match)


## ────────────────────────────────────────────────────────
## 6. Check Covariate bal_weightance (after weighting)
## ────────────────────────────────────────────────────────

# weight
bal_weight_trimmed <- check_covar_balance(
  w              = pseudo_weight_trimmed$.data[, c("treat")],
  c              = pseudo_weight_trimmed$.data[, pseudo_weight_trimmed$params$covariate_col_names],
  ci_appr        = "weighting",
  counter_weight = pseudo_weight_trimmed$.data[, c("counter_weight")],
  covar_bl_method = "absolute",
  covar_bl_trs    = 0.10,
  covar_bl_trs_type = "mean")  # maximal

# Print results
bal_weight_trimmed$pass  # TRUE if covariate bal_weight_trimmedance is acceptable
bal_weight_trimmed$corr_results$mean_absolute_corr  # summary table of covariate correlations

max_corr <- bal_weight_trimmed$corr_results$maximal_absolute_corr
if (!bal_weight_trimmed$pass) {
  warning(sprintf("bal_weight_trimmedance not achieved: max |corr| = %.3f", max_corr))
}

bad <- bal_weight_trimmed$corr_results$absolute_corr            # vector of |corr|
bad <- bad[bad > .10]
sort(bad, decreasing = TRUE)


# match
bal_match <- check_covar_balance(
  w              = pseudo_match$.data[, c("treat")],
  c              = pseudo_match$.data[, pseudo_match$params$covariate_col_names],
  ci_appr        = "weighting",
  counter_weight = pseudo_match$.data[, c("counter_weight")],
  covar_bl_method = "absolute",
  covar_bl_trs    = 0.10,
  covar_bl_trs_type = "mean")  # maximal

# Print results
bal_match$pass  # TRUE if covariate bal_weightance is acceptable
bal_match$corr_results$mean_absolute_corr  # summary table of covariate correlations

max_corr <- bal_match$corr_results$maximal_absolute_corr
if (!bal_match$pass) {
  warning(sprintf("bal_matchance not achieved: max |corr| = %.3f", max_corr))
}

bad <- bal_match$corr_results$absolute_corr            # vector of |corr|
bad <- bad[bad > .10]
sort(bad, decreasing = TRUE)



## ────────────────────────────────────────────────────────
## 6. Estimate and Plot Exposure–Response Function (ERF)
## ────────────────────────────────────────────────────────

# weight
# ensure the log goes somewhere writable
set_logger(logger_file_path = file.path(tempdir(), "CausalGPS.log"), logger_level = "INFO")

range(pseudo_weight_trimmed$.data$treat)
sd(pseudo_weight_trimmed$.data$treat)

erf_np <- estimate_erf(
  .data            = pseudo_weight_trimmed$.data,
  .formula         = outcome ~ treat,          # treatment column = "treat"
  weights_col_name = "counter_weight",
  model_type       = "nonparametric",
  
  ## Grid of exposure values for which to estimate ERF
  w_vals = seq(
    from = min(pseudo_weight_trimmed$.data$treat),
    to   = max(pseudo_weight_trimmed$.data$treat),
    length.out = 20
  ),
  
  ## Required tuning arguments – TOP-LEVEL, correctly spelled
  bw_seq = seq(0.2, 2, 0.2),
  kernel_appr = "kernsmooth"       # "kernsmooth" 
)


#  ERF → causal contrast (+1 SD)
erf_tbl <- as.data.table(erf_np$.data_prediction)    # cols: w_vals, y_pred
setnames(erf_tbl, c("w_vals","y_pred"), c("treat","erf"))

# interpolate so we hit exactly 0 SD and +1 SD
erf_fun <- approxfun(erf_tbl$treat, erf_tbl$erf)

mu_0  <- erf_fun(0)     # expected speeding at mean of treatment variable
round(mu_0, 3)
mu_1  <- erf_fun(1)     # expected speeding at +1 SD compared to mean
round(mu_1, 3)
delta_gps <- mu_1 - mu_0           # absolute causal difference
round(delta_gps, 3)

mu_n1  <- erf_fun(-1)
round(mu_n1, 3)
delta_gps1 <- mu_0 - mu_n1           # absolute causal difference
round(delta_gps1, 3)



# match
# ensure the log goes somewhere writable
set_logger(logger_file_path = file.path(tempdir(), "CausalGPS.log"), logger_level = "INFO")

range(pseudo_match$.data$treat)
sd(pseudo_match$.data$treat)

erf_np_match <- estimate_erf(
  .data            = pseudo_match$.data,
  .formula         = outcome ~ treat,          # treatment column = "treat"
  weights_col_name = "counter_weight",
  model_type       = "nonparametric",       
  
  ## Grid of exposure values for which to estimate ERF
  w_vals = seq(
    from = min(pseudo_match$.data$treat),
    to   = max(pseudo_match$.data$treat),
    length.out = 20
  ),
  
  ## Required tuning arguments – TOP-LEVEL, correctly spelled
  bw_seq = seq(0.2, 2, 0.2),
  kernel_appr = "kernsmooth"       # "kernsmooth" or "locpol"
)


#  ERF → causal contrast (+1 SD)
erf_tbl_match <- as.data.table(erf_np_match$.data_prediction)    # cols: w_vals, y_pred
setnames(erf_tbl_match, c("w_vals","y_pred"), c("treat","erf"))

# interpolate so we hit exactly 0 SD and +1 SD
erf_fun_match <- approxfun(erf_tbl_match$treat, erf_tbl_match$erf)

mu_0  <- erf_fun_match(0)     # expected speeding at mean treatment variable
round(mu_0, 3)
mu_1  <- erf_fun_match(1)     # expected speeding at +1 SD compared to mean
round(mu_1, 3)
delta_gps <- mu_1 - mu_0           # absolute causal difference
round(delta_gps, 3)

mu_n1  <- erf_fun_match(-1)
round(mu_n1, 3)
delta_gps1 <- mu_0 - mu_n1           # absolute causal difference
round(delta_gps1, 3)

#
