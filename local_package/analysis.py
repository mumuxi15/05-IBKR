import numpy as np
import pandas as pd
import logging
import pickle
from . import *


def portfolio_change(resample_frequency='W-MON'):
    with open('portfolio.pickle', 'rb') as file:
        df = pickle.load(file)
    df = df.resample(resample_frequency).last()
    df = df.pct_change()*100

    df = df.stack(dropna=True).reset_index()
    df.set_index("date",inplace = True)
    df.columns = ['code','pct_chg']
    return df

def read_porfolio(resample_frequency='W-MON'):
    df = portfolio_change('W-MON')
    df.to_csv('data/b.csv')

def main():
    df = read_porfolio()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
