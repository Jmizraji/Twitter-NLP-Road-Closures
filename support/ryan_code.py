import pandas as pd
import twitter
import GetOldTweets3 as got
from api_keys import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET

KEYWORDS = ['hurricane', 'closed', 'road closed',
             'congestion', 'blocked', 'highway',
            'traffic', 'route', 'open',
             'shut down', 'detour', 'evacuation', 'hwy']

api = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN_KEY,
                  access_token_secret=ACCESS_TOKEN_SECRET)

###############################################################################

def get_tweets(top_only, geocode_city, start_date, end_date, max_tweets):
#Getoldtweets3 seems to have broken, so this is modified to use twitter API to grab recent tweets from a geocoded location
    df = pd.DataFrame()

    for i in KEYWORDS:

        search_results = api.GetSearch(term = i ,geocode = geocode_city, result_type='recent', return_json=True, count = 100)
        try:
            text_tweets = pd.DataFrame(search_results['statuses'])['text'].drop_duplicates().values
        except:
            continue

        df2 = pd.DataFrame(
            text_tweets,
            columns=['Text'],
            )

        df = df.append(df2)
        # print(f"Total tweets scraped: {len(df)}")

    return df.drop_duplicates()
###############################################################################
