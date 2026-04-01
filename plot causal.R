

# just for 50m

# 50m heat grids
# ── 50m ATT heatmap: X = variables, Y = distance bands ─────────────────────────
library(readxl)
library(dplyr)
library(stringr)
library(forcats)
library(ggplot2)

# ── File path
xlsx_path <- "/Users/longpc/Documents/Leeds/results_new1/causal all2x.xlsx"

# ── Helper to read & parse one sheet
read_att_sheet <- function(path, sheet_name, band_label) {
  pat <- "\\(\\s*([-+]?\\d*\\.?\\d+)\\s*,\\s*([-+]?\\d*\\.?\\d+)\\s*\\)\\s*,\\s*([-+]?\\d*\\.?\\d+)"
  read_excel(path, sheet = sheet_name) %>%
    mutate(
      ATT_chr = str_replace_all(as.character(ATT), "\u2212", "-"),
      m    = as.numeric(str_match(ATT_chr, pat)[, 2]),
      step = as.numeric(str_match(ATT_chr, pat)[, 3]),
      att  = as.numeric(str_match(ATT_chr, pat)[, 4]),
      band = band_label,
      row_id = row_number()
    ) %>%
    transmute(
      var_raw = tolower(trimws(Treat_var)),
      var_lab = str_to_title(Treat_var),
      m, step, att, band, row_id
    )
}

# ── Read ONLY 50m sheets
df_50_400 <- read_att_sheet(xlsx_path, "50m400m", "50m_400m")
df_50_800 <- read_att_sheet(xlsx_path, "50m800m", "50m_800m")
df_50_2k  <- read_att_sheet(xlsx_path, "50m2km",  "50m_2km")
df_50_5k  <- read_att_sheet(xlsx_path, "50m5km",  "50m_5km")

# ── Use the 50–400 m order globally so all 50m plots align
global_order <- df_50_400$var_lab

# ── Binary variables (lowercase to match var_raw)
binary_vars <- c(
  "traffic calming","choker","island","signal crossing","marked crossing",
  "uncontrolled crossing","roundabout","mini roundabout","motorway junction",
  "traffic signal","speed camera","link bidirection"
)

# Combine four 50m bands
df_50_all <- bind_rows(
  df_50_400 %>% mutate(band_short = "400 m"),
  df_50_800 %>% mutate(band_short = "800 m"),
  df_50_2k  %>% mutate(band_short = "2 km"),
  df_50_5k  %>% mutate(band_short = "5 km")
) %>%
  mutate(
    # variables go on X in your global order (left→right)
    var_x = factor(var_lab, levels = global_order),
    # bands go on Y; put 400m at top
    band_short = factor(band_short, levels = c("400 m","800 m","2 km","5 km")),
    att_lab = sprintf("%.2f", att)
  )


# --- Use the exact IRR-style band wiring for ATT (same object names) ---
cutoff_values <- c(-Inf, -30, -20, -10, -5, -2, 0, 2, 5, 10, 20, 30, Inf)

labels <- c(
  "< -30","[-30, -20)","[-20, -10)","[-10, -5)","[-5, -2)",
  "[-2, 0)","[0, 2]", "[2, 5)","[5, 10)","[10, 20)","[20, 30)","> 30"
)

# Same color vectors & assembly pattern as IRR
colors_below_1 <- c("#236da9", "#4a91c7", "#76afdb", "#a6cbea", "#d0e1f4", "#ebf3fc")
colors_above_1 <- c("#fde0e6", "#f9b8cd", "#f598c1", "#f47ab5", "#f05ca9", "#e63d9d")

colors_below_1 <- c("#238443", "#41ab5d", "#78c679", "#addd8e", "#d9f0a3", "#f7fcb9")
colors_above_1 <- c("#fee0d2", "#fcbba1", "#fc9272", "#fb6a4a", "#ef3b2c", "#cb181d")
all_colors <- c(colors_below_1, colors_above_1)


# Bin ATT using the IRR-style objects
df_50_all <- df_50_all %>%
  mutate(ATT_band = cut(att, breaks = cutoff_values, labels = labels, right = FALSE))

# Example positions for adding vertical and horizontal lines
vline_positions <- c(12)  # Positions for vertical lines (between columns)
hline_positions <- c(1, 2, 3, 4)  # Positions for horizontal lines (between rows)


