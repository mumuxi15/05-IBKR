import yfinance
from datetime import datetime
import numpy as np
import pandas as pd
import logging
import pickle
from config import *

logger = logging.getLogger(__name__)


class Portfolio(object):
    def __init__(self, start_date="2011-01-01", end_date=None):
        self.stocks = PORTFOLIO.keys()
        self.start_date = start_date
        if end_date is None:
            self.end_date = datetime.today().strftime("%Y-%m-%d")
        else:
            self.end_date = end_date

    def __str__(self):
        print ('Portfolio consists of ')
        for k,v in PORTFOLIO.items():
            print ('%s: %d'%(k,v))

    def import_data_from_yahoo(self, code):
        # 30-day rolling std
        df = yfinance.download(code,self.start_date,self.end_date)
        df = df.rename(columns={"Adj Close": code})
        df['std'] = df[code].pct_change().rolling(30).std()
        df['code'] = code
        df.index.name = 'date'
        return df[['code',code,'std']].round(5)

    #
    # def run(self,save_to=None):
    #     self.import_data_from_yahoo('ADBE')
    #     self.import_data_from_yahoo('AMZN')

    def run(self, save_to=None):
        df = [self.import_data_from_yahoo(stock) for stock in self.stocks]
        df = pd.concat(df,axis=1)
        if save_to is not None:
            df.to_csv(save_to)
        return



def main():
    p = Portfolio()
    p.run('data/yahoo.csv')
    logger.info('-------------------\nSession complete')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
