# Load dependencies
library(tidyverse)

# Import virus data
virus <- read_csv("data/original_virus/all_subreddits_virus_data.csv")
liwc <- read_csv("data/original_virus/all_subreddits_virus_data_liwc_features.csv")

# Remove posts that also contain MPX term
virus <- virus %>%
  filter(contains_monkeypox_term == 0)

liwc <- liwc %>% 
  filter(contains_monkeypox_term == 0)

# How many posts just related to virus?
nrow(virus)

# Count the number of subreddits and get percentages
virus %>%
  count(subreddit) %>%
  mutate(perc = (n / nrow(virus)) * 100) %>%
  arrange(desc(perc))

# Export to file
write_csv(virus, "data/all_subreddits_virus_data.csv")
write_csv(liwc, "data/all_subreddits_virus_data_liwc_features.csv")
