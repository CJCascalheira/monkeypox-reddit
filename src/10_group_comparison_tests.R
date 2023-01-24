# COMPARE PSYCHOLINGUISTIC ATTRIBUTES -------------------------------------

# @author Cory J. Cascalheira
# Created: 2022-01-04

# This file uses group comparison tests to compare Reddit vs Twitter group
# differences in psycholinguistic attributes.

# LOAD AND IMPORT ---------------------------------------------------------

# Load dependencies
library(tidyverse)
library(lsr)
library(janitor)
library(tidytext)
library(stopwords)

# Import data - MPX data set for Twitter
tweets <- read_csv("data/combined_tweets/tweets_liwc.csv")
nrow(tweets)

# Import data - MPX data set for Reddit
reddit <- read_csv("data/combined_subreddits/all_subreddits_mpx_data_liwc_features.csv") %>%
  rename(text = body...2, body = body...65, time_created = converted_createdutc) %>%
  # Remove unnecessary columns
  select(-author, -created_utc, -retrieved_utc, -permalink, -link_id, -parent_id,
         -contains_epoxy_term, -contains_monkeypox_term) %>%
  # Add temporary id variables
  mutate(temp_id = 1:nrow(.)) %>%
  select(temp_id, subreddit, time_created, everything())
nrow(reddit)

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

# PREPROCESS DATA ---------------------------------------------------------

# General preprocessing of the LIWC data for MPX data set
liwc_tweets <- tweets %>%
  # Make long format
  pivot_longer(cols = WC:OtherP, names_to = "liwc_names", values_to = "liwc_values") %>%
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
  ) %>%
  # Remove links / URLs
  mutate(text = str_remove_all(text, " ?(f|ht)tp(s?)://(.*)[.][a-z]+")) %>%
  # Replace whitespace characters
  mutate(text = str_replace_all(text, "\r\n\r\n", " ")) %>%
  mutate(text = str_replace_all(text, "\n", " ")) %>%
  # Remove strange characters
  mutate(text = str_remove_all(text, "&amp;#x200B;|â€¦|&lt;|&gt;|â€œ|ðŸ¥´|ðŸ¥²|â„¢|ðŸ¤·â€|â™€ï¸|â€™|â€|&gt;|Ã©||ðŸ™|ðŸŒˆ|ðŸ")) %>%
  # Recode characters
  mutate(text = recode(text, "&amp;" = "and", "Â´" = "'", "â€™" = "'")) %>%
  # Lowercase format
  mutate(text = str_to_lower(text))

# Get text for descriptive statistics
descriptives_tweets <- liwc_tweets %>%
  select(temp_id, text, liwc_names, liwc_values) %>%
  filter(liwc_names == "WC")

# Add grouping variable
liwc_tweets <- liwc_tweets %>%
  mutate(group = "twitter") %>%
  select(group, liwc_names, liwc_values, liwc_categories)

# General preprocessing of the LIWC data for MPX data set
liwc_reddit <- reddit %>%
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
  ) %>%
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
  mutate(text = str_to_lower(text))
liwc_reddit

# Get text for descriptive statistics
descriptives_reddit <- liwc_reddit %>%
  select(temp_id, text, liwc_names, liwc_values) %>%
  filter(liwc_names == "WC")

# Add grouping variable
liwc_reddit <- liwc_reddit %>%
  mutate(group = "reddit") %>%
  select(group, liwc_names, liwc_values, liwc_categories)

# Combine the datasets
social_media_liwc <- bind_rows(liwc_tweets, liwc_reddit) %>%
  # Remove variables that are not in major categories
  filter(!liwc_categories %in% c("Summary", "Grammar", "Linguistic")) %>%
  filter(!liwc_names %in% c("WC", "Exclam", "AllPunc", "Colon", "Apostro", "Comma", 
                            "Period", "SemiC", "Dash", "Parenth", "OtherP", "Quote"))
print(social_media_liwc)

# Number of features used
social_media_liwc %>%
  distinct(liwc_names)

