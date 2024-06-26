import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


def Analyze_User_Message(message):
    sid = SentimentIntensityAnalyzer()
    # Analyze sentiment
    sentiment_score = sid.polarity_scores(message)
    compound_score = sentiment_score['compound']

    if compound_score >= 0.05:
        sentiment_label = "Positive"
    elif compound_score <= -0.05:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"

    def scale_to_100(score):
        return (score + 1) * 50  # Scaling to 0-100 range

    # Analyze communication skills
    communication_score = sentiment_score['compound']
    communication_skills = scale_to_100(communication_score)
    communication_skills = int(communication_skills)

    return {
        'sentiment': sentiment_label,
        'communication_skills': communication_skills
    }

sen = "Every day presents new opportunities for growth and learning"
result = Analyze_User_Message(sen)
print(result['communication_skills'])