# plot
att_heatmap_50m <- ggplot(df_50_all, aes(x = var_x, y = band_short, fill = ATT_band)) +
  geom_tile(color = "white", linewidth = 0.2) +
  geom_text(aes(label = att_lab), size = 4, color = "black", family = "Arial") +
  scale_fill_manual(values = setNames(all_colors, labels), name = "ATT") +
  scale_x_discrete(expand = c(0.028, 0.028)) +
  scale_y_discrete(expand = c(0.132, 0.132)) +
  labs(
    title = "Average Treatment Effect on the Treated (ATT) on Speeding Events by Network Distance",
    # x = "Binary Treatment (PSM) vs Continuous Treatment (GPS)",
    x = "Binary Treatment via Propensity Score Matching vs Continuous Treatment via Generalized Propensity Score",
    y = NULL
  ) +
  theme_linedraw(base_size = 14, base_family = "Arial") +
  theme(
    panel.grid = element_blank(),
    panel.border = element_rect(color = "black", linewidth = 0.8),
    axis.ticks = element_line(color = "black", linewidth = 0.4),
    axis.ticks.length = unit(0.16, "cm"),
    axis.text.x = element_text(size = 12, angle = 40, hjust = 1, vjust = 1, family = "Arial"),
    axis.text.y = element_text(size = 13, family = "Arial"),
    axis.title.x = element_text(size = 13, color = "black", margin = margin(t = 6), family = "Arial"),
    legend.position = "right",
    legend.title = element_text(size = 12),
    legend.text  = element_text(size = 12),
    plot.title = element_text(size = 14, margin = margin(b = 6))
  ) +
  # Add vertical lines between specific columns
  geom_vline(xintercept = vline_positions + 0.5, color = "white", linewidth = 1.2) +
  # Add horizontal lines between specific rows
  geom_hline(yintercept = hline_positions + 0.5, color = "white", linewidth = 0.5)


print(att_heatmap_50m)


# Save
out_dir <- "/Users/longpc/Documents/Leeds/plot3_update1/fig"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
ggsave(
  filename = file.path(out_dir, "ATT_heatmap_50m.png"),
  plot = att_heatmap_50m, width = 14, height = 6, dpi = 300
)







# 50m heat grids, speeding percent
# ── 50m ATT heatmap: X = variables, Y = distance bands ─────────────────────────
library(readxl)
library(dplyr)
library(stringr)
library(forcats)
library(ggplot2)

# ── File path
xlsx_path <- "/Users/longpc/Documents/Leeds/results_revision/causal/causal revision.xlsx"

# ── Helper to read & parse one sheet
read_att_sheet <- function(path, sheet_name, band_label) {
  pat <- "\\(\\s*([-+]?\\d*\\.?\\d+)\\s*,\\s*([-+]?\\d*\\.?\\d+)\\s*\\)\\s*,\\s*([-+]?\\d*\\.?\\d+)"
  read_excel(path, sheet = sheet_name) %>%
    mutate(
      ATT_chr = str_replace_all(as.character(ATT), "\u2212", "-"),
      m    = as.numeric(str_match(ATT_chr, pat)[, 2]),
      step = as.numeric(str_match(ATT_chr, pat)[, 3]),
      att  = as.numeric(str_match(ATT_chr, pat)[, 4]),
      band = band_label,
      row_id = row_number()
    ) %>%
    transmute(
      var_raw = tolower(trimws(Treat_var)),
      var_lab = str_to_title(Treat_var),
      m, step, att, band, row_id
    )
}

# ── Read ONLY 50m sheets
df_50_400 <- read_att_sheet(xlsx_path, "50m400m", "50m_400m")
df_50_800 <- read_att_sheet(xlsx_path, "50m800m", "50m_800m")
df_50_2k  <- read_att_sheet(xlsx_path, "50m2km",  "50m_2km")
df_50_5k  <- read_att_sheet(xlsx_path, "50m5km",  "50m_5km")

# ── Use the 50–400 m order globally so all 50m plots align
global_order <- df_50_400$var_lab

# ── Binary variables (lowercase to match var_raw)
binary_vars <- c(
  "traffic calming","choker","island","signal crossing","marked crossing",
  "uncontrolled crossing","roundabout","mini roundabout","motorway junction",
  "traffic signal","speed camera","link bidirection"
)

