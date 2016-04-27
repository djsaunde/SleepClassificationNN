import gzip
import numpy as np
import cPickle as pickle
from numpy.fft import rfft
from itertools import islice
import math, scipy


def downsample(rows, downsample_factor):  # simple downsampling method used in reducing dimension of spectral plot input
	rows = np.array(rows)
	pad_size = math.ceil(float(rows.size)/downsample_factor) * downsample_factor - rows.size
	rows_padded = np.append(rows, np.zeros(pad_size)*np.NaN)
	scipy.nanmean(rows_padded.reshape(-1, downsample_factor), axis=1)
	return list(rows_padded)


def get_all_data(downsample_factor):  # builds pickled, zipped files for training, validation, and testing
	train_data_x = []
	train_data_y = []

	for i in range(1, 12):
		if i == 4 or i == 5 or i == 6 or i == 7 or i == 8 or i == 9 or i == 11:  # bad data :(
			continue
		print '...loading training file for participant %d' % i
		data = get_data(i, downsample_factor)
		train_data_x.extend(data[0])
		train_data_y.extend(data[1])

	print '...pickling training data'

	train_data = (np.array(train_data_x), np.array(train_data_y))

	with gzip.open('train_data_' + str(downsample_factor) + '.pkl.gz', 'wb') as f:
		pickle.dump(train_data, f)

	valid_data_x = []
	valid_data_y = []

	for i in range(12, 14):
		print '...loading validation file for participant %d' % i
		data = get_data(i, downsample_factor)
		valid_data_x.extend(data[0])
		valid_data_y.extend(data[1])

	print '...pickling validation data'

	valid_data = (np.array(valid_data_x), np.array(valid_data_y))

	with gzip.open('valid_data_' + str(downsample_factor) + '.pkl.gz', 'wb') as f:
		pickle.dump(valid_data, f)

	test_data_x = []
	test_data_y = []

	for i in range(14, 16):
		print '...loading test file for participant %d' % i
		data = get_data(i, downsample_factor)
		test_data_x.extend(data[0])
		test_data_y.extend(data[1])

	print '...pickling testing data'

	test_data = (np.array(test_data_x), np.array(test_data_y))

	with gzip.open('test_data_' + str(downsample_factor) + '.pkl.gz', 'wb') as f:
		pickle.dump(test_data, f)


def stage(stage):  # codes each sleep stage as a unique integer
	switcher = { 'W': 0, 'N1': 1, 'N2': 2, 'N3': 3, 'R': 4, 'No Stage': 5 }
	return switcher.get(stage)


def get_data(index, downsample_factor):  # gets input, expected output for a given participant
	sample_rate = 200  # electrode sampling rate in Hz
	epoch_length = 30  # length in seconds of a single epoch

	data = open("PSG Data/p%d.txt" % index, "r")  # open PSG data for a given participant

	split_file = data.read().split('\n')  # split line by line (each line is a single sample from all 10 electrodes

	epochs = []

	print '...reading raw PSG data into Fourier transformed epochs'

	values = []
	for j in range(10):  # there are 10 signal readings per line
		values.append([])

	for i in range(len(split_file)):
		split_line = split_file[i].split()
		if len(split_line) == 10:
			for k in range(10):
				values[k].append(float(split_line[k]))

		if (i + 1) % (sample_rate * epoch_length) == 0:  # this ensures that we start a new epoch after 220 * 30 samples
			epoch = []
			for (k, value) in enumerate(values):  # for each signal in the epoch's worth of data
				values[k] = downsample(np.abs(np.real(rfft(value))), downsample_factor)  # we do the real FFT on
				# the epoch's worth of data and further downsample by the input factor
				epoch.append(values[k])

			epoch = [item for sublist in epoch for item in sublist]

			epochs.append(epoch)  # add this epoch's data to our list of epochs

			epochs.append(epoch)  # add this epoch's data to our list of epochs

			values = []  # reset this array of arrays to prepare for the next epoch
			for j in range(10):
				values.append([])

	epoch = []
	for (k, value) in enumerate(values):
		for i in range(len(values[k]) + 1, 6000):
			values[k].append(0)  # if the last epoch was cut short, we pad it to the correct length with 0's
		values[k] = downsample(np.abs(np.real(rfft(value))), downsample_factor)
		epoch.append(values[k])

	epoch = [item for sublist in epoch for item in sublist]

	epochs.append(epoch)

	epochs = np.array(epochs, dtype = 'float32')

	teacher = open("PSG Data/p%d_ss.txt" % index, "r")

	split_file = teacher.read().split('\n')

	print '...reading in teacher values'

	sleep_stages = []

	for line in split_file:
		if 'No Stage' in line:
			sleep_stages.append((int(line.split()[0].replace(',', '')), stage('No Stage')))
		if len(line.split()) == 4:
			sleep_stages.append((int(line.split()[0].replace(',', '')), stage(line.split()[3])))

	temp = []

	cur_index = 1
	cur_stage = 0

	for s in sleep_stages:
		if s[0] == 1:
			cur_index = s[0] - 1
			cur_stage = s[1]
			continue
		for i in range(cur_index, s[0] - 1):
			temp.append(cur_stage)
		cur_index = s[0] - 1
		cur_stage = s[1]

	for i in range(cur_index, sleep_stages[-1][0]):
		temp.append(cur_stage)

	sleep_stages = temp

	if len(sleep_stages) < len(epochs):
		epochs = epochs[0:len(sleep_stages)]
	else:
		sleep_stages = sleep_stages[0:len(epochs)]

	return epochs, sleep_stages


if __name__ == '__main__':
	downsample_factor = input('Enter downsampling factor: ')
	get_all_data(downsample_factor)