from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Flatten, GRU, Input, GlobalMaxPooling1D, Conv1D, concatenate, LSTM
from keras.optimizers import Adam
from keras.initializers import RandomNormal, RandomUniform

def standard(input_shape, nb_actions):

	# Next, we build a very simple model.
	model = Sequential()
	model.add(Flatten(input_shape=(1,) + input_shape))
	model.add(Dense(16))
	model.add(Activation('relu'))
	model.add(Dense(16))
	model.add(Activation('relu'))
	model.add(Dense(16))
	model.add(Activation('relu'))
	model.add(Dense(nb_actions))
	model.add(Activation('linear'))
	print(model.summary())

	return model

def gru_network(window_length, input_shape, nb_actions):

	print(window_length, input_shape, nb_actions)

	model = Sequential()
	model.add(GRU(32, dropout=0.2, input_shape=(window_length, input_shape), return_sequences=False))
	model.add(Dense(64, activation='relu'))
	model.add(Dense(16, activation='relu'))
	model.add(Dense(nb_actions, activation='linear'))
	print(model.summary())

	return model

def lstm_network(window_length, input_shape, nb_actions):

	model = Sequential()
	model.add(LSTM(64, dropout=0.2, input_shape=(window_length, input_shape), return_sequences=False))
	model.add(Dense(64, activation='relu'))
	model.add(Dense(16, activation='relu'))
	model.add(Dense(nb_actions, activation='softmax', kernel_initializer=RandomNormal(mean=-0, stddev=0)))
	print(model.summary())

	return model

def cnn(window_length, input_shape, nb_actions, n_sizes=[14, 11, 8, 5, 3, 2], n_filters=16, kernel_initializer='random_normal'):

	
	if kernel_initializer == 'random_normal':
		print('Random Normal')
		init = RandomNormal(mean=-10, stddev=10)

	else:

		init = RandomUniform()

	inputs = Input((window_length, input_shape))

	convs = []
	for size in n_sizes:
	    
	    conv = Conv1D(n_filters, size, strides=1, activation='relu')(inputs)
	    conv_max = GlobalMaxPooling1D()(conv)
	    #conv_avg = GlobalAveragePooling1D()(conv)
	    #concat = concatenate([conv_max, conv_avg])
	    convs.append(conv_max)

	conv = concatenate(convs)
	dense = Dense(64)(conv)
	dense = Dense(3)(dense)
	output = Dense(nb_actions, activation='softmax')(dense)

	model = Model(inputs=[inputs], outputs=[output])
	print(model.summary())

	return model