# Combine four 50m bands
df_50_all <- bind_rows(
  df_50_400 %>% mutate(band_short = "400 m"),
  df_50_800 %>% mutate(band_short = "800 m"),
  df_50_2k  %>% mutate(band_short = "2 km"),
  df_50_5k  %>% mutate(band_short = "5 km")
) %>%
  mutate(
    # variables go on X in your global order (left→right)
    var_x = factor(var_lab, levels = global_order),
    # bands go on Y; put 400m at top
    band_short = factor(band_short, levels = c("400 m","800 m","2 km","5 km")),
    att_lab = sprintf("%.2f", att)
  )


# --- Use the exact IRR-style band wiring for ATT (same object names) ---
cutoff_values <- c(-Inf, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, Inf)

labels <- c(
  "< -5","[-5, -4)","[-4, -3)","[-3, -2)","[-2, -1)",
  "[-1, 0)","[0, 1)", "[1, 2)","[2, 3)","[3, 4)","[4, 5)","> 5"
)

# Same color vectors & assembly pattern as IRR
colors_below_1 <- c("#236da9", "#4a91c7", "#76afdb", "#a6cbea", "#d0e1f4", "#ebf3fc")
colors_above_1 <- c("#fde0e6", "#f9b8cd", "#f598c1", "#f47ab5", "#f05ca9", "#e63d9d")

colors_below_1 <- c("#238443", "#41ab5d", "#78c679", "#addd8e", "#d9f0a3", "#f7fcb9")
colors_above_1 <- c("#fee0d2", "#fcbba1", "#fc9272", "#fb6a4a", "#ef3b2c", "#cb181d")
all_colors <- c(colors_below_1, colors_above_1)


# Bin ATT using the IRR-style objects
df_50_all <- df_50_all %>%
  mutate(ATT_band = cut(att, breaks = cutoff_values, labels = labels, right = FALSE))

# Example positions for adding vertical and horizontal lines
vline_positions <- c(12)  # Positions for vertical lines (between columns)
hline_positions <- c(1, 2, 3, 4)  # Positions for horizontal lines (between rows)


# plot
att_heatmap_50m <- ggplot(df_50_all, aes(x = var_x, y = band_short, fill = ATT_band)) +
  geom_tile(color = "white", linewidth = 0.2) +
  geom_text(aes(label = att_lab), size = 4, color = "black", family = "Arial") +
  scale_fill_manual(values = setNames(all_colors, labels), name = "ATT") +
  scale_x_discrete(expand = c(0.028, 0.028)) +
  scale_y_discrete(expand = c(0.132, 0.132)) +
  labs(
    title = "Average Treatment Effect on the Treated (ATT) on Speeding Rates (%) by Network Distance",
    # x = "Binary Treatment (PSM) vs Continuous Treatment (GPS)",
    x = "Binary Treatment via Propensity Score Matching vs Continuous Treatment via Generalized Propensity Score",
    y = NULL
  ) +
  theme_linedraw(base_size = 14, base_family = "Arial") +
  theme(
    panel.grid = element_blank(),
    panel.border = element_rect(color = "black", linewidth = 0.8),
    axis.ticks = element_line(color = "black", linewidth = 0.4),
    axis.ticks.length = unit(0.16, "cm"),
    axis.text.x = element_text(size = 12, angle = 40, hjust = 1, vjust = 1, family = "Arial"),
    axis.text.y = element_text(size = 13, family = "Arial"),
    axis.title.x = element_text(size = 13, color = "black", margin = margin(t = 6), family = "Arial"),
    legend.position = "right",
    legend.title = element_text(size = 12),
    legend.text  = element_text(size = 12),
    plot.title = element_text(size = 14, margin = margin(b = 6))
  ) +
  # Add vertical lines between specific columns
  geom_vline(xintercept = vline_positions + 0.5, color = "white", linewidth = 1.2) +
  # Add horizontal lines between specific rows
  geom_hline(yintercept = hline_positions + 0.5, color = "white", linewidth = 0.5)


print(att_heatmap_50m)


# Save
out_dir <- "/Users/longpc/Documents/Leeds/results_revision"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
ggsave(
  filename = file.path(out_dir, "ATT_heatmap_50m_Pct.png"),
  plot = att_heatmap_50m, width = 14, height = 6, dpi = 300
)








