from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze(text: str) -> str:
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.5:
        return "positive"
    elif compound >= 0.1:
        return "neutral"
    elif compound >= -0.3:
        return "controversial"
    elif compound >= -0.6:
        return "chaos"
    else:
        return "chaos"