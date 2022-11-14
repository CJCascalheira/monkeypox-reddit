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
library(ggridges)
library(tidytext)
library(stopwords)

# Import data - MPX data set
mpx <- read_csv("data/combined_subreddits/all_subreddits_mpx_data_liwc_features.csv") %>%
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
virus <- read_csv("data/combined_subreddits/all_subreddits_virus_data_liwc_features.csv") %>%
  rename(text = body...2, body = body...65, time_created = converted_createdutc) %>%
  # Remove unnecessary columns
  select(-author, -created_utc, -retrieved_utc, -permalink, -link_id, -parent_id,
         -contains_monkeypox_term, -contains_virus_term) %>%
  # Convert to date
  mutate(time_created = dmy_hm(time_created)) %>%
  # Add temporary id variables
  mutate(temp_id = 1:nrow(.)) %>%
  select(temp_id, subreddit, time_created, everything())

# Get sentiments
afinn <- get_sentiments("afinn")

# Get slangSD: https://github.com/airtonbjunior/opinionMining/blob/master/dictionaries/slangSD.txt
slangsd <- read_delim("data/utility/slangSD.txt", delim = "\t", col_names = FALSE) %>%
  rename(word = X1, value = X2)

# Combine sentiment libraries
sentiment_df <- bind_rows(afinn, slangsd) %>%
  distinct(word, .keep_all = TRUE)

# Get all the stop words
all_stopwords <- c(stopwords(source = "snowball"), stopwords(source = "stopwords-iso"), 
                  stopwords(source = "smart"), stopwords(source = "marimo"), stopwords(source = "nltk"))

# DEFINE FUNCTIONS --------------------------------------------------------

# Min-max normalization for features
scale_this <- function(x){
  (x - min(x)) / (max(x) - min(x))
}

# PREPROCESS DATA ---------------------------------------------------------

# General preprocessing of the LIWC data for MPX data set
mpx_liwc <- mpx %>%==_+++
  # Make long format
  pivot_longer(cols = WC:OtherP, names_to = "liwc_names", values_to = "liwc_values") %>%
  # Min-max normalize feature values
  #group_by(liwc_names) %>%
  #mutate(liwc_values = scale_this(liwc_values)) %>%
  #ungroup() %>%
  # Add LIWC categories
  mutate(
    liwc_categories = if_else(liwc_names %in% c("Analytic", "Clout", "Authentic", 
                                                "Tone", "WPS", "Sixltr", "Dic"), 
                              "Summary", "None"),
    liwc_categories = if_else(liwc_names %in% c("function", "pronoun", "ppron", "i", "we", "you",
                                                "shehe", "they", "ipron", "article", "prep",
                                                "auxverb", "adverb", "conj", "negate"), 
                              "Linguistic", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c("verb", "adj", "compare", "interrog", "numbers",
                                                "quant"), 
                              "Grammar", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c("affect", "posemo", "negemo", "anx", "anger", "sad"), 
                              "Affect", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c("social", "family", "friend", "female", "male"), 
                              "Social", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c("cogproc", "insight", "cause", "discrep", "tentat", "certain",
                                                "differ"), 
                              "Cognitive", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c("percept", "see", "hear", "feel"), 
                              "Perceptual", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c("bio", "body", "health", "sexual", "ingest"), 
                              "Biological", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c("drives", "affiliation", "achieve", "power", "reward", "risk"), 
                              "Drives", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c("TimeOrient", "focuspast", "focuspresent", "focusfuture"), 
                              "Time Orientation", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c("relativ", "motion", "space", "time"), 
                              "Relativity", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c("work", "leisure", "home", "money", "relig", "death"), 
                              "Personal Concerns", liwc_categories),
    liwc_categories = if_else(liwc_names %in% c("informal", "swear", "netspeak", "assent", "nonflu", "filler"), 
                              "Informal Language", liwc_categories)
  )
mpx_liwc

# General preprocessing of text
mpx_tokens <- mpx %>%
  # Remove links / URLs
  mutate(text = str_remove_all(text, " ?(f|ht)tp(s?)://(.*)[.][a-z]+")) %>%
  # Remove markdown links
  mutate(text = str_remove_all(text, "\\[.*\\]\\(.*\\)")) %>%
  # Replace whitespace characters
  mutate(text = str_replace_all(text, "\r\n\r\n", " ")) %>%
  mutate(text = str_replace_all(text, "\n", " ")) %>%
  # Remove strange characters
  mutate(text = str_remove_all(text, "&amp;#x200B;|â€¦|&lt;|&gt;|â€œ|ðŸ¥´|ðŸ¥²|â„¢|ðŸ¤·â€|â™€ï¸|â€™|â€|&gt;|Ã©||ðŸ™|ðŸŒˆ|ðŸ")) %>%
  # Recode characters
  mutate(text = recode(text, "&amp;" = "and", "Â´" = "'", "â€™" = "'")) %>%
  # Lowercase format
  mutate(text = str_to_lower(text)) %>%
  unnest_tokens(output = "word", input = "text") %>%
  # Remove stopwords
  filter(!(word %in% all_stopwords))