# 50m heat grids, sensitivity, speeding rate
# ── 50m ATT heatmap: X = variables, Y = distance bands ─────────────────────────
library(readxl)
library(dplyr)
library(stringr)
library(forcats)
library(ggplot2)

# ── File path
xlsx_path <- "/Users/longpc/Documents/Leeds/results_revision/causal1/causal revision1 rate.xlsx"

# ── Helper to read & parse one sheet
read_att_sheet <- function(path, sheet_name, band_label) {
  irr_pat <- "([-+]?\\d*\\.?\\d+)\\s*,\\s*\\(\\s*([-+]?\\d*\\.?\\d+)\\s*,\\s*([-+]?\\d*\\.?\\d+)\\s*\\)"
  read_excel(path, sheet = sheet_name) %>%
    mutate(
      IRR_chr = str_replace_all(as.character(IRR), "\u2212", "-"),
      m    = as.numeric(str_match(IRR_chr, irr_pat)[, 3]),
      step = as.numeric(str_match(IRR_chr, irr_pat)[, 4]),
      irr  = as.numeric(str_match(IRR_chr, irr_pat)[, 2]),
      band = band_label,
      row_id = row_number()
    ) %>%
    transmute(
      var_raw = tolower(trimws(Treat_var)),
      var_lab = str_to_title(Treat_var),
      m, step, irr, band, row_id
    )
}

# ── Read ONLY 50m sheets
df_50_400 <- read_att_sheet(xlsx_path, "50m400m", "50m_400m")
df_50_800 <- read_att_sheet(xlsx_path, "50m800m", "50m_800m")
df_50_2k  <- read_att_sheet(xlsx_path, "50m2km",  "50m_2km")
df_50_5k  <- read_att_sheet(xlsx_path, "50m5km",  "50m_5km")

# ── Use the 50–400 m order globally so all 50m plots align
global_order <- df_50_400$var_lab

# ── Binary variables (lowercase to match var_raw)
binary_vars <- c(
  "traffic calming","choker","island","signal crossing","marked crossing",
  "uncontrolled crossing","roundabout","mini roundabout","motorway junction",
  "traffic signal","speed camera","link bidirection"
)

# Combine four 50m bands
df_50_all <- bind_rows(
  df_50_400 %>% mutate(band_short = "400 m"),
  df_50_800 %>% mutate(band_short = "800 m"),
  df_50_2k  %>% mutate(band_short = "2 km"),
  df_50_5k  %>% mutate(band_short = "5 km")
) %>%
  mutate(
    # variables go on X in your global order (left→right)
    var_x = factor(var_lab, levels = global_order),
    # bands go on Y; put 400m at top
    band_short = factor(band_short, levels = c("400 m","800 m","2 km","5 km")),
    irr_lab = sprintf("%.2f", irr)
  )


# --- Use the exact IRR-style band wiring for ATT (same object names) ---
cutoff_values <- c(0.6, 0.7, 0.8, 0.9, 1, 1.2, 1.4, 1.6, 2.0)

labels <- c(
  "[0.6, 0.7)","[0.7, 0.8)","[0.8, 0.9)","[0.9, 1.0)",
  "[1, 1.2)","[1.2, 1.4]", "[1.4, 1.6)", "[1.8, 2.0)"
)

# Same color vectors & assembly pattern as IRR
colors_below_1 <- c("#238443", "#41ab5d", "#78c679", "#addd8e", "#d9f0a3", "#f7fcb9")
colors_above_1 <- c("#fee0d2", "#fcbba1", "#fc9272", "#fb6a4a", "#ef3b2c", "#cb181d")

colors_below_1 <- c("#41ab5d", "#78c679", "#addd8e", "#d9f0a3")
colors_above_1 <- c("#fcbba1", "#fc9272", "#fb6a4a", "#ef3b2c")
all_colors <- c(colors_below_1, colors_above_1)


# Bin ATT using the IRR-style objects
df_50_all <- df_50_all %>%
  mutate(IRR_band = cut(irr, breaks = cutoff_values, labels = labels, right = FALSE))

# Example positions for adding vertical and horizontal lines
vline_positions <- c(12)  # Positions for vertical lines (between columns)
hline_positions <- c(1, 2, 3, 4)  # Positions for horizontal lines (between rows)


