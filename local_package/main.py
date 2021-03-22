from ib_insync import *
import numpy as np
import pandas as pd
import logging
import pickle
from config import *


ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)
logger = logging.getLogger(__name__)

class Portfolio:
    def __init__(self,end_date='',duration='1 Y', sample_freq='W-MON'):
        self.stocks = PORTFOLIO.keys()
        self.failed = []
        self.end_date = end_date
        self.duration = duration
        self.sample_freq = sample_freq

    def import_data_from_IB(self, code):
        contract = Stock(code, 'SMART', 'USD')
        contract.primaryExchange = "NASDAQ"
        bars = ib.reqHistoricalData(
         contract, endDateTime='', durationStr=self.duration,
         barSizeSetting='1 day', whatToShow='MIDPOINT', useRTH=True)
        # convert to pandas dataframe:
        df = util.df(bars)
        if df is not None:
            df = df.rename(columns={"close": code}) #close price is used
            df.index=df['date']
            return df[[code]]
        else:
            self.failed.append(code)
            logger.info('-------------------\n "%s" not found in NASDAQ'%(code))
            return pd.DataFrame()

    def import_data_from_yahoo(self):
        pass

    def run(self, save_to=None):
        df = [self.import_data_from_IB(stock) for stock in self.stocks]
        df = pd.concat(df,axis=1)
        df.index = pd.to_datetime(df.index)
        df = df.resample(self.sample_freq).last()
        df = df.pct_change()*100
        df = df.stack(dropna=True).reset_index()
        df.set_index("date",inplace = True)
        df.columns = ['code','pct_chg']
        if save_to is not None:
            df.to_csv(save_to)
        return df



def main():
    p = Portfolio(duration='2 Y')
    # p.run()
    p.run(save_to='data/c.csv')

    # load_porfolio(PORTFOLIO,'','2Y')
    logger.info('-------------------\n session complete')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
