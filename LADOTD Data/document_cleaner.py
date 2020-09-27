import string
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

PUNCT = set(string.punctuation+'‘’“”')

class DocumentCleaner(BaseEstimator, TransformerMixin):
    
    def __init__(self, special_chars=PUNCT):
        
        self.punct = set(special_chars)

    def fit(self, *kwargs):
        
        return self
    
    def transform(self, documents_raw, *kwargs):
        
        documents_clean = []
        
        for document in documents_raw:
    
            document = document.replace('-', ' ')
            document = document.replace('–', ' ')
            document = document.replace('—', ' ')
            document = document.replace('/', ' ')
            
            document = ''.join([i.lower() for i in document if i not in self.punct])
            document = ' '.join([i.strip() for i in document.split()])
            
            documents_clean.append(document)
            
        return np.array(documents_clean)
    