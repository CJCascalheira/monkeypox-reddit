"""
@author: Cory J Cascalheira
Created: 2022-10-30

The purpose of this script is to generate topic models of the monkeypox conversation among LGBTQ+ people using Reddit
text.

The core code is heavily inspired by the following resources:
- https://www.machinelearningplus.com/nlp/topic-modeling-gensim-python/
- https://radimrehurek.com/gensim/

Issues with importing pyLDAvis.gensim, solved with: https://github.com/bmabey/pyLDAvis/issues/131

Resources for working with spaCy
- https://spacy.io/models
- https://stackoverflow.com/questions/51881089/optimized-lemmitization-method-in-python

# Regular expressions in Python
- https://docs.python.org/3/howto/regex.html
"""

#region LIBRARIES AND IMPORT

# Load core libraries
import numpy as np
import pandas as pd
from pprint import pprint

# Import tool for regular expressions
import re

# Load Gensim libraries
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel

# Initialize spaCy language model
# Must download the spaCy model first in terminal with command: python -m spacy download en_core_web_sm
# May need to restart IDE before loading the spaCy pipeline
import importlib_metadata
import spacy
nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

# Load plotting tools
import pyLDAvis.gensim_models
import matplotlib.pyplot as plt

# Load NLTK stopwords
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words = stopwords.words('english')

# Improve NLTK stopwords
new_stop_words = [re.sub("\'", "", sent) for sent in stop_words]
stop_words.extend(new_stop_words)
stop_words.extend(['ish', 'lol', 'non', 'im', 'like', 'ive', 'cant', 'amp', 'ok', 'gt'])

# Load GSDMM - topic modeling for short texts (i.e., social media)
from gsdmm import MovieGroupProcess

# Import data
mpx = pd.read_csv('data/combined_subreddits/all_subreddits_mpx_data.csv')

#endregion

#region HELPER FUNCTIONS


def transform_to_words(sentences):

    """
    A function that uses Gensim's simple_preprocess(), transforming sentences into tokens of word unit size = 1 and removing
    punctuation in a for loop.

    Parameters
    -----------
    sentences: a list
        A list of text strings to preprocess
    """

    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))


def remove_stopwords(word_list):

    """
    A function to remove stop words with the NLTK stopword data set. Relies on NLTK.

    Parameters
    ----------
    word_list: a list
        A list of words that represent tokens from a list of sentences.
    """
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in word_list]


def make_bigrams(word_list):
    """
    A function to transform a list of words into bigrams if bigrams are detected by gensim. Relies on a bigram model
    created separately (see below). Relies on Gensim.

    Parameters
    ----------
    word_list: a list
        A list of words that represent tokens from a list of sentences.
    """
    return [bigram_mod[doc] for doc in word_list]


def make_trigrams(word_list):
    """
    A function to transform a list of words into trigrams if trigrams are detected by gensim. Relies on a trigram model
    created separately (see below). Relies on Gensim.

    Parameters
    ----------
    word_list: a list
        A list of words that represent tokens from a list of sentences.
    """
    return [trigram_mod[bigram_mod[doc]] for doc in word_list]


def lemmatization(word_list, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV', 'PROPN']):
    """
    A function to lemmatize words in a list. Relies on spaCy functionality.

    Parameters
    ----------
    word_list: a list
        A list of words that represent tokens from a list of sentences.
    allowed_postags: a list
        A list of language units to process.
    """
    # Initialize an empty list
    texts_out = []

    # For everyone word in the word list
    for word in word_list:

        # Process with spaCy to lemmarize
        doc = nlp(" ".join(word))
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])

    # Returns a list of lemmas
    return texts_out


def get_optimal_lda(dictionary, corpus, limit=30, start=2, step=2):
    """
    Execute multiple LDA topic models and computer the perplexity and coherence scores to choose the LDA model with
    the optimal number of topics. Relies on Gensim.

    Parameters
    ----------
    dictionary: Gensim dictionary
    corpus: Gensim corpus
    limit: an integer
        max num of topics
    start: an integer
        number of topics with which to start
    step: an integer
        number of topics by which to increase during each model training iteration

    Returns
    -------
    model_list: a list of LDA topic models
    coherence_values: a list
        coherence values corresponding to the LDA model with respective number of topics
    perplexity_values: a list
        perplexity values corresponding to the LDA model with respective number of topics
    """
    # Initialize empty lists
    model_list = []
    coherence_values = []
    perplexity_values = []

    # For each number of topics
    for num_topics in range(start, limit, step):

        # Train an LDA model with Gensim
        model = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, random_state=100,
                                                update_every=1, chunksize=2000, passes=10, alpha='auto',
                                                per_word_topics=True)

        # Add the trained LDA model to the list
        model_list.append(model)

        # Compute UMass coherence score and add to list  - lower is better
        # https://radimrehurek.com/gensim/models/coherencemodel.html
        # https://www.os3.nl/_media/2017-2018/courses/rp2/p76_report.pdf
        cm = CoherenceModel(model=model, corpus=corpus, coherence='u_mass')
        coherence = cm.get_coherence()
        coherence_values.append(coherence)

        # Compute Perplexity and add to list - lower is better
        perplex = model.log_perplexity(corpus)
        perplexity_values.append(perplex)

    return model_list, coherence_values, perplexity_values

#endregion

#region PREPROCESS THE TEXT

# Convert text to list
mpx_text_original = mpx['body'].values.tolist()

