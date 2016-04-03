import numpy
import cPickle as pickle
from numpy.fft import fft


def get_all_data():
	train_data = []
	for i in range(1, 9):
		if i == 4 or i == 7:
			continue
		train_data.append(get_data(i))

	valid_data = []
	for i in range(9, 11):
		valid_data.append(get_data(i))

	test_data = []
	for i in range(11, 13):
		test_data.append(get_data(i))

	data_sets = train_data, valid_data, test_data

	return data_sets


def stage(stage):
	switcher = {
		'W': 0,
		'N1': 1,
		'N2': 2,
		'N3': 3,
		'R': 5
	}
	return switcher.get(stage)


def get_data(index):
	data = open("PSG Data/p%d.txt" % index, "r")
	teacher = open("PSG Data/p%d_ss.txt" % index, "r")

	split_file = data.read().split('\n')

	epochs = []

	values = []
	for j in range(10):
		values.append([])

	for i in range(len(split_file)):
		print i
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

		if (i+1) % (220*30) == 0:
			epochs.append(fft(numpy.asarray(values)))

			values = []
			for j in range(10):
				values.append([])

	split_file = teacher.read().split('\n')

	sleep_stages = []

	for line in split_file:
		split_line = line.split()
		if len(split_line) == 4:
			sleep_stages.append((int(split_line[0].replace(',', '')), stage(split_line[3])))

	temp = []

	cur_index = 1
	cur_stage = 0
	for s in sleep_stages:
		if s[0] == 1:
			cur_index = s[0] - 1
			cur_stage = s[1]
			continue
		for i in range(cur_index, s[0]-1):
			temp.append(cur_stage)
		cur_index = s[0] - 1
		cur_stage = s[1]

	for i in range(cur_index, sleep_stages[-1][0]):
		temp.append(cur_stage)

	sleep_stages = numpy.asarray(temp)

	return values, sleep_stages

if __name__ == '__main__':
	data_sets = get_all_data()

	pickle.dump(data_sets, open('data.p', 'wb'))
