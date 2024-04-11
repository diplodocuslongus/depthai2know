# using AllanTools

import os # for file manipulation
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import allantools
#x = allantools.noise.white(10000)        # Generate some phase data, in seconds.

import scipy.stats as stats

HOME = os.getenv("HOME")
CSV_FILENAME = 'imu_oakdpro_1hr_28032024.csv'
#CSV_FILENAME = HOME+'/Data/Drones/IMU/imu_oak_BNO086_2hr_02042024.csv'
FS = 100  # Sample rate [Hz]
NOISE_PARAM_UNIT = 'rad'
TS = 1.0 / FS
NB_SAMPLE = 1000 # nb of samples to take from the input data (csv file)

# Load CSV into np array
dataArr = np.genfromtxt(CSV_FILENAME, delimiter=',')

# Separate into arrays and select a slice of the input data
gx = dataArr[:NB_SAMPLE, 5]  # (rad/s)
gy = dataArr[:NB_SAMPLE, 6]
gz = dataArr[:NB_SAMPLE, 7]
(taus, adevs, errors, ns) = allantools.oadev(gx)
print(taus, adevs,errors,ns)
