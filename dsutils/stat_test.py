__author__ = 'sidazad'

from scipy import stats
import numpy as np

def is_normal(values):
    if stats.normaltest(values)[1] < 0.05:
        return False
    return True

def get_mean_median(values):
    return np.mean(values), np.median(values)


def mann_whitney_t_test(values1, values2, ci=0.05):
    print stats.ttest_ind(values1, values2, equal_var=False)
    print stats.ttest_ind(values1, values2, equal_var=False)[1]*2
    return stats.ttest_ind(values1, values2, equal_var=False)[1]*2 >= ci

