import nltk
import re
from nltk.tokenize import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from collections import Counter
nltk.download('wordnet')      #download if using this module for the first time


from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
nltk.download('stopwords')     #download if using this module for the first time
nltk.download('punkt')         #download if using this module for the first time
nltk.download('vader_lexicon') #download if using this module for the first time

#For Gensim
import gensim
import string
from gensim import corpora
from gensim.corpora.dictionary import Dictionary
from nltk.tokenize import word_tokenize


class TopicGenerator:
    def __init__(self):
        self.feed_backs = []
        self.stopwords = set(stopwords.words('english'))
        self.exclude = set(string.punctuation)
        self.lemma = WordNetLemmatizer()
        self.analyzer = SentimentIntensityAnalyzer()
    def make_topics(self, feed_backs):
        self.feed_backs = feed_backs
        final_doc = [self.clean(document).split() for document in self.feed_backs]

        dictionary = corpora.Dictionary(final_doc)
        DT_matrix = [dictionary.doc2bow(doc) for doc in final_doc]
        Lda_object = gensim.models.ldamodel.LdaModel
        lda_model = Lda_object(DT_matrix, num_topics=10, id2word=dictionary)
        topics = lda_model.print_topics(num_topics=10, num_words=10)
        #print(map(list, topics))
        return topics

    def generate_topic_sentences(self, topics):
        sentences = []
        for topic in topics:
            words = re.findall(r'[a-zA-Z]+', topic[1])
            if len(words) > 0: sentences.append(', '.join(words))
        print(sentences)
        return sentences


    def clean(self, document):
        stopwordremoval = " ".join([i for i in document.lower().split() if i not in self.stopwords])
        punctuationremoval = ''.join(ch for ch in stopwordremoval if ch not in self.exclude)
        normalized = " ".join(self.lemma.lemmatize(word) for word in punctuationremoval.split())
        return normalized

    def sentiment_helper(self, polarity_score):
        if polarity_score['compound'] >= 0.05: return 'positive'
        elif polarity_score['compound'] > -0.05 and polarity_score['compound'] < 0.05: return 'neutral'
        elif polarity_score['compound'] <= -0.05: return 'negative'