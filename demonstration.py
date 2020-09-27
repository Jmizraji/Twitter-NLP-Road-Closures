import os
import sys
import gmplot
import pickle
import warnings
import pandas as pd
from datetime import datetime

warnings.simplefilter('ignore')

sys.path.append(
    os.path.join(
        os.getcwd(),
        'support',
        )
    )

from api_keys import GOOGLE_API_KEY
from josh_code import query_string, get_lat_lng, map_plotter
from caleb_code import RoadFinder, add_closure_predictions
from ryan_code import get_tweets

PATH = './support/'
MODEL_PATH = './models/'
NLP_MODEL = 'tweet_nlp.p'
MAX_TWEETS = 1000

###############################################################################

def main():

    ## Get user input

    while True:
        user_city = input('Enter City, State: ')
        try:
            assert ',' in user_city
            break
        except AssertionError:
            print('Please separate city and state with comma')

    state = user_city.split(',')[-1]
    date = str(datetime.now()).split()[0]

    ## From ryan_code
    location = gmplot.GoogleMapPlotter.geocode(user_city, apikey=GOOGLE_API_KEY)
    tweets_dataframe = get_tweets(
         top_only=False,
         geocode_city=(location[0], location[1], '10mi'),
         start_date=date,
         end_date=date,
         max_tweets=MAX_TWEETS,
        )

    #tweets_dataframe = pd.read_csv(PATH + 'lake_ch_tweets.csv')
    if len(tweets_dataframe) > 500:
        tweets_dataframe = tweets_dataframe.sample(n = 500)

    ## From caleb_code

    nlp = pickle.load(open(MODEL_PATH + NLP_MODEL, 'rb'))
    rf = RoadFinder(nlp)

    tweets = rf.get_roads_df(tweets_dataframe)
    tweets = add_closure_predictions(tweets)

    ## From josh_code

    tweets['query_string'] = query_string(tweets)
    tweets_with_geo = get_lat_lng(tweets, state)

    map_name = map_plotter(tweets_with_geo)
    os.system(f'start {map_name}')


###############################################################################

if __name__ == '__main__':
    main()
