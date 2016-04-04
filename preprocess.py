import numpy as np
import cPickle as pickle
from numpy.fft import rfft
from numpy import average

def get_all_data():
	train_data = []
	for i in range(1, 12):
		if i == 4 or i == 7 or i == 8:
			continue
		print '...loading training file for participant %d' % i
		train_data.append(get_data(i))

	valid_data = []
	for i in range(12, 14):
		print '...loading validation file for participant %d' % i
		valid_data.append(get_data(i))

	test_data = []
	for i in range(14, 16):
		test_data.append(get_data(i))
		print '...loading test file for participant %d' % i
	data_sets = train_data, valid_data, test_data

	return data_sets


def stage(stage):
	switcher = { 'W': 0, 'N1': 1, 'N2': 2, 'N3': 3, 'R': 5, 'No Stage': -1 }
	return switcher.get(stage)


def get_data(index):
	sample_rate = 220
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
				values[k] = np.abs(np.real(rfft(value)))
				cur_inputs = [average(values[k][0:15]), average(values[k][16:60]), average(values[k][61:120]),
				              average(values[k][121:180]), average(values[k][181:240]), average(values[k][241:315]),
				              average(values[k][315:390]), average(values[k][391:600]), average(values[k][601:900]),
				              average(values[k][901:2401]), average(values[k][2401:3300])]
				inputs.append(cur_inputs)
			epochs.append(np.asarray(inputs))

			values = []
			for j in range(10):
				values.append([])

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

	print epochs

	print sleep_stages

	return epochs, sleep_stages


if __name__ == '__main__':
	data_sets = get_all_data()

	pickle.dump(data_sets, open('data.p', 'wb'))
