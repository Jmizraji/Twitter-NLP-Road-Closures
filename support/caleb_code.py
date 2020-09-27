import pickle
import spacy
import pandas as pd

CLOSE_MODEL_NAME = '../models/tweets_ada_model.p'
PATH = './support/'

###############################################################################

class RoadFinder:

    def __init__(self, nlp):

        self.nlp = nlp

    def get_docs(self, df):

        new_df = df.copy()
        len_df = len(df)
        docs = []

        count = 0

        for text in df['Text']:
            try:
                doc = self.nlp(text.lower())
            except:
                doc = []

            count += 1
            if count % 1000 == 0:
                #print(f'nlp progress: {round(100.0 * count / len_df, 1)}%')
                pass

            docs.append(doc)

        new_df['docs'] = docs

        return new_df

    def find_matches(self, df):

        new_df = df.copy()

        to_keep = []

        for doc in new_df['docs']:

            if doc == []:
                to_keep.append(False)
                continue

            keep = False

            for ent in doc.ents:
                e = ent.label_
                if(e == "street" or e == 'highway' or e == 'exit'):
                    keep = True
                    continue

            to_keep.append(keep)

        return new_df[to_keep]

    def make_street_cols(self, df):

        new_df = df.copy()

        streets = []
        highways = []
        exits = []
        markers = []

        for doc in df['docs']:
            doc_streets = []
            doc_highways = []
            doc_exits = []
            doc_markers = []

            if(doc != []):
                for ent in doc.ents:
                    if(ent.label_ == 'street'):
                        doc_streets.append(ent.text)
                    elif(ent.label_ == 'highway'):
                        doc_highways.append(ent.text)
                    elif(ent.label_ == 'exit'):
                        doc_exits.append(ent.text)
                    elif(ent.label_ == 'marker'):
                        doc_markers.append(ent.text)

            streets.append(doc_streets)
            highways.append(doc_highways)
            exits.append(doc_exits)
            markers.append(doc_markers)

        new_df['streets'] = streets
        new_df['highways'] = highways
        new_df['exits'] = exits
        new_df['markers'] = markers

        return new_df

    def get_roads_df(self, df):

        new_df = df.drop_duplicates().copy()
        new_df = self.get_docs(new_df)
        new_df = self.find_matches(new_df)
        new_df = self.make_street_cols(new_df)

        return new_df

###############################################################################

def add_closure_predictions(df):

    tweets = df.copy(deep=True)
    model = pickle.load(open(PATH + CLOSE_MODEL_NAME, 'rb'))

    tweets['road_closed'] = model.predict(df['Text'])
    tweets = tweets[tweets['road_closed'] == 1][['Text', 'streets', 'highways', 'exits', 'markers']]

    return tweets

###############################################################################
