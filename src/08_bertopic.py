"""
@author: Cory J Cascalheira
Created: 2022-11-13

The purpose of this script is to generate topic models of the monkeypox conversation among LGBTQ+ people, but using
BERTopic modeling, a method based on the BERT large language model.

The core code is heavily inspired by the following resources:
- https://maartengr.github.io/BERTopic/getting_started/quickstart/quickstart.html

To install BERTopic on Python 3.8.13 MSC v.1916 64 bit (AMD64) on win32, use this resource:
- https://stackoverflow.com/questions/73171473/how-to-resolve-error-could-not-build-wheels-for-hdbscan-which-is-required-to-i

Order of code to execute in anaconda prompt:
- pip install python-dev-tools
- conda install -c conda-forge hdbscan
- pip install bertopic

To download the sentence model, open ChromeDriver 107.0.5304.62 in the background, then execute code. For more details
on sentence models for embedding, see:
- https://www.sbert.net/docs/pretrained_models.html

# To save the interactive plotly visualization
- https://plotly.com/python/interactive-html-export/
"""

#region LIBRARIES AND IMPORT

# Core libraries
import time
import pandas as pd
import pprint

# For interactive plotting
import plotly.express as px

# Topic libraries for modeling
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer

# Import data
mpx = pd.read_csv('data/combined_subreddits/all_subreddits_mpx_data.csv')

# Convert text to list - no need to pre-process since we are using BERT
mpx_docs = mpx['body'].values.tolist()

#endregion

#region BERTOPIC MODELING

# Create an embedding model using sentence transformers
# https://maartengr.github.io/BERTopic/getting_started/embeddings/embeddings.html
sentence_model = SentenceTransformer("all-mpnet-base-v2")

# Initialize the BERT topic model with the sentence embeddings
topic_model = BERTopic(embedding_model=sentence_model)

# Train the topic model
start_time = time.time()
topics, probs = topic_model.fit_transform(mpx_docs)
end_time = time.time()
bt_processing_time = end_time - start_time

# Print the processing time
print('The processing time is: %f' % bt_processing_time)

# Save the BERTopic model
# topic_model.save("data/results/bertopic")

# Take a peak at the topic information
topic_model.get_topic_info()

# Visualize intertopic distance map and export to HTML
vis = topic_model.visualize_topics()
vis.write_html("plots/bertopic/bertopic.html")

# Reduce topics
topic_model.reduce_topics(mpx_docs, nr_topics=15)
topic_model.get_topic_info()

# Remove stop words and create n grams for topic representation
vectorizer_model = CountVectorizer(stop_words="english", ngram_range=(1, 1))
topic_model.update_topics(mpx_docs, vectorizer_model=vectorizer_model)
topic_model.get_topic_info()

# Rename the topics
topic_model.set_topic_labels({-1: "Noise", 0: "MPX Vax Info Sharing", 1: "Intersection Between Gay Men and MPX", 2: "MPX as STD",
                              3: "Gay Men Spread MPX", 4: "Injection Site Symptoms", 5: "MPX Spreads via Skin Contact",
                              6: "Homophobia Concerns", 7: "Expressing Gratitude", 8: "MPX Cases and Testing",
                              9: "MPX Vax Availability", 10: "Vax 2nd Dose", 11: "Visiting the Doctor",
                              12: "COVID-19 References", 13: "Comparing Straight and Gay People",
                              14: "Blame & Fear Mongering"})

# Save the topic results
topic_df = topic_model.get_topic_info()
topic_df['Percent'] = topic_df['Count'] / len(mpx_docs)
topic_df.to_csv("data/results/bertopic.csv")

# Get information for reporting
pprint.pprint(topic_model.representative_docs_)
pprint.pprint(topic_model.topic_representations_)

#endregion

#region DYNAMIC TOPIC MODELING

# Prepare the time component
timestamps = mpx['converted_createdutc'].values.tolist()

# Create topics over time
topics_over_time = topic_model.topics_over_time(mpx_docs, timestamps, nr_bins=20)

# Visualize topics
vis_time = topic_model.visualize_topics_over_time(topics_over_time, custom_labels=True, height=500)
vis_time.write_html("plots/bertopic/bertopic_time.html")

#endregion