# Get sentiment of each token
mpx_sentiment <- mpx_tokens %>%
  # Get sentiment of words
  left_join(sentiment_df) %>%
  # Recode missing to 0 sentiment
  mutate(value = if_else(is.na(value), 0, value)) %>%
  # Select the main variables
  select(temp_id, time_created, sentiment = value) %>%
  mutate(sentiment = if_else(sentiment < 0, "negative", if_else(sentiment == 0, "neutral", "positive")))

# CONVERSATION VOLUME OVER TIME -------------------------------------------

# For week to date conversion, see:
# https://www.epochconverter.com/weeks/2021

# MPX conversation volume over time
mpx_conversation_rate <- mpx %>%
  # Group time by week
  mutate(time_week = week(time_created)) %>%
  # Number of posts per week
  count(time_week) %>%
  # Set variables for plot and create line plot
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
  # Adjust axes, add labels, adjust theme
  scale_y_continuous(breaks = pretty_breaks(n = 15), labels = comma) +
  scale_x_continuous(breaks = c(21, 25, 29, 33, 37, 41), 
                     labels = c("21" = "May", "25" = "June", "29" = "July", "33" = "August", 
                                "37" = "September", "41" = "October")) +
  labs(x = "Months in 2022", y = "Number of MPX-Related Posts and Comments") +
  theme_bw() +
  theme(axis.text.x = element_text(size = 10),
        axis.text.y = element_text(size = 10),
        legend.text=element_text(size = 10))
mpx_conversation_rate

# Save plot
ggsave(filename = "plots/mpx_conversation_rate.png", plot = mpx_conversation_rate,
       width = 10, height = 5)

# LIWC FEATURES OVER TIME -------------------------------------------------

# Major psychological foci over time
mpx_psychological_focus_by_time <- mpx_liwc %>%
  # Transform data into weeks
  mutate(time_week = week(time_created)) %>%
  group_by(time_week, liwc_names) %>%
  # Average psychological focus per week
  summarize(
    total_values = mean(liwc_values)
  ) %>%
  ungroup() %>%
  # Select the psychological foci
  filter(liwc_names %in% c("social", "cogproc", "percept", "bio", "drives")) %>%
  # Organize the legend by most common psychological foci
  mutate(liwc_names = factor(liwc_names, levels = c("cogproc", "social", "drives", "bio", "percept"))) %>%
  # Change names of liwc variables
  mutate(liwc_names = recode(liwc_names, "cogproc" = "Cognitive", "social" = "Social", "drives" = "Drives", 
                             "bio" = "Biological", "percept" = "Perceptual")) %>%
  # Specify the variables for the graph and plot
  ggplot(aes(x = time_week, y = total_values, group = liwc_names, color = liwc_names)) +
  geom_line(size = 1) + 
  # Adjust the axes, change colors and theme
  scale_y_continuous(breaks = pretty_breaks(n = 10), limits = c(0, 16)) +
  scale_x_continuous(breaks = c(21, 25, 29, 33, 37, 41), 
                     labels = c("21" = "May", "25" = "June", "29" = "July", "33" = "August", 
                                "37" = "September", "41" = "October")) +
  scale_color_viridis_d() +
  labs(x = "Months in 2022", y = "Average Expression of Psychological Focus", 
       color = "Psychological\nFocus") +
  theme_bw() +
  theme(axis.text.x = element_text(size = 10),
        axis.text.y = element_text(size = 10),
        legend.text=element_text(size = 10))
mpx_psychological_focus_by_time

# Save plot
ggsave(filename = "plots/mpx_psychological_focus_by_time.png", plot = mpx_psychological_focus_by_time,
       width = 10, height = 5)

# SENTIMENT OVERTIME ------------------------------------------------------

# Plot of overall sentiment over time
mpx_sentiment_over_time <- mpx_sentiment %>%
  # Transform data into weeks
  mutate(time_week = week(time_created)) %>%
  count(time_week, sentiment) %>%
  # Organize the legend by most common sentiment
  mutate(sentiment = factor(sentiment, levels = c("neutral", "negative", "positive"))) %>%
  # Change names of variables
  mutate(sentiment = recode(sentiment, "neutral" = "Neutral", "negative" = "Negative", 
                             "positive" = "Positive")) %>%
  # Specify variables and create line plot
  ggplot(aes(x = time_week, y = n, group = sentiment, color = sentiment)) +
  geom_line(size = 1.5) +
  # Adjust the axes, change colors and theme
  scale_y_continuous(breaks = pretty_breaks(n = 10), labels = comma) +
  scale_x_continuous(breaks = c(21, 25, 29, 33, 37, 41), 
                     labels = c("21" = "May", "25" = "June", "29" = "July", "33" = "August", 
                                "37" = "September", "41" = "October")) +
  scale_color_discrete(type = c("cadetblue3", "darkblue", "dodgerblue")) +
  labs(x = "Months in 2022", y = "Number of Words", 
       color = "Sentiment") +
  theme_bw() +
  theme(axis.text.x = element_text(size = 10),
        axis.text.y = element_text(size = 10),
        legend.text=element_text(size = 10))
mpx_sentiment_over_time

# Save plot
ggsave(filename = "plots/mpx_sentiment_over_time.png", plot = mpx_sentiment_over_time,
       width = 10, height = 5)