# plot
irr_heatmap_50m <- ggplot(df_50_all, aes(x = var_x, y = band_short, fill = IRR_band)) +
  geom_tile(color = "white", linewidth = 0.2) +
  geom_text(aes(label = irr_lab), size = 4, color = "black", family = "Arial") +
  scale_fill_manual(values = setNames(all_colors, labels), name = "IRR (ATT)") +
  scale_x_discrete(expand = c(0.028, 0.028)) +
  scale_y_discrete(expand = c(0.132, 0.132)) +
  labs(
    title = "Post Causal Model IRR as ATT for Speeding Rates (%) by Network Distance",
    # x = "Binary Treatment (PSM) vs Continuous Treatment (GPS)",
    x = "Binary Treatment via Propensity Score Matching vs Continuous Treatment via Generalized Propensity Score",
    y = NULL
  ) +
  theme_linedraw(base_size = 14, base_family = "Arial") +
  theme(
    panel.grid = element_blank(),
    panel.border = element_rect(color = "black", linewidth = 0.8),
    axis.ticks = element_line(color = "black", linewidth = 0.4),
    axis.ticks.length = unit(0.16, "cm"),
    axis.text.x = element_text(size = 12, angle = 40, hjust = 1, vjust = 1, family = "Arial"),
    axis.text.y = element_text(size = 13, family = "Arial"),
    axis.title.x = element_text(size = 13, color = "black", margin = margin(t = 6), family = "Arial"),
    legend.position = "right",
    legend.title = element_text(size = 12),
    legend.text  = element_text(size = 12),
    plot.title = element_text(size = 14, margin = margin(b = 6))
  ) +
  # Add vertical lines between specific columns
  geom_vline(xintercept = vline_positions + 0.5, color = "white", linewidth = 1.2) +
  # Add horizontal lines between specific rows
  geom_hline(yintercept = hline_positions + 0.5, color = "white", linewidth = 0.5)


print(irr_heatmap_50m)


# Save
out_dir <- "/Users/longpc/Documents/Leeds/results_revision"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
ggsave(
  filename = file.path(out_dir, "IRR_heatmap_50m_Pct.png"),
  plot = irr_heatmap_50m, width = 14, height = 6, dpi = 300
)




# 50m heat grids, sensitivity, speeding events
# ── 50m ATT heatmap: X = variables, Y = distance bands ─────────────────────────
library(readxl)
library(dplyr)
library(stringr)
library(forcats)
library(ggplot2)

# ── File path
xlsx_path <- "/Users/longpc/Documents/Leeds/results_revision/causal1/causal revision1 count.xlsx"

# ── Helper to read & parse one sheet
read_att_sheet <- function(path, sheet_name, band_label) {
  irr_pat <- "([-+]?\\d*\\.?\\d+)\\s*,\\s*\\(\\s*([-+]?\\d*\\.?\\d+)\\s*,\\s*([-+]?\\d*\\.?\\d+)\\s*\\)"
  read_excel(path, sheet = sheet_name) %>%
    mutate(
      IRR_chr = str_replace_all(as.character(IRR), "\u2212", "-"),
      m    = as.numeric(str_match(IRR_chr, irr_pat)[, 3]),
      step = as.numeric(str_match(IRR_chr, irr_pat)[, 4]),
      irr  = as.numeric(str_match(IRR_chr, irr_pat)[, 2]),
      band = band_label,
      row_id = row_number()
    ) %>%
    transmute(
      var_raw = tolower(trimws(Treat_var)),
      var_lab = str_to_title(Treat_var),
      m, step, irr, band, row_id
    )
}

# ── Read ONLY 50m sheets
df_50_400 <- read_att_sheet(xlsx_path, "50m400m", "50m_400m")
df_50_800 <- read_att_sheet(xlsx_path, "50m800m", "50m_800m")
df_50_2k  <- read_att_sheet(xlsx_path, "50m2km",  "50m_2km")
df_50_5k  <- read_att_sheet(xlsx_path, "50m5km",  "50m_5km")

# ── Use the 50–400 m order globally so all 50m plots align
global_order <- df_50_400$var_lab

# ── Binary variables (lowercase to match var_raw)
binary_vars <- c(
  "traffic calming","choker","island","signal crossing","marked crossing",
  "uncontrolled crossing","roundabout","mini roundabout","motorway junction",
  "traffic signal","speed camera","link bidirection"
)

