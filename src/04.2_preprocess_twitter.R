# CLEAN UP THE TWITTER DATA -----------------------------------------------

# @author: Cory J. Cascalheira
# Created: 2023.01.03

# Load dependencies
library(tidyverse)
library(lubridate)

# Load all tweets
all_files <- list.files(path = "data/original_data/tweets/")
tweets_a <- map_df(all_files, ~ read_csv(paste0("data/original_data/tweets/", .)))

# Select variables
tweets <- tweets_a %>%
  select(date, tweetm) %>%
  mutate(temp_id = 1:nrow(.)) %>%
  mutate(date = ymd(date)) %>%
  select(temp_id, everything()) %>%
  rename(text = tweetm) %>%
  # Filter for dates to match Reddit dataset
  filter(date > ymd('2022-05-01'), date <= ymd('2022-10-13'))
tweets

# Number of tweets in date range
nrow(tweets)

# CLEAN -------------------------------------------------------------------

# Remove missing data
tweets_1 <- tweets %>%
  mutate(text = str_remove_all(text, regex("\\[")),
         text = str_remove_all(text, regex("\\]"))) %>%
  mutate(blank = if_else(text == "", 1, 0)) %>%
  filter(blank == 0) %>%
  select(-blank)

# Number of tweets after filtering out blanks
nrow(tweets_1)

# Clean up the text
tweets_2 <- tweets_1 %>%
  mutate(
    # Remove user names
    text = str_remove_all(text, regex("@[a-zA-Z0-9_]{1,15}")),
    # Remove all ampersands
    text = str_remove_all(text, regex("&amp;")),
    # Remove all unicodes
    text = str_remove_all(text, regex("<U\\+[a-zA-Z0-9]+>")),
    # Retweet code
    text = str_remove_all(text, regex("RT ")),
    # Space and blanks
    text = str_replace_all(text, regex("\\n|\\\\n"), " "),
    # Twitter URLS
    text = str_remove_all(text, regex("https://t.co/[a-zA-Z0-9_]+")),
    # Twitter user slashes
    text = str_remove_all(text, regex("\\\\u[a-zA-Z0-9_]+")),
    # Force text to lower and trim whitespace
    text = str_to_lower(text),
    text = str_trim(text)
  ) %>%
  # Remove references to chicken pox
  mutate(chicken = if_else(str_detect(text, regex("chicken")), 1, 0)) %>%
  filter(chicken == 0) %>%
  select(-chicken)
tweets_2

# Export
write_csv(tweets_2, "data/combined_tweets/tweets.csv")