# DESCRIPTIVE STATISTICS --------------------------------------------------

# BEFORE PREPROCESSING - RAW DATA -----------------------------------------

# Word characters
descriptives_tweets %>%
  summarize(
    mean = mean(liwc_values),
    sd = sd(liwc_values),
    median = median(liwc_values),
    min = min(liwc_values),
    max = max(liwc_values)
  )

descriptives_reddit %>%
  summarize(
    mean = mean(liwc_values),
    sd = sd(liwc_values),
    median = median(liwc_values),
    min = min(liwc_values),
    max = max(liwc_values)
  )
  
# AFTER PREPROCESSING - CLEANED DATA -------------------------------------

# Remove stop words from Twitter data
cleaned_tweets <- descriptives_tweets %>%
  # Unnest words
  unnest_tokens(output = "word", input = "text") %>%
  # Remove stopwords
  filter(!(word %in% all_stopwords)) %>%
  # Remove non American standard code (i.e., unicode characters)
  mutate(word = iconv(word, "latin1", "ASCII", sub = "")) %>%
  filter(word != "")

# Remove stop words from Reddit data
cleaned_reddit <- descriptives_reddit %>%
  # Unnest words
  unnest_tokens(output = "word", input = "text") %>%
  # Remove stopwords
  filter(!(word %in% all_stopwords)) %>%
  # Remove non American standard code (i.e., unicode characters)
  mutate(word = iconv(word, "latin1", "ASCII", sub = "")) %>%
  filter(word != "")

# Word characters
cleaned_tweets %>%
  count(temp_id) %>%
  summarize(
    mean = mean(n),
    sd = sd(n),
    median = median(n),
    min = min(n),
    max = max(n)
  )

cleaned_reddit %>%
  count(temp_id) %>%
  summarize(
    mean = mean(n),
    sd = sd(n),
    median = median(n),
    min = min(n),
    max = max(n)
  )

# MULTIPLE T-TESTS --------------------------------------------------------

# Execute the independent samples t-tests w/o variance equality assumption
test_results <- lapply(split(social_media_liwc, social_media_liwc$liwc_names), 
       function(x) t.test(liwc_values~group, x))
print(test_results)

# Bonferroni correction value
bonf_value <- 0.05 / length(names(test_results))

# Extract data from list into df, next few lines

# Prepare vectors
t_stat <- c()
p_val <- c()
deg_free <- c()

# For loop to extract data
for (i in 1:length(names(test_results))) {
  t_stat <- c(t_stat, test_results[[i]]$statistic)
  p_val <- c(p_val, test_results[[i]]$p.value)
  deg_free <- c(deg_free, test_results[[i]]$parameter)
}

# Effect size using Cohen's D
# https://rcompanion.org/handbook/I_03.html
effect_sizes <- lapply(split(social_media_liwc, social_media_liwc$liwc_names), 
       function(x) cohensD(liwc_values~group, x)) %>%
  as_vector()

# Get LIWC vars names
liwc_names <- names(test_results)

# Add all vectors into df
test_signf_results <- data.frame(liwc_names, t_stat, deg_free, effect_sizes, p_val) %>%
  as_tibble() %>%
  # Set Bonferroni value and determine if p_val is beyond/more extreme
  mutate(bonf_value = bonf_value) %>%
  mutate(signf_at_bonf = p_val < bonf_value) %>%
  # Keep only significant differences
  filter(signf_at_bonf == TRUE)
test_signf_results

# Add LIWC categories
test_signf_results1 <- social_media_liwc %>%
  select(liwc_categories, liwc_names) %>%
  distinct(liwc_names, .keep_all = TRUE) %>%
  right_join(test_signf_results) %>% 
  # Round values
  mutate(
    t_stat = round(t_stat, 3),
    effect_sizes = round(effect_sizes, 3)
  ) %>%
  arrange(liwc_categories, desc(effect_sizes))
test_signf_results1

# Save data to csv
write_csv(test_signf_results1, "data/results/significance_tests.csv")
