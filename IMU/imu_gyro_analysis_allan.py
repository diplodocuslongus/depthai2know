# Return 3 main noise characteristics of an IMU with accelerometer and gyroscope
# Capture > 1hr (ideal 3 to 6) of IMU data, save to a .csv file
# Allan deviation function derived from
# https://mwrona.com/posts/gyro-noise-analysis/
# and matlab code
# data format
# accTs, accX, accY, accZ, gyrTs, gyrX, gyrY, gyrZ
# Ts = time stamp
# accX,...: component of raw accelerometer m/s^2
# gyrX,...: component of raw gyroscope, rad/s
# https://stackoverflow.com/questions/18760903/fit-a-curve-using-matplotlib-on-loglog-scale
# modif: added constrained linear fit, ref:
# https://stackoverflow.com/questions/48469889/how-to-fit-a-polynomial-with-some-of-the-coefficients-constrained
# added all Allan deviation parameters:
# - angle random walk (ARW), noted N in matlab, IEEE std 952. In rad/s / √Hz
# - rate random walk (RRW), noted K in matlab, IEEE std 952, in rad/s * √Hz
# - bias instability, B in rad/s
#
import os # for file manipulation
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# fit function for the linear fit of a constrained coefficient polynomial (e.g. for the -0.5 slope)

def fitfunc(x, a, b):
    return a*x + b

# format result display
PRECI= 2
TYPE = "e" # e: exponential notation
HOME = os.getenv("HOME")
# Config. params
#CSV_FILENAME = 'imu_oakdpro_1hr_28032024.csv'
CSV_FILENAME = HOME+'/Data/Drones/IMU/imu_oak_BNO086_2hr_02042024.csv'
FS = 100  # Sample rate [Hz]
NOISE_PARAM_UNIT = 'rad'
#NOISE_PARAM_UNIT = 'deg' # 'rad'
DEG_2_RAD = np.pi / 180.0
RAD_2_DEG = 180.0 / np.pi
def AllanDeviation(dataArr: np.ndarray, fs: float, maxNumM: int=100):
    """Compute the Allan deviation (sigma) of time-series data.

    Algorithm obtained from Mathworks:
    https://www.mathworks.com/help/fusion/ug/inertial-sensor-noise-analysis-using-allan-variance.html

    Args
    ----
        dataArr: 1D data array
        fs: Data sample frequency in Hz
        maxNumM: Number of output points

    Returns
    -------
        (taus, allanDev): Tuple of results
        taus (numpy.ndarray): Array of tau values
        allanDev (numpy.ndarray): Array of computed Allan deviations
    """
    ts = 1.0 / fs
    N = len(dataArr)
    Mmax = 2**np.floor(np.log2(N / 2))
    M = np.logspace(np.log10(1), np.log10(Mmax), num=maxNumM)
    M = np.ceil(M)  # Round up to integer
    M = np.unique(M)  # Remove duplicates
    taus = M * ts  # Compute 'cluster durations' tau

    # Compute Allan variance
    allanVar = np.zeros(len(M))
    for i, mi in enumerate(M):
        twoMi = int(2 * mi)
        mi = int(mi)
        allanVar[i] = np.sum(
            (dataArr[twoMi:N] - (2.0 * dataArr[mi:N-mi]) + dataArr[0:N-twoMi])**2
        )

    allanVar /= (2.0 * taus**2) * (N - (2.0 * M))
    return (taus, np.sqrt(allanVar))  # Return deviation (dev = sqrt(var))


# Load CSV into np array
dataArr = np.genfromtxt(CSV_FILENAME, delimiter=',')
TS = 1.0 / FS

# Separate into arrays
gx = dataArr[:, 5]  # (rad/s)
gy = dataArr[:, 6]
gz = dataArr[:, 7]
if NOISE_PARAM_UNIT == 'deg':
    gx = gx * (180.0 / np.pi)  # [deg/s]
    gy = gy * (180.0 / np.pi)
    gz = gz * (180.0 / np.pi)