# Combine four 50m bands
df_50_all <- bind_rows(
  df_50_400 %>% mutate(band_short = "400 m"),
  df_50_800 %>% mutate(band_short = "800 m"),
  df_50_2k  %>% mutate(band_short = "2 km"),
  df_50_5k  %>% mutate(band_short = "5 km")
) %>%
  mutate(
    # variables go on X in your global order (left→right)
    var_x = factor(var_lab, levels = global_order),
    # bands go on Y; put 400m at top
    band_short = factor(band_short, levels = c("400 m","800 m","2 km","5 km")),
    irr_lab = sprintf("%.2f", irr)
  )


# --- Use the exact IRR-style band wiring for ATT (same object names) ---
cutoff_values <- c(0.3, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.2, 1.4, 1.6, 1.8, 2.0, 5)

labels <- c(
  "< 0.5","[0.5, 0.6)","[0.6, 0.7)","[0.7, 0.8)","[0.8, 0.9)","[0.9, 1.0)",
  "[1, 1.2)","[1.2, 1.4]", "[1.4, 1.6)","[1.6, 1.8)","[1.8, 2.0)", "> 2.0"
)

# Same color vectors & assembly pattern as IRR

colors_below_1 <- c("#238443", "#41ab5d", "#78c679", "#addd8e", "#d9f0a3", "#f7fcb9")
colors_above_1 <- c("#fee0d2", "#fcbba1", "#fc9272", "#fb6a4a", "#ef3b2c", "#cb181d")
all_colors <- c(colors_below_1, colors_above_1)


# Bin ATT using the IRR-style objects
df_50_all <- df_50_all %>%
  mutate(IRR_band = cut(irr, breaks = cutoff_values, labels = labels, right = FALSE))

# Example positions for adding vertical and horizontal lines
vline_positions <- c(12)  # Positions for vertical lines (between columns)
hline_positions <- c(1, 2, 3, 4)  # Positions for horizontal lines (between rows)


# plot
irr_heatmap_50m <- ggplot(df_50_all, aes(x = var_x, y = band_short, fill = IRR_band)) +
  geom_tile(color = "white", linewidth = 0.2) +
  geom_text(aes(label = irr_lab), size = 4, color = "black", family = "Arial") +
  scale_fill_manual(values = setNames(all_colors, labels), name = "IRR (ATT)") +
  scale_x_discrete(expand = c(0.028, 0.028)) +
  scale_y_discrete(expand = c(0.132, 0.132)) +
  labs(
    title = "Post Causal Model IRR as ATT for Speeding Events by Network Distance",
    # x = "Binary Treatment (PSM) vs Continuous Treatment (GPS)",
    x = "Binary Treatment via Propensity Score Matching vs Continuous Treatment via Generalized Propensity Score",
    y = NULL
  ) +
  theme_linedraw(base_size = 14, base_family = "Arial") +
  theme(
    panel.grid = element_blank(),
    panel.border = element_rect(color = "black", linewidth = 0.8),
    axis.ticks = element_line(color = "black", linewidth = 0.4),
    axis.ticks.length = unit(0.16, "cm"),
    axis.text.x = element_text(size = 12, angle = 40, hjust = 1, vjust = 1, family = "Arial"),
    axis.text.y = element_text(size = 13, family = "Arial"),
    axis.title.x = element_text(size = 13, color = "black", margin = margin(t = 6), family = "Arial"),
    legend.position = "right",
    legend.title = element_text(size = 12),
    legend.text  = element_text(size = 12),
    plot.title = element_text(size = 14, margin = margin(b = 6))
  ) +
  # Add vertical lines between specific columns
  geom_vline(xintercept = vline_positions + 0.5, color = "white", linewidth = 1.2) +
  # Add horizontal lines between specific rows
  geom_hline(yintercept = hline_positions + 0.5, color = "white", linewidth = 0.5)


print(irr_heatmap_50m)


# Save
out_dir <- "/Users/longpc/Documents/Leeds/results_revision"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
ggsave(
  filename = file.path(out_dir, "IRR_heatmap_50m_Count.png"),
  plot = irr_heatmap_50m, width = 14, height = 6, dpi = 300
)






