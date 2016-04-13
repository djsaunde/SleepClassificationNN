import numpy as np
import cPickle as pickle
from numpy.fft import rfft
from itertools import islice


def downsample(rows, proportion = 1.0):
	return list(islice(rows, 0, len(rows), int(1 / proportion)))


def get_all_data():
	train_data = []
	for i in range(1, 12):
		if i == 4 or i == 5 or i == 6 or i == 7 or i == 8 or i == 9 or i == 11:
			continue
		print '...loading training file for participant %d' % i
		train_data.append(get_data(i))

	valid_data = []
	for i in range(12, 14):
		print '...loading validation file for participant %d' % i
		valid_data.append(get_data(i))

	test_data = []
	for i in range(14, 16):
		print '...loading test file for participant %d' % i
		test_data.append(get_data(i))

	return train_data, valid_data, test_data


def stage(stage):
	switcher = { 'W': 0, 'N1': 1, 'N2': 2, 'N3': 3, 'R': 4, 'No Stage': 5 }
	return switcher.get(stage)


def get_data(index):
	sample_rate = 200
	epoch_length = 30

	data = open("PSG Data/p%d.txt" % index, "r")

	split_file = data.read().split('\n')

	epochs = []

	print '...reading raw PSG data into Fourier transformed epochs'

	values = []
	for j in range(10):
		values.append([])

	for i in range(len(split_file)):
		split_line = split_file[i].split()
		if len(split_line) == 10:
			values[0].append(float(split_line[0]))
			values[1].append(float(split_line[1]))
			values[2].append(float(split_line[2]))
			values[3].append(float(split_line[3]))
			values[4].append(float(split_line[4]))
			values[5].append(float(split_line[5]))
			values[6].append(float(split_line[6]))
			values[7].append(float(split_line[7]))
			values[8].append(float(split_line[8]))
			values[9].append(float(split_line[9]))

		if (i + 1) % (sample_rate * epoch_length) == 0:
			inputs = []
			for (k, value) in enumerate(values):
				values[k] = downsample(np.abs(np.real(rfft(value))), 0.2)
				if len(values[k]) != 600:
					print(len(values[k]))
					print('2nd')
				inputs.append(values[k])
			epochs.append(np.asarray(inputs))

			values = []
			for j in range(10):
				values.append([])

	inputs = []
	for (k, value) in enumerate(values):
		for i in range(len(values[k]) + 1, 6000):
			values[k].append(0)
		values[k] = downsample(np.abs(np.real(rfft(value))), 0.2)
		if len(values[k]) != 600:
			print(len(values[k]))
			print('2nd')
		inputs.append(values[k])
	epochs.append(np.asarray(inputs))

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

	sleep_stages = np.asarray(temp)

	if len(sleep_stages) < len(epochs):
		epochs = epochs[0:len(sleep_stages)]
	else:
		sleep_stages = sleep_stages[0:len(epochs)]

	return epochs, sleep_stages


if __name__ == '__main__':
	data_sets = get_all_data()

	pickle.dump(data_sets, open('conv_data_5.p', 'wb'))
