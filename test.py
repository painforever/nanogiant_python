import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

print(analyzer.polarity_scores("Oh my god, you are an idiot, fuck you!"))
