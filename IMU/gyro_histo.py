# plot the gyroscope historgram for few seconds of data
# https://stackoverflow.com/questions/29208440/fit-a-distribution-to-a-histogram
# https://stackoverflow.com/questions/70164620/how-to-gaussian-fit-histogram
# For gyro input in rad/s, the FWHM will be in rad/s
# TODO find relation between sigma and FWHM



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
PRECI= 2
TYPE = "e" # e: exponential notation
TS = 1.0 / FS
NB_SAMPLE = 1000 # nb of samples to take from the input data (csv file)
DEG_2_RAD = np.pi / 180.0
RAD_2_DEG = 180.0 / np.pi

def lin_interp(x, y, i, half):
    return x[i] + (x[i+1] - x[i]) * ((half - y[i]) / (y[i+1] - y[i]))

def half_max_x(x, y):
    half = max(y)/2.0
    signs = np.sign(np.add(y, -half))
    zero_crossings = (signs[0:-2] != signs[1:-1])
    zero_crossings_i = np.where(zero_crossings)[0]
    return [lin_interp(x, y, zero_crossings_i[0], half),
            lin_interp(x, y, zero_crossings_i[1], half)]
# Load CSV into np array
dataArr = np.genfromtxt(CSV_FILENAME, delimiter=',')

# Separate into arrays and select a slice of the input data
ts = dataArr[:NB_SAMPLE, 4]  # time stamp, second
gx = dataArr[:NB_SAMPLE, 5]  # (rad/s)
gy = dataArr[:NB_SAMPLE, 6]
gz = dataArr[:NB_SAMPLE, 7]

_, bins_gx, _ = plt.hist(gx, 20, density=1, alpha=0.5)
_, bins_gy, _ = plt.hist(gy, 20, density=1, alpha=0.5)
_, bins_gz, _ = plt.hist(gz, 20, density=1, alpha=0.5)
print(f'bins from histo: { bins_gx,bins_gy,bins_gz}')
mu, sigma = zip(stats.norm.fit(gx),stats.norm.fit(gy),stats.norm.fit(gz))

print(f'Gaussian best fit mu, sigma = {mu,sigma}')
best_fit_line = stats.norm.pdf(bins_gx, mu[0], sigma[0])
plt.plot(bins_gx, best_fit_line)
#x = gx.index.values
#y = np.array(gx['ABC'])
print(f'best_fit_line = {best_fit_line}')
x = bins_gx
#x = np.arange(len(gx))
#hmx = half_max_x(bins,gx) #x,y)
hmx = half_max_x(bins_gx,best_fit_line) #x,y)
#hmx = half_max_x(ts,gx) #x,y)
fwhm = (hmx[1] - hmx[0]) # 
print(f'FWHM = {fwhm:.{PRECI}}{NOISE_PARAM_UNIT}/s, hmx = {hmx}')

plt.plot([hmx[0],hmx[0]], [0,50])
plt.plot([hmx[1],hmx[1]], [0,50])
f, axarr = plt.subplots(3, sharex=True)
f.set_figheight(12)
f.set_figwidth(8)
f.suptitle(f'gyro noise histogram (OAK-D pro)',fontsize = 20)
#axarr[0].plot(t, accX_ref, 'y.',label="ground truth AccX")
_, bins, _ = axarr[0].hist(gx, 20, density=True, alpha=0.5)
#    axarr[0].plot(t, accX_best, "r-", label="best sensor")
#    axarr[0].plot(t, accX_good, "b-", label="good sensor")
#    axarr[0].plot(t, accX_worst, "g--", label="worst sensor")
axarr[0].set_title('Gyro Angular rate X')
axarr[0].grid()
axarr[0].legend()
#axarr[0].set_ylim([-2, 2])

plt.show()
