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
CSV_FILENAME = 'test_imu.csv'
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
# that is, between  10^-1 < tau < 20 for the test_imu file 
# 
idx_start = np.where(taux < 0.1)[0][-1]
idx_end = np.where(taux > 20)[0][0]
print(idx_start,idx_end)
logtaux = np.log(taux[idx_start:idx_end])
logadx = np.log(adx[idx_start:idx_end])
coeffs = np.polyfit(logtaux,logadx, deg=1)
#coeffs = np.polyfit(taux,adx, deg=3)
poly = np.poly1d(coeffs)
yfit = lambda x: np.exp(poly(np.log(taux))) #np.log(x)))
#yfit = lambda x: np.exp(poly(taux)) #np.log(x)))
plt.plot(taux,yfit(taux))
#plt.loglog(taux,yfit(taux))
plt.show()