# Calculate gyro angles
thetax = np.cumsum(gx) * TS  # deg or rad depending on NOISE_PARAM_UNIT
thetay = np.cumsum(gy) * TS
thetaz = np.cumsum(gz) * TS

# Compute Allan deviations
(taux, adx) = AllanDeviation(thetax, FS, maxNumM=200)
(tauy, ady) = AllanDeviation(thetay, FS, maxNumM=200)
(tauz, adz) = AllanDeviation(thetaz, FS, maxNumM=200)

# Plot data on log-scale
plt.figure()
plt.title('Gyro Allan Deviations')
plt.plot(taux, adx, 'rx', label='gx')
# plt.plot(taux, adx, 'rx', label='gx') # to see the points
plt.plot(tauy, ady, label='gy')
plt.plot(tauz, adz, label='gz')
plt.xlabel(r'$\tau$ [sec]')
plt.ylabel(f'Deviation ({NOISE_PARAM_UNIT}/s)')
plt.grid(True, which="both", ls="-", color='0.65')
plt.legend()
plt.xscale('log')
plt.yscale('log')
#plt.show()
# find angle random walk, intersection of random walk line fit (-0.5 slope)
# at tau = 1
# add curve fit to proper section of curve
# that is, between  10^-1 < tau < 20 for the gx component for one of the OAK-D
# Location for the other components (gy, gz) is likely (slightly) different
# get the corresponding indexes (manual work, could do auto)
idx_start = np.where(taux < 0.1)[0][-1]
idx_end = np.where(taux > 20)[0][0]
print(f'linear -0.5 slope for gx: = {idx_start,idx_end}')
logtaux = np.log(taux[idx_start:idx_end])
logadx = np.log(adx[idx_start:idx_end])
# for gy
idx_start = np.where(tauy < 0.05)[0][-1]
idx_end = np.where(tauy > 10)[0][0]
print(f'linear -0.5 slope for gy: = {idx_start,idx_end}')
logtauy = np.log(tauy[idx_start:idx_end])
logady = np.log(ady[idx_start:idx_end])
# for gz
idx_start = np.where(tauz < 0.06)[0][-1]
idx_end = np.where(tauz > 10)[0][0]
print(f'linear -0.5 slope for gz: = {idx_start,idx_end}')
logtauz = np.log(tauz[idx_start:idx_end])
logadz = np.log(adz[idx_start:idx_end])
#####
# below we do 2 different fits: one with fixed -0.5 slope, the other computes the slope (linear fit)
# fix the slope for the linear fit
#####
UP_BOUND_SLOPE = -0.5
LO_BOUND_SLOPE = -0.5001
popt_cons, _ = curve_fit(fitfunc, logtaux,logadx, bounds=([LO_BOUND_SLOPE,-np.inf],
                                                          [UP_BOUND_SLOPE,np.inf]))
print(f'popt_cons = {popt_cons}')
# compute the slope
coeffs_x = np.polyfit(logtaux,logadx, deg=1)
coeffs_y = np.polyfit(logtauy,logady, deg=1)
coeffs_z = np.polyfit(logtauz,logadz, deg=1)
print(coeffs_x,coeffs_y,coeffs_z)
poly_x = np.poly1d(coeffs_x)
poly_y = np.poly1d(coeffs_y)
poly_z = np.poly1d(coeffs_z)
#yfit_x = lambda x: np.exp(poly_x(np.log(taux))) #np.log(x)))
#yfit_y = lambda x: np.exp(poly_y(np.log(tauy))) #np.log(x)))
#yfit_z = lambda x: np.exp(poly_z(np.log(tauz))) #np.log(x)))
# random walk fit
rw_fit_x = lambda taux: np.exp(poly_x(np.log(taux)))
rw_fit_y = lambda tauy: np.exp(poly_y(np.log(tauy)))
rw_fit_z = lambda tauz: np.exp(poly_z(np.log(tauz)))
# -0.5 slope line fit to random walk
fixpoly_x = np.poly1d(popt_cons)
#fixpoly_y = np.poly1d(coeffs_y)
#fixpoly_z = np.poly1d(coeffs_z)
rw_fixfit_x = lambda taux: np.exp(fixpoly_x(np.log(taux)))
#rw_fixfit_y = lambda tauy: np.exp(poly_y(np.log(tauy)))
#rw_fixfit_z = lambda tauz: np.exp(poly_z(np.log(tauz)))

