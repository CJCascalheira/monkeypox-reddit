# REMOVE BOTS AND SIMILAR POSTS BETWEEN DATA SETS -------------------------

# @author: Cory J. Cascalheira
# Created: 2022.10.29

# Load dependencies
library(tidyverse)

# Import virus data
virus <- read_csv("data/original_data/all_subreddits_virus_data.csv")
virus_liwc <- read_csv("data/original_data/all_subreddits_virus_data_liwc_features.csv")
mpx <- read_csv("data/original_data/all_subreddits_mpx_data.csv")
mpx_liwc <- read_csv("data/original_data/all_subreddits_mpx_data_liwc_features.csv")

# CLEAN THE DATA ----------------------------------------------------------

# Clean virus data
virus <- virus %>%
  # Remove posts that also contain MPX term
  filter(contains_monkeypox_term == 0) %>%
  # Remove bot authors
  mutate(is_bot = if_else(str_detect(author, regex("bot$|moderator", ignore_case = TRUE)), 1, 0)) %>%
  filter(is_bot == 0) %>%
  select(-is_bot) %>%
  # Only keep distinct text
  distinct(body, .keep_all = TRUE)
virus

virus_liwc <- virus_liwc %>% 
  # Remove posts that also contain MPX term
  filter(contains_monkeypox_term == 0) %>%
  # Remove bot authors
  mutate(is_bot = if_else(str_detect(author, regex("bot$|moderator", ignore_case = TRUE)), 1, 0)) %>%
  filter(is_bot == 0) %>%
  select(-is_bot) %>%
  # Only keep distinct text
  distinct(body...2, .keep_all = TRUE) %>%
  rename(body = body...2)
virus_liwc

# Clean the MPX data
mpx <- mpx %>%
  # Remove bot authors
  mutate(is_bot = if_else(str_detect(author, regex("bot$|moderator", ignore_case = TRUE)), 1, 0)) %>%
  filter(is_bot == 0) %>%
  select(-is_bot) %>%
  # Only keep distinct text
  distinct(body, .keep_all = TRUE)

mpx_liwc <- mpx_liwc %>%
  # Remove bot authors
  mutate(is_bot = if_else(str_detect(author, regex("bot$|moderator", ignore_case = TRUE)), 1, 0)) %>%
  filter(is_bot == 0) %>%
  select(-is_bot) %>%
  # Only keep distinct text
  distinct(body...2, .keep_all = TRUE) %>%
  rename(body = body...2)

# BRIEF ANALYSIS ----------------------------------------------------------

# How many posts just related to virus?
nrow(virus)

# Count the number of subreddits and get percentages
virus %>%
  count(subreddit) %>%
  mutate(perc = (n / nrow(virus)) * 100) %>%
  arrange(desc(perc))

# How many posts related to MPX?
nrow(mpx)

# Count the number of subreddits and get percentages
mpx %>%
  count(subreddit) %>%
  mutate(perc = (n / nrow(mpx)) * 100) %>%
  arrange(desc(perc))

# How many unique users?
bind_rows(mpx, virus) %>%
  distinct(author) %>%
  nrow()

# Export to file
write_csv(virus, "data/combined_subreddits/all_subreddits_virus_data.csv")
write_csv(virus_liwc, "data/combined_subreddits/all_subreddits_virus_data_liwc_features.csv")
write_csv(mpx, "data/combined_subreddits/all_subreddits_mpx_data.csv")
write_csv(mpx_liwc, "data/combined_subreddits/all_subreddits_mpx_data_liwc_features.csv")
