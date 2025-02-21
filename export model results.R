library(lmerTest)
library(openxlsx) 


# export results
modelres_glmmTMB <- function(model) {
  # Ensure required packages are installed
  if (!requireNamespace("glmmTMB", quietly = TRUE)) {
    stop("Please install the 'glmmTMB' package.")
  }
  
  # Extract summary statistics
  summ <- summary(model)
  coeffs <- as.data.frame(summ$coefficients$cond)
  coeffs$Parameter <- rownames(coeffs)
  
  # Extract confidence intervals
  conf_int <- confint(model, parm = "beta_", method = "Wald")
  conf_int <- as.data.frame(conf_int)
  conf_int$Parameter <- rownames(conf_int)
  conf_int <- conf_int[, c("Parameter", "2.5 %", "97.5 %")]
  
  # std_coef_df <- as.data.frame(standardize_parameters(model))
  # print(std_coef_df)
  # std_coef_df <- std_coef_df[, c("Parameter", "Std_Coefficient")]
  
  # Merge coefficients and confidence intervals
  res_df <- merge(coeffs, conf_int, by = "Parameter", sort = FALSE)
  # res_df <- merge(res_df, std_coef_df, by = "Parameter", sort = FALSE, all = TRUE)
  
  # Calculate IRR and 95% CI for IRR
  res_df$IRR <- exp(res_df$Estimate)
  res_df$IRR_Lower <- exp(res_df$`2.5 %`)
  res_df$IRR_Upper <- exp(res_df$`97.5 %`)
  
  # Select and rename columns
  # res_df <- res_df[, c("Parameter", "Estimate", "Std. Error", "z value", "Pr(>|z|)", "2.5 %", "97.5 %", "IRR", "IRR_Lower", "IRR_Upper", "Std_Coefficient")]
  # names(res_df) <- c("Parameter", "Estimate", "Std_Error", "z_value", "p_value", "CI_2.5%", "CI_97.5%", "IRR", "IRR_2.5%", "IRR_97.5%", "Std_Coef_effectsize")
  
  res_df <- res_df[, c("Parameter", "Estimate", "Std. Error", "z value", "Pr(>|z|)", "2.5 %", "97.5 %", "IRR", "IRR_Lower", "IRR_Upper")]
  names(res_df) <- c("Parameter", "Estimate", "Std_Error", "z_value", "p_value", "CI_2.5%", "CI_97.5%", "IRR", "IRR_2.5%", "IRR_97.5%")
  
  # Round values
  res_df$Estimate <- formatC(res_df$Estimate, format = "f", digits = 3)
  res_df$Std_Error <- formatC(res_df$Std_Error, format = "f", digits = 3)
  res_df$z_value <- formatC(res_df$z_value, format = "f", digits = 3)
  res_df$`CI_2.5%` <- formatC(res_df$`CI_2.5%`, format = "f", digits = 3)
  res_df$`CI_97.5%` <- formatC(res_df$`CI_97.5%`, format = "f", digits = 3)
  res_df$IRR <- formatC(res_df$IRR, format = "f", digits = 3)
  res_df$`IRR_2.5%` <- formatC(res_df$`IRR_2.5%`, format = "f", digits = 3)
  res_df$`IRR_97.5%` <- formatC(res_df$`IRR_97.5%`, format = "f", digits = 3)
  
  res_df$p_value_num <- res_df$p_value
  res_df$p_value <- formatC(res_df$p_value, format = "f", digits = 3)
  
  # Create formatted strings for estimates and IRRs with their 95% CIs
  res_df$Estimate_CI <- paste0(res_df$Estimate, " (", res_df$`CI_2.5%`, ", ", res_df$`CI_97.5%`, ")")
  res_df$Estimate_CIx <- paste0("(", res_df$`CI_2.5%`, ", ", res_df$`CI_97.5%`, ")")
  res_df$IRR_CI <- paste0(res_df$IRR, " (", res_df$`IRR_2.5%`, ", ", res_df$`IRR_97.5%`, ")")
  res_df$IRR_CIx <- paste0("(", res_df$`IRR_2.5%`, ", ", res_df$`IRR_97.5%`, ")")
  
  # Add significance stars
  res_df$Significance <- ifelse(res_df$p_value_num < 0.001, "***",
                                ifelse(res_df$p_value_num < 0.01, "**",
                                       ifelse(res_df$p_value_num < 0.05, "*", "")))
  
  res_df$p_sig <- paste0(res_df$p_value, res_df$Significance)
  
  # res_df$Std_Coef_effectsize <- formatC(res_df$Std_Coef_effectsize, format = "f", digits = 3)
  
  # Arrange columns
  # res_df <- res_df[, c("Parameter", "Estimate", "Std_Error", "z_value", "CI_2.5%", "CI_97.5%", "Estimate_CI", "Estimate_CIx", "IRR", "IRR_2.5%", "IRR_97.5%", "IRR_CI", "IRR_CIx", "p_value", "Significance", "p_sig", "Std_Coef_effectsize")]
  res_df <- res_df[, c("Parameter", "Estimate_CI", "p_sig", "IRR", "Estimate_CIx", "Significance", "IRR_CI", "IRR_CIx")]
  
  return(res_df)
}



# Export to CSV
results_glmmTMB <- modelres_glmmTMB(mod_speeding_100m10km_mph70)
file_path <- "/Users/longpc/Documents/Leeds/results/mod_speeding_100m10km.xlsx"

if (file.exists(file_path)) {
  wb <- loadWorkbook(file_path)
} else {
  wb <- createWorkbook()
}

addWorksheet(wb, "10km_mph70")
writeData(wb, "10km_mph70", results_glmmTMB, rowNames = FALSE)
saveWorkbook(wb, file = file_path, overwrite = TRUE)