# angle random walk
# often noted N
# unit rad/s/√Hz or rad/√s or °/√hr for a more palpable unit
gyro_angle_randwalk_x = rw_fit_x(1)
gyro_angle_randwalk_x_fixfit = rw_fixfit_x(1)
gyro_angle_randwalk_y = rw_fit_y(1)
gyro_angle_randwalk_z = rw_fit_z(1)
gyro_angle_randwalk_avg = (gyro_angle_randwalk_x
                           + gyro_angle_randwalk_y
                           + gyro_angle_randwalk_z) / 3.0
gyro_angle_randwalk_avg_dph = 60 * gyro_angle_randwalk_avg * RAD_2_DEG
print((f'gyro_angle_randwalk_x: from linear fit '
      f'{gyro_angle_randwalk_x:.{PRECI}{TYPE}},'
      f'from -0.5 slope fit: {gyro_angle_randwalk_x_fixfit:.{PRECI}{TYPE}}'))
print(f'gyro_angle_randwalk_y = {gyro_angle_randwalk_y:.{PRECI}{TYPE}}')
print(f'gyro_angle_randwalk_z = {gyro_angle_randwalk_z:.{PRECI}{TYPE}}')
print(f'Average gyro_angle_randwalk = '
      f'{gyro_angle_randwalk_avg:.{PRECI}{TYPE}} {NOISE_PARAM_UNIT}/√s'
      f' or {gyro_angle_randwalk_avg_dph:.{PRECI:g}} °/√hr (deg/sqrt(hour))')
      #f' or {gyro_angle_randwalk_avg_dph:.{PRECI}{TYPE}} °/√hr (deg/sqrt(hour))')
#print(f'Sqrt Average gyro_angle_randwalk \
    #= {np.sqrt(gyro_angle_randwalk_avg):.{PRECI}{TYPE}}')
plt.plot(1,gyro_angle_randwalk_x,'b8')
plt.plot(1,gyro_angle_randwalk_y,'r8')
plt.plot(1,gyro_angle_randwalk_z,'g8')
plt.plot(taux,rw_fit_x(taux))
plt.plot(tauy,rw_fit_y(tauy))
plt.plot(tauz,rw_fit_z(tauz))

# get the rate random walk (unit: (rad/s)/√Hz
# fit in the other direction

idx_start = np.where(taux > 100)[0][0]
idx_end = np.where(taux < 1000)[0][-1]
print(f'linear fit slope for gx: = {idx_start,idx_end}')
logtaux = np.log(taux[idx_start:idx_end])
logadx = np.log(adx[idx_start:idx_end])
# for gy
idx_start = np.where(tauy > 100)[0][0]
idx_end = np.where(tauy < 1000)[0][-1]
print(f'linear fit slope for gy: = {idx_start,idx_end}')
logtauy = np.log(tauy[idx_start:idx_end])
logady = np.log(ady[idx_start:idx_end])
# for gz
idx_start = np.where(tauz > 100)[0][0]
idx_end = np.where(tauz < 1000)[0][-1]
print(f'linear fit slope for gz: = {idx_start,idx_end}')
logtauz = np.log(tauz[idx_start:idx_end])
logadz = np.log(adz[idx_start:idx_end])

