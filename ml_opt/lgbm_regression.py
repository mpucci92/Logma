import pandas as pd
import numpy as np
import sys, os

from sklearn.model_selection import ParameterGrid
from sklearn.model_selection import StratifiedKFold

import lightgbm as lgbm
from sklearn.metrics import accuracy_score

import joblib
from joblib import delayed, Parallel

def evalerror(labels, preds):
    preds[preds > 0.5] = 1
    preds[preds <= 0.5] = 0
    return 'accuracy', accuracy_score(preds, labels), True

dir_ = 'res'
k = 100
train_pct = 0.5

def get_main_df():

    main = []

    for file in os.listdir('D:/AlgoMLData/Scaled/'):
        print(file)
        ticker = file.split('_')[0]
        df = pd.read_csv('D:/AlgoMLData/Scaled/{}'.format(file))
        df['Ticker'] = ticker
        main.append(df)

    main = pd.concat(main, axis=0).iloc[:, 1:].reset_index(drop=True)

    main = main[(main.sig30 == 1) & (main.sig50 == 1)]

    main.TTC = main.TTC.values + 4 + (np.random.randint(0, 5, size=main.shape[0]) - 4)

    main.TTC = 120 - main.TTC

    return main

def get_splits(main):

    test_pct = 1 - train_pct

    idc = np.random.permutation(main.shape[0])
    train_len = int(train_pct * main.shape[0])

    print(main.shape)

    train = main.iloc[idc[:train_len], :]
    test = main.iloc[idc[train_len:], :]

    train_tickers = train.Ticker.values
    train_drawdowns = train.Drawdown.values
    train_directions = train.Direction.values
    y_train = train.TTC.values
    idx = train.columns.tolist().index('sig20')-1
    X_train = train.iloc[:, idx:-1]

    test_tickers = test.Ticker.values
    test_drawdown = test.Drawdown.values
    test_directions = test.Direction.values
    y_test = test.TTC.values
    idx = test.columns.tolist().index('sig20')-1
    X_test = test.iloc[:, idx:-1]

    return X_train, y_train, X_test, y_test

def eval_params(X_train, y_train, params, i):

    print(params)
    dataset = lgbm.Dataset(X_train, label=y_train)
    results = lgbm.cv(params, train_set=dataset, early_stopping_rounds=10)
    with open('res/results_{}'.format(i), 'wb') as file:
        joblib.dump([params, results], file)

if __name__ == '__main__':

    np.random.seed(73)

    main = get_main_df()
    X_train, y_train, X_test, y_test = get_splits(main)

    params = {
        'boosting_type' : ['gbdt'],
        'num_leaves' : [5, 10, 20, 50, 100],
        'max_depth' : [-1, 5, 10, 20, 50, 100],
        'num_boost_round' : [10000],
        'objective' : ['regression'],
        'min_data_in_leaf' : [10, 50, 100, 200, 500]
    }

    param_grid = ParameterGrid(params)

    Parallel(n_jobs=1)(delayed(eval_params)(X_train.values.copy(), y_train.copy(), param, i) for i, param in enumerate(param_grid))



