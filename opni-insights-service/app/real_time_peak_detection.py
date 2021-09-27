import numpy as np


class real_time_peak_detection:
    def __init__(self, window, threshold, influence):
        self.y = []
        self.length = len(self.y)
        self.window = window
        self.threshold = threshold
        self.influence = influence

    def thresholding_algo(self, new_value):
        self.y.append(new_value)
        i = len(self.y) - 1
        self.length = len(self.y)
        if i < self.window:
            return 0
        elif i == self.window:
            self.signals = [0] * len(self.y)
            self.filteredY = np.array(self.y).tolist()
            self.avgFilter = [0] * len(self.y)
            self.stdFilter = [0] * len(self.y)
            self.avgFilter[self.window] = np.mean(self.y[0 : self.lag]).tolist()
            self.stdFilter[self.window] = np.std(self.y[0 : self.lag]).tolist()
            return 0

        if self.y[i] > self.avgFilter[i - 1] and (
            (self.y[i] - self.avgFilter[i - 1])
            > (self.threshold * self.stdFilter[i - 1])
        ):
            self.signals.append(1)
            self.filteredY.append(
                self.influence * self.y[i]
                + (1 - self.influence) * self.filteredY[i - 1]
            )
            self.avgFilter.append(np.mean(self.filteredY[(i - self.window) : i]))
            self.stdFilter.append(np.std(self.filteredY[(i - self.window) : i]))
        else:
            self.signals.append(0)
            self.filteredY.append(self.y[i])
            self.avgFilter.append(np.mean(self.filteredY[(i - self.window) : i]))
            self.stdFilter.append(np.std(self.filteredY[(i - self.window) : i]))

        return self.signals[i]