coeffs_x = np.polyfit(logtaux,logadx, deg=1)
coeffs_y = np.polyfit(logtauy,logady, deg=1)
coeffs_z = np.polyfit(logtauz,logadz, deg=1)
print(coeffs_x,coeffs_y,coeffs_z)
poly_x = np.poly1d(coeffs_x)
poly_y = np.poly1d(coeffs_y)
poly_z = np.poly1d(coeffs_z)
#yfit = lambda x: poly_x(taux)
rrw_fit_x = lambda taux: np.exp(poly_x(np.log(taux)))
rrw_fit_y = lambda tauy: np.exp(poly_y(np.log(tauy)))
rrw_fit_z = lambda tauz: np.exp(poly_z(np.log(tauz)))
#yfit_x = lambda x: np.exp(poly_x(np.log(taux))) #np.log(x)))
#yfit_y = lambda x: np.exp(poly_y(np.log(tauy))) #np.log(x)))
#yfit_z = lambda x: np.exp(poly_z(np.log(tauz))) #np.log(x)))
plt.plot(taux,rrw_fit_x(taux))
plt.plot(tauy,rrw_fit_y(tauy))
plt.plot(tauz,rrw_fit_z(tauz))
#plt.plot(tauz,yfit_z(tauz))
#################
# Bias instability
# called gyro "random walk" in Kalibr
#################
# compute derivative of Allan curve and intersect with line of slope 0

deriv_x = np.gradient(adx,taux)
deriv_y = np.gradient(ady,tauy)
deriv_z = np.gradient(adz,tauz)
local_min_x = np.argmin(np.abs(deriv_x))
local_min_y = np.argmin(np.abs(deriv_y))
local_min_z = np.argmin(np.abs(deriv_z))
scale_fact = np.sqrt(2*np.log(2)/np.pi)
bias_instab_x =adx[local_min_x] * scale_fact
bias_instab_y =ady[local_min_y] * scale_fact
bias_instab_z =adz[local_min_z] * scale_fact
gyro_bias_instab_avg = (bias_instab_x + bias_instab_y + bias_instab_z)/3.0
gyro_bias_instab_avg_dph = 3600 * gyro_bias_instab_avg * RAD_2_DEG
print(f'local min: {np.argmin(np.abs(deriv_x))}, scale_fact = {scale_fact}')
print(f'Bias instability in x: {bias_instab_x:.{PRECI}{TYPE}}{NOISE_PARAM_UNIT}/s')
print(f'Bias instability in y: {bias_instab_y:.{PRECI}{TYPE}}{NOISE_PARAM_UNIT}/s')
print(f'Bias instability in z: {bias_instab_z:.{PRECI}{TYPE}}{NOISE_PARAM_UNIT}/s')
print(f'Average bias instability = '
    f'{gyro_bias_instab_avg:.{PRECI}{TYPE}} {NOISE_PARAM_UNIT}/s '
    f'{gyro_bias_instab_avg_dph:.{PRECI}} deg/hr')
#print(f'dev = {logadx(local_min[0])}')

# find rate random walk unit (rad/s)*√Hz or (°/s)*√Hz
#, intersection of random walk line fit
# at tau = 3
# print(f'poly_z = {poly_z}')
# print(f'rrw_fit_z(1)= {rrw_fit_z(1)}')
gyro_rate_randwalk_x = rrw_fit_x(3)
gyro_rate_randwalk_y = rrw_fit_y(3)
gyro_rate_randwalk_z = rrw_fit_z(3)
gyro_rate_randwalk_avg = (gyro_rate_randwalk_x + gyro_rate_randwalk_y + gyro_rate_randwalk_z)/3.0
print(f'gyro_rate_randwalk_x = {gyro_rate_randwalk_x:.{PRECI}{TYPE}} {NOISE_PARAM_UNIT}/s/√s')
print(f'gyro_rate_randwalk_y = {gyro_rate_randwalk_y:.{PRECI}{TYPE}} {NOISE_PARAM_UNIT}/s/√s')
print(f'gyro_rate_randwalk_z = {gyro_rate_randwalk_z:.{PRECI}{TYPE}} {NOISE_PARAM_UNIT}/s/√s')
print(f'Average gyro_rate_randwalk = {gyro_rate_randwalk_avg:.{PRECI}{TYPE}} {NOISE_PARAM_UNIT}/s/√s')
plt.plot(3,gyro_rate_randwalk_x,'bo')
plt.plot(3,gyro_rate_randwalk_y,'ro')
plt.plot(3,gyro_rate_randwalk_z,'go')
plt.show()
