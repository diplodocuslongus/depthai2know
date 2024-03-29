# https://mwrona.com/posts/gyro-noise-analysis/
# data format
# accTs, accX, accY, accZ, gyrTs, gyrX, gyrY, gyrZ 
# Ts = time stamp 
# accX,...: component of raw accelerometer m/s^2
# gyrX,...: component of raw gyroscope, rad/s
# https://stackoverflow.com/questions/18760903/fit-a-curve-using-matplotlib-on-loglog-scale
import numpy as np
import matplotlib.pyplot as plt

# Config. params
CSV_FILENAME = 'imu_oakdpro_1hr_28032024.csv'
#DATA_FILE = 'gyro-data.csv'  # CSV data file "gx,gy,gz"
fs = 100  # Sample rate [Hz]
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
ts = 1.0 / fs

# Separate into arrays
gx = dataArr[:, 5] * (180.0 / np.pi)  # [deg/s]
gy = dataArr[:, 6] * (180.0 / np.pi)
gz = dataArr[:, 7] * (180.0 / np.pi)

# Calculate gyro angles
thetax = np.cumsum(gx) * ts  # [deg]
thetay = np.cumsum(gy) * ts
thetaz = np.cumsum(gz) * ts

# Compute Allan deviations
(taux, adx) = AllanDeviation(thetax, fs, maxNumM=200)
(tauy, ady) = AllanDeviation(thetay, fs, maxNumM=200)
(tauz, adz) = AllanDeviation(thetaz, fs, maxNumM=200)

# Plot data on log-scale
plt.figure()
plt.title('Gyro Allan Deviations')
plt.plot(taux, adx, 'rx', label='gx')
# plt.plot(taux, adx, 'rx', label='gx') # to see the points
plt.plot(tauy, ady, label='gy')
plt.plot(tauz, adz, label='gz')
plt.xlabel(r'$\tau$ [sec]')
plt.ylabel('Deviation [deg/sec]')
plt.grid(True, which="both", ls="-", color='0.65')
plt.legend()
plt.xscale('log')
plt.yscale('log')
#plt.show()

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
# get the angle random walk
gyro_angle_randwalk_x = rw_fit_x(1)
gyro_angle_randwalk_y = rw_fit_y(1)
gyro_angle_randwalk_z = rw_fit_z(1)
gyro_angle_randwalk_avg = (gyro_angle_randwalk_x + gyro_angle_randwalk_y + gyro_angle_randwalk_z)/3.0
print(f'gyro_angle_randwalk_x = {gyro_angle_randwalk_x}')
print(f'gyro_angle_randwalk_y = {gyro_angle_randwalk_y}')
print(f'gyro_angle_randwalk_z = {gyro_angle_randwalk_z}')
print(f'Average gyro_angle_randwalk = {gyro_angle_randwalk_avg} deg/sqrt(s)')
plt.plot(1,gyro_angle_randwalk_x,'b8')
plt.plot(1,gyro_angle_randwalk_y,'r8')
plt.plot(1,gyro_angle_randwalk_z,'g8')
plt.plot(taux,rw_fit_x(taux))
plt.plot(tauy,rw_fit_y(tauy))
plt.plot(tauz,rw_fit_z(tauz))

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
# find random walk, intersection of random walk line fit (-0.5 slope)
# at tau = 1
print(f'poly_z = {poly_z}')
print(f'rrw_fit_z(0)= {rrw_fit_z(0)}')
print(f'rrw_fit_z(1)= {rrw_fit_z(1)}')
gyro_rate_randwalk_x = rrw_fit_x(2)
gyro_rate_randwalk_y = rrw_fit_y(2)
gyro_rate_randwalk_z = rrw_fit_z(2)
gyro_rate_randwalk_avg = (gyro_rate_randwalk_x + gyro_rate_randwalk_y + gyro_rate_randwalk_z)/3.0
print(f'gyro_rate_randwalk_x = {gyro_rate_randwalk_x} deg/s/sqrt(s)')
print(f'gyro_rate_randwalk_y = {gyro_rate_randwalk_y} deg/s/sqrt(s)')
print(f'gyro_rate_randwalk_z = {gyro_rate_randwalk_z} deg/s/sqrt(s)')
print(f'Average gyro_rate_randwalk = {gyro_rate_randwalk_avg} deg/s/sqrt(s)')
plt.plot(2,gyro_rate_randwalk_x,'bo')
plt.plot(2,gyro_rate_randwalk_y,'ro')
plt.plot(2,gyro_rate_randwalk_z,'go')
plt.show()
