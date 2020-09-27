import pickle
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

URL = 'http://wwwapps.dotd.la.gov/administration/announcements/home.aspx?type=roadandlaneclosure'
MODEL_NAME = './closed_clf.pkl'
TABLE_NAME = 'gvAnnouncements'

###

class DOTAlerts:
    
    def __init__(self):
                
        with open(MODEL_NAME, 'rb') as f:
            self.model = pickle.load(f)
            
        self.source = URL
        self.req = requests.get(URL)
        assert 200 <= self.req.status_code < 300
        
        self.soup = BeautifulSoup(self.req.content, 'lxml')
            
    def scrape(self, date=None, lim=100, return_status=True):
        
        if date is None:
            date = str(datetime.now()).split()[0]
            self.date = pd.to_datetime(date)
        else:
            self.date = pd.to_datetime(date)        
        
        reports = []
        table = self.soup.find('table', attrs={'id': TABLE_NAME})
        
        count = 1
        for row in table.find_all('tr')[1:]:

            info = row.text.strip().split('\n')

            alert_date = pd.to_datetime(info[0])
            alert_text = str(info[1])
                    
            if alert_date > self.date:
                continue
            elif alert_date < self.date:
                break
                
            if alert_text == 'x':
                continue
            
            report = {}
            report['date'] = alert_date
            report['report'] = alert_text
            
            if return_status:
                report['closed'] = self.is_closed(alert_text)
            
            reports.append(report)
            
            if count < lim:
                count += 1
            else:
                break
            
        self.reports = pd.DataFrame(reports)
        return self.reports
    
    def is_closed(self, report):
    
        return self.model.predict([report])[0]
    
        #return 0 if 'open' in report.lower() else 1    
