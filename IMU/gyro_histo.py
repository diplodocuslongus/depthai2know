# plot the gyroscope historgram for few seconds of data
# https://stackoverflow.com/questions/29208440/fit-a-distribution-to-a-histogram
# https://stackoverflow.com/questions/70164620/how-to-gaussian-fit-histogram
import os # for file manipulation
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import scipy.stats as stats

HOME = os.getenv("HOME")
#CSV_FILENAME = 'imu_oakdpro_1hr_28032024.csv'
CSV_FILENAME = HOME+'/Data/Drones/IMU/imu_oak_BNO086_2hr_02042024.csv'
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

_, bins, _ = plt.hist(gx, 20, density=1, alpha=0.5)
mu, sigma = stats.norm.fit(gx)
best_fit_line = stats.norm.pdf(bins, mu, sigma)
plt.plot(bins, best_fit_line)
plt.show()
x = data.index.values
y = np.array(data['ABC'])

def lin_interp(x, y, i, half):
    return x[i] + (x[i+1] - x[i]) * ((half - y[i]) / (y[i+1] - y[i]))

def half_max_x(x, y):
    half = max(y)/2.0
    signs = np.sign(np.add(y, -half))
    zero_crossings = (signs[0:-2] != signs[1:-1])
    zero_crossings_i = np.where(zero_crossings)[0]
    return [lin_interp(x, y, zero_crossings_i[0], half),
            lin_interp(x, y, zero_crossings_i[1], half)]
hmx = half_max_x(x,y)
fwhm = hmx[1] - hmx[0]

