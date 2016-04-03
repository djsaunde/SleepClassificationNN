from numpy.fft import fft
import matplotlib.pyplot as plt
import numpy as np

# sample spacing
T = 1.0 / 220.0

p = input('Enter participant number: ')

data = open('/home/dan/Documents/PSG Reports for NN Project/p%s.txt' % p, 'r')

print 'reading file'

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

print 'found %d sample points' % N

labels = []

fft_values = [[] for j in range(10)]

print 'taking fourier transform'

for j in range(10):
	print 'iteration %d' % (j+1)
	y = [np.float64(k) for k in values[j]]
	yf = fft(y)
	yf_real = ['%.3f' % val for val in yf.real.tolist()]
	fft_values[j] = yf_real
	xf = np.linspace(0.0, 1.0/(2.0*T), N/2)
	label, = plt.plot(xf, 2.0/N * np.abs(yf[0:N/2]), label='signal %d' % (j+1))
	labels.append(label)

write_data = open('fft_data/p%d_fft.txt' % p, 'w')

print 'writing to file'

write_data.truncate()

for j in range(len(fft_values[0])):
	line = ''
	for k in range(10):
		line += '%s ' % fft_values[k][j]
	write_data.write('%s\n' % line)

write_data.close()

plt.legend(handles = labels)
plt.grid()
plt.show()
