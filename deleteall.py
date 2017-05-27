import tweepy

auth = tweepy.OAuthHandler('vBRGejyUwo4SODXHBKuA8Q7oE',
        'NIncJA2K07omhlVl14CHJtsvMiaGoGwo2nDzdfMCpuQCfAifQD')
auth.set_access_token('860453090696343552-VXXxo95CWAoE4zfbpo0Q4zdQbbxJ0r4',
        'qZ6LtE7TcB6yLxniSTm9kHrW5PghRu6Yxx26zT5SQzA9V')

api = tweepy.API(auth)

public_tweets = api.user_timeline()
for tweet in public_tweets:
    api.destroy_status(tweet.id)
