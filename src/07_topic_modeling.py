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
import pyLDAvis
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

#endregion

#region PREPROCESS THE TEXT

# Convert text to list
mpx_text = mpx['body'].values.tolist()

# Remove emails, new line characters, and single quotes
mpx_text = [re.sub('\\S*@\\S*\\s?', '', sent) for sent in mpx_text]
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

#region EXECUTE THE TOPIC MODELS WITH LDA

# Build LDA model, num_topics = 10
lda_10 = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=id2word, num_topics=10, random_state=100,
                                         update_every=1, chunksize=2000, passes=10, alpha='auto', per_word_topics=True)

# Compute Perplexity - lower is better
print('\nPerplexity: ', lda_10.log_perplexity(corpus))

# Compute Coherence Score - higher is better
# https://radimrehurek.com/gensim/models/coherencemodel.html
cm = CoherenceModel(model=lda_10, corpus=corpus, coherence='u_mass')
coherence = cm.get_coherence()
print('\nCoherence Score: ', coherence)

#endregion

#region VISUALIZE BEST TOPIC MODEL AND INTERPRET

# Visualize best LDA topic model
# https://stackoverflow.com/questions/41936775/export-pyldavis-graphs-as-standalone-webpage
vis = pyLDAvis.gensim_models.prepare(lda10, corpus, id2word)
pyLDAvis.save_html(vis, 'plots/lda.html')

#endregion
