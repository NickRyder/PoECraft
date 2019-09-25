import numpy as np
import matplotlib.pyplot as plt

def statistics(data):
    data = np.array(data)
    print("mean", np.mean(data))
    print("median", np.median(data))
    print("66 percentile", np.percentile(data, 66))
    print("75 percentile", np.percentile(data, 75))
    print("80 percentile", np.percentile(data, 80))


def discrete_pdf(data):
    #wrap as numpy array
    data = np.array(data, dtype=np.int64)

    np.bincount(data)
    data_min = np.min(data)
    data_max = np.max(data)

    data_bin_counts_clipped = np.bincount(data)[data_min:data_max + 1]

    plt.bar(np.arange(data_min, data_max + 1), data_bin_counts_clipped, width=1.0, facecolor='black', edgecolor='black')
    plt.xlabel("values")
    plt.ylabel("frequency")

def discrete_cdf(data):
    #wrap as numpy array
    data = np.array(data)
    percentiles = np.percentile(data, np.arange(0,101))
    plt.plot(np.arange(0,101), percentiles)
    plt.xlabel("percentiles")
    plt.ylabel("values")

def plot_clear():
    plt.clf()

def plot_show():
    plt.show()
