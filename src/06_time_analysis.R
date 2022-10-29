# LONGITUDINAL ANALYSIS OF MPX CONVERSATION -------------------------------

# @author Cory J. Cascalheira
# Created: 2022-10-29

# The purpose of this script is to understand the MPX conversation by looking
# at key psycholinguistic variables and sentiment over time.

# This script is written in R to leverage the powerful graphing techniques
# of ggplot2. 

# Load dependencies
library(tidyverse)
library(lubridate)

# Import data
mpx <- read_csv("data/all_subreddits_mpx_data_liwc_features.csv") %>%
  rename(text = body...2, body = body...65, time_created = converted_createdutc) %>%
  # Remove unnecessary columns
  select(-author, -created_utc, -retrieved_utc, -permalink, -link_id, -parent_id,
         -contains_epoxy_term, -contains_monkeypox_term) %>%
  # Convert to date
  mutate(time_created = dmy_hm(time_created))

# PREPROCESS DATA ---------------------------------------------------------

mpx

# LIWC FEATURES OVER TIME -------------------------------------------------

# SENTIMENT OVERTIME ------------------------------------------------------

