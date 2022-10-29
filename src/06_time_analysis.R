# LONGITUDINAL ANALYSIS OF MPX CONVERSATION -------------------------------

# @author Cory J. Cascalheira
# Created: 2022-10-29

# The purpose of this script is to understand the MPX conversation by looking
# at conversation volume, key psycholinguistic variables, and sentiment over time.

# This script is written in R to leverage the powerful graphing techniques
# of ggplot2. 

# LOAD AND IMPORT ---------------------------------------------------------

# Load dependencies
library(tidyverse)
library(lubridate)
library(scales)

# Import data - MPX data set
mpx <- read_csv("data/all_subreddits_mpx_data_liwc_features.csv") %>%
  rename(text = body...2, body = body...65, time_created = converted_createdutc) %>%
  # Remove unnecessary columns
  select(-author, -created_utc, -retrieved_utc, -permalink, -link_id, -parent_id,
         -contains_epoxy_term, -contains_monkeypox_term) %>%
  # Convert to date
  mutate(time_created = dmy_hm(time_created)) %>%
  # Add temporary id variables
  mutate(temp_id = 1:nrow(.)) %>%
  select(temp_id, subreddit, time_created, everything())

# Import data - virus data set
virus <- read_csv("data/all_subreddits_virus_data_liwc_features.csv") %>%
  rename(text = body...2, body = body...65, time_created = converted_createdutc) %>%
  # Remove unnecessary columns
  select(-author, -created_utc, -retrieved_utc, -permalink, -link_id, -parent_id,
         -contains_monkeypox_term, -contains_virus_term) %>%
  # Convert to date
  mutate(time_created = dmy_hm(time_created)) %>%
  # Add temporary id variables
  mutate(temp_id = 1:nrow(.)) %>%
  select(temp_id, subreddit, time_created, everything())

# DEFINE FUNCTIONS --------------------------------------------------------

# Min-max normalization for features
scale_this <- function(x){
  (x - min(x)) / (max(x) - min(x))
}

# PREPROCESS DATA ---------------------------------------------------------

# General preprocessing of the LIWC data 
mpx_liwc <- mpx %>%
  # Make long format
  pivot_longer(cols = WC:OtherP, names_to = "liwc_names", values_to = "liwc_values") %>%
  # Min-max normalize feature values
  group_by(liwc_names) %>%
  mutate(liwc_values = scale_this(liwc_values)) %>%
  ungroup() %>%
  # Add LIWC categories
  mutate(
    liwc_categories = if_else(liwc_names %in% c("Analytic", "Clout", "Authentic", 
                                                "Tone", "WPS", "Sixltr", "Dic"), 
                              "Summary", "None"),
    liwc_categories = if_else(liwc_names %in% c("funct", "pronoun", "ppron", "i", "we", "you",
                                                "shehe", "they", "ipron", "article", "prep",
                                                "auxverb", "adverb", "conj", "negate"), 
                              "Linguistic", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c("verb", "adj", "compare", "interrog", "numbers",
                                                "quant"), 
                              "Grammar", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c(""), 
                              "Affect", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c(""), 
                              "Social", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c(""), 
                              "Cognitive", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c(""), 
                              "Perceptual", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c(""), 
                              "Biological", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c(""), 
                              "Drives", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c(""), 
                              "Time Orientation", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c(""), 
                              "Relativity", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c(""), 
                              "Personal Concerns", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c("swear", "netspeak", "assent", "nonflu", "filler"), 
                              "Informal Language", liwc_categories)
  )
mpx_liwc

# CONVERSATION VOLUME OVER TIME -------------------------------------------

# For week to date conversion, see:
# https://www.epochconverter.com/weeks/2021

# MPX conversation volume over time
mpx_volume_plot <- mpx %>%
  mutate(time_week = week(time_created)) %>%
  count(time_week) %>%
  ggplot(aes(x = time_week, y = n)) +
  geom_line(size = 1.5) +
  # Date of first U.S. Case - 17 May 2022
  geom_vline(xintercept = 20) +
  annotate("label", x = 20, y = 2800, label = "1st U.S. case of\nMPX reported") +
  # US White House announce MPX outbreak response - 28 June 2022
  geom_vline(xintercept = 26) +
  annotate("label", x = 26, y = 1600, label = "U.S. announces national\nvaccine strategy") +
  # Number of JYNNEOS vaccines reaches > 50,000 in US - 07/24 to 07/30, 2022
  geom_vline(xintercept = 29) +
  annotate("label", x = 28, y = 2700, label = "Number of\nJYNNEOS\ndoses > 50,000") +
  # Highest spike in number of US cases - 2nd week of August 2022
  geom_vline(xintercept = 32) +
  annotate("label", x = 33.5, y = 1600, label = "Highest spike in\nreported MPX cases") +
  # Over 30% of eligible MSM vaccinated with first dose - 10 September 2022
  geom_vline(xintercept = 36) +
  annotate("label", x = 36, y = 800, label = ">30% of high-risk population\nbecomes vaccinated") +
  scale_y_continuous(breaks = pretty_breaks(n = 15), labels = comma) +
  scale_x_continuous(breaks = c(21, 25, 29, 33, 37, 41), 
                     labels = c("21" = "May", "25" = "June", "29" = "July", "33" = "August", 
                                "37" = "September", "41" = "October")) +
  labs(x = "Months in 2022", y = "Number of MPX-Related Posts and Comments") +
  theme_bw() 

# Save plot
ggsave(filename = "plots/mpx_volume_over_time.png", plot = mpx_volume_plot,
       width = 10, height = 5)

# LIWC FEATURES OVER TIME -------------------------------------------------

mpx_liwc %>%
  ggplot(aes(x = time_created, y = liwc_values, group = liwc_names, color = liwc_names)) +
  geom_line()

# SENTIMENT OVERTIME ------------------------------------------------------