# Remove emails, new line characters, and single quotes
mpx_text = [re.sub('\\S*@\\S*\\s?', '', sent) for sent in mpx_text_original]
mpx_text = [re.sub('\\s+', ' ', sent) for sent in mpx_text]
mpx_text = [re.sub("\'", "", sent) for sent in mpx_text]

# Remove markdown links with multiple words
mpx_text = [re.sub("\\[[\\S\\s]+\\]\\(https:\\/\\/[\\D]+\\)", "", sent) for sent in mpx_text]

# Remove markdown links with single words
mpx_text = [re.sub("\\[\\w+\\]\\(https:\\/\\/[\\D\\d]+\\)", "", sent) for sent in mpx_text]

# Remove urls
mpx_text = [re.sub("https:\\/\\/[\\w\\d\\.\\/\\-\\=]+", "", sent) for sent in mpx_text]

# Transform sentences into words, convert to list
mpx_words = list(transform_to_words(mpx_text))

# Build the bigram and trigram models
bigram = gensim.models.Phrases(mpx_words, min_count=5, threshold=100)
trigram = gensim.models.Phrases(bigram[mpx_words], threshold=100)

# Faster way to get a sentence clubbed as a trigram/bigram
bigram_mod = gensim.models.phrases.Phraser(bigram)
trigram_mod = gensim.models.phrases.Phraser(trigram)

# Remove stop words
mpx_words_nostops = remove_stopwords(mpx_words)

# Form bigrams
mpx_words_bigrams = make_bigrams(mpx_words_nostops)

# Lemmatize the words, keeping nouns, adjectives, verbs, adverbs, and proper nouns
mpx_words_lemma = lemmatization(mpx_words_bigrams)

# Remove any stop words created in lemmatization
mpx_words_cleaned = remove_stopwords(mpx_words_lemma)

#endregion

#region CREATE DICTIONARY AND CORPUS

# Create Dictionary
id2word = corpora.Dictionary(mpx_words_cleaned)

# Create Corpus
texts = mpx_words_cleaned

# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in texts]

#endregion

#region EXECUTE THE TOPIC MODELS WITH VANILLA LDA

# Get the LDA topic model with the optimal number of topics
model_list, coherence_values, perplexity_values = get_optimal_lda(dictionary=id2word, corpus=corpus,
                                                                  limit=30, start=2, step=2)

# Plot the coherence scores
# Set the x-axis valyes
limit = 30
start = 2
step = 2
x = range(start, limit, step)

# Create the plot
plt.figure(figsize=(6, 4), dpi=200)
plt.plot(x, coherence_values)
plt.xlabel("Number of Topics")
plt.ylabel("UMass Coherence Score")
plt.xticks(np.arange(min(x), max(x)+1, 2.0))
plt.axvline(x=10, color='red')
plt.savefig('plots/lda_coherence_plot.png')
plt.show()

# From the plot, the best LDA model is when num_topics == 10
optimal_lda_model = model_list[4]

# Visualize best LDA topic model
# https://stackoverflow.com/questions/41936775/export-pyldavis-graphs-as-standalone-webpage
vis = pyLDAvis.gensim_models.prepare(optimal_lda_model, corpus, id2word)
pyLDAvis.save_html(vis, 'plots/lda.html')

# Get the Reddit post that best represents each topic
# https://radimrehurek.com/gensim/models/ldamodel.html

# Initialize empty lists
lda_output = []
topic_distributions = []

# For each post, get the LDA estimation output
for i in range(len(mpx_text_original)):
    lda_output.append(optimal_lda_model[corpus[i]])

# For each output, select just the topic distribution
for i in range(len(mpx_text_original)):
    topic_distributions.append(lda_output[i][0])

# Initialize empty lists
dominant_topics = []
dominance_strength = []

# For each post, extract the dominant topic from the topic distribution
for i in range(len(mpx_text_original)):

    # Sort the tuple by the topic probability (2nd tuple item), largest to smallest
    # https://www.geeksforgeeks.org/python-program-to-sort-a-list-of-tuples-by-second-item/
    topic_distributions[i].sort(key = lambda x: x[1], reverse=True)

    # Extract the dominant topic
    dominant_topic = topic_distributions[i][0][0]
    dominant_topics.append(dominant_topic)

    # Extract the probability of the dominant topic
    how_dominant = topic_distributions[i][0][1]
    dominance_strength.append(how_dominant)

# Prepare to merge with original dataframe
new_mpx_df = mpx.loc[:, ['author', 'body', 'permalink']]

# Add the dominant topics and strengths
new_mpx_df['dominant_topic'] = dominant_topics
new_mpx_df['topic_probability'] = dominance_strength

# Sort the data frame
new_mpx_df = new_mpx_df.sort_values(by=['dominant_topic', 'topic_probability'], ascending=[True, False])

# Select the 10 most illustrative posts per topic
topics_to_quote = new_mpx_df.groupby('dominant_topic').head(10)

# Save the data frame for easy reading
topics_to_quote.to_csv("data/results/topics_to_quote.csv")

#endregion

#region EXECUTE THE TOPIC MODELS WITH GSDMM

# Get the number of words per post
words_per_post = []

for i in range(len(mpx_words_cleaned)):
    words_per_post.append(len(mpx_words_cleaned[i]))

# Histogram of words per post
plt.hist(x=words_per_post)
plt.show()

# Descriptive statistic of words per post
print(np.mean(words_per_post))
print(np.std(words_per_post))
print(len([num for num in words_per_post if num <= 50]) / len(words_per_post))

#endregion