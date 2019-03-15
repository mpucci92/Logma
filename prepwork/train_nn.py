from keras.models import Sequential, Model
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.layers import Dense, Dropout, Activation, Flatten, Input, concatenate
from keras.layers import MaxPooling1D, InputLayer, Conv1D, GlobalMaxPooling1D, GlobalAveragePooling1D
import data_prep as dp
import pandas as pd
import sys

from argparse import ArgumentParser

from consts import dir_

def get_model(ticker):

	n_sizes = [14, 11, 8, 5, 3, 2]
	n_filters = 64
	es = EarlyStopping(monitor="val_loss", min_delta=10e-3, patience=10)
	red = ReduceLROnPlateau()

	inputs = Input((20, 11))

	convs = []
	for size in n_sizes:
	    
	    conv = Conv1D(n_filters, size, strides=1, activation='relu')(inputs)
	    #conv_max = GlobalMaxPooling1D()(conv)
	    conv_avg = GlobalAveragePooling1D()(conv)
	    #concat = concatenate([conv_max, conv_avg])
	    convs.append(conv_avg)

	conv = concatenate(convs)
	dense = Dense(128)(conv)
	dropout = Dropout(0.2)(conv)
	dense = Dense(64)(dropout)
	dropout = Dropout(0.2)(dense)
	dense = Dense(32)(dropout)
	output = Dense(11)(dense)

	model = Model(inputs=[inputs], outputs=[output])
	model.compile('rmsprop', loss='mse')

	print(model.summary())

	X_train, y_train, X_val, y_val = dp.load_data(ticker)
	model.fit(x=X_train, y=y_train, epochs=100, batch_size = 3200, validation_data=(X_val, y_val), callbacks=[es, red])
	new_model = Model(inputs=[model.layers[0].output], outputs=[model.layers[-2].output])
	new_model.save('{}/timeseries_embeddor'.format(dir_))

	return new_model

def save_embeddings(model, ticker):

	X_new, dates = dp.get_X_new(ticker)
	X_new = model.predict(X_new)

	print(X_new.shape[0] == dates.shape[0])

	df_embed = pd.DataFrame(X_new)
	df_embed['Datetime'] = dates
	df_embed.to_pickle('{}/{}_embed.pkl'.format(dir_, ticker))

def main(ticker):

	model = get_model(ticker)
	save_embeddings(model, ticker)

if __name__ == '__main__':

	argparser = ArgumentParser()
	argparser.add_argument('ticker')
	args = argparser.parse_args()

	sys.exit(save_embeddings(get_model(args.ticker), args.ticker))