from numpy.fft import fft
import matplotlib.pyplot as plt
import numpy as np

# sample spacing
T = 1.0 / 220.0

files = ['p1.txt', 'p2.txt', 'p3.txt', 'p4.txt', 'p5.txt', 'p6.txt', 'p8.txt', 'p9.txt', 'p10.txt',
         'p11.txt', 'p12.txt', 'p13.txt', 'p14.txt', 'p15.txt', 'p17.txt', 'p18.txt', 'p19.txt', 'p20.txt', 'p24.txt',
         'p25.txt', 'p26.txt', 'p27.txt', 'p31.txt', 'p33.txt', 'p34.txt', 'p35.txt', 'p36.txt', 'p37.txt', 'p38.txt',
         'p29.txt', 'p40.txt']

for (i, f) in enumerate(files):
	data = open('/home/dan/Documents/PSG Reports for NN Project/%s' % f, 'r')

	values = [[] for j in range(10)]

	for line in data.read().split('\n'):
		split_line = line.split()
		if len(split_line) == 10:
			values[0].append(split_line[0])
			values[1].append(split_line[1])
			values[2].append(split_line[2])
			values[3].append(split_line[3])
			values[4].append(split_line[4])
			values[5].append(split_line[5])
			values[6].append(split_line[6])
			values[7].append(split_line[7])
			values[8].append(split_line[8])
			values[9].append(split_line[9])

	# number of sample points
	N = len(values[0])

	labels = []

	fft_values = [[] for j in range(10)]

	for j in range(10):
		y = [float(k) for k in values[j]]
		yf = fft(y)
		# yf = yf.real.tolist()
		# fft_values[j] = yf
		xf = np.linspace(0.0, 1.0/(2.0*T), N/2)
		label, = plt.plot(xf, 2.0/N * np.abs(yf[0:N/2]), label='signal %d' % (i + 1))
		labels.append(label)

	write_data = open('fft_data/p%d_fft.txt' % i, 'w')

	for (j, value) in enumerate(fft_values):
		line = ''
		for k in range(10):
			line += '%s ' % value[k]
		write_data.write('%s\n' % line)

	plt.legend(handles = labels)
	plt.grid()
	plt.show()
