import os
import time
import gmplot
import requests
import numpy as np
import pandas as pd

from api_keys import HERE_API_KEY, GOOGLE_API_KEY

MAP_FILE = 'map.html'
QUERY_SCORE_THRESH = 0.6
ZOOM = 9
RADIUS = 25

###############################################################################

def query_string(tweets):
    """Create the query string"""

    # take streets, highways, exits, and markers and put them in one column
    tweets['query'] = tweets['streets'] + tweets['highways'] + tweets['exits'] + tweets['markers']

    # format string
    tweets['query'] = [str(val).replace('[]','') for val in tweets['query'].values]
    tweets['query'] = [str(val).replace('][',',') for val in tweets['query'].values]
    tweets['query'] = [str(val).replace(']','') for val in tweets['query'].values]
    tweets['query'] = [str(val).replace('[','') for val in tweets['query'].values]

    query = []

    # url encode the column
    for val in tweets['query']:
        val = val.replace(',','%2C+')
        val = val.replace(' ','+')
        val = val.replace("'",'')
        val = val.replace("",'')
        s = ''.join(val)
        query.append(s)

    return query

###############################################################################

def get_lat_lng(df, state):
    """Get the lat and lng from the dataframe. There must be a 'query_string' column in the data frame"""

    lat, lng = [], []
    query_score = []
    field_score = []

    for row in df['query_string']:

        res=requests.get( # create the api get request
            'https://geocode.search.hereapi.com/v1/geocode?q=' + \
            row + '&qq=state='+ state + '&apiKey=' + HERE_API_KEY
            )

        time.sleep(1) # add a sleep to not hit servers too hard
        json = res.json() # extract json

        # if no value is returned, just put 0.0
        try:
            # append to lat
            lat.append(json['items'][0]['position']['lat'])

            # append to long
            lng.append(json['items'][0]['position']['lng'])

            # append to query_score
            query_score.append(json['items'][0]['scoring']['queryScore'])

            # append to field_score
            field_score.append(json['items'][0]['scoring']['fieldScore'])

        except IndexError:
            # append to lat
            lat.append(0.0)

            # append to long
            lng.append(0.0)

            # append to query_score
            query_score.append(0.0)

            # append to field_score
            field_score.append(0.0)

        except KeyError:
            # append to lat
            lat.append(0.0)

            # append to long
            lng.append(0.0)

            # append to query_score
            query_score.append(0.0)

            # append to field_score
            field_score.append(0.0)

    # add columns to the dataframe
    df['lat'] = lat
    df['lng'] = lng
    df['query_score'] = query_score
    df['field_score'] = field_score

    return df

###############################################################################

def map_plotter(df_full):
    """Create file for map"""
    # Only plot points with a score above 0.6
    df = df_full[df_full['query_score'] >= QUERY_SCORE_THRESH].copy(deep=True)
    # Set the points:
    lat = tuple(df['lat'].values)
    lng = tuple(df['lng'].values)
    # Create the map plotter:
    gmap = gmplot.GoogleMapPlotter(df['lat'].mean(), df['lng'].mean(), ZOOM, apikey=GOOGLE_API_KEY)
    for point in range(0,len(lat)):
        gmap.marker(
            lat[point],
            lng[point],
            color='orangered',
            info_window=f"<p>{[tweet for tweet in df['Text']][point]}</p>",
            )
    gmap.heatmap(lat,lng,
                 radius=RADIUS,
                 gradient=[(0, 0, 255, 0), (0, 255, 0, 0.9), (255, 0, 0, 1)])
    # # Plot the points
    # gmap.scatter(lat, lng,
    #              color='#3B0B39',
    #              size=150,
    #              marker=False, #adjust styling of markers and points on the map
    #              title=[tweet for tweet in df['Text']])  #create a list of each tweet so that tweet displays when you hover
    # Create the map:

    gmap.draw(MAP_FILE)

    return MAP_FILE

###############################################################################
