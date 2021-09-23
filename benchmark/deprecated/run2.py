from os.path import dirname, abspath

import numpy as np
import scipy

ROOT = dirname(dirname(dirname(abspath(__file__))))


def bonferroni(pvals, alpha=0.05):
    m, pvals = len(pvals), np.asarray(pvals)
    return pvals < alpha / float(m)


def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)


def stat_dom(d, alpha=0.05):
    m = len(d)

    # calculate all the p values for each pairwise comparison
    pvals_better = np.ones((m, m))
    pvals_worse = np.ones((m, m))

    for i in range(m):
        for j in range(m):

            if i != j:
                # p-value less or equal to alpha means i is significantly better than j
                _, pvals_better[i, j] = scipy.stats.wilcoxon(d[i], d[j], alternative="less")

                # p-value less or equal to alpha means i is significantly worse than j
                _, pvals_worse[i, j] = scipy.stats.wilcoxon(d[i], d[j], alternative="greater")

    # use the alpha to see if we reject the null - value is sign. better or worse
    is_better = (pvals_better <= alpha)
    is_worse = (pvals_worse <= alpha)

    # make sure the special case that it is both better and worse does not occur
    invalid = np.logical_and(is_better, is_worse)
    is_better[invalid] = False
    is_worse[invalid] = False

    # now simply count how often an algorithm has better, same, or worse performance
    n_better = is_better.sum(axis=1)
    n_worse = is_worse.sum(axis=1)

    # sort the results first by being better and if tied by being less worse
    # less times worse in other words means more often with no signicant difference
    S = sorted(np.arange(m), key=lambda i: (n_better[i], -n_worse[i]), reverse=True)

    # the finals ranks of each entry
    ranks = np.full(m, -1, dtype=int)

    # now create the ranks but include if two algorithms have the results - they share the rank as an average
    i = 0
    while i < m:

        # the indices based on the sorted array S
        j = i + 1

        # check if current and next element have exactly the same values
        while j < m and n_better[S[i]] == n_better[S[j]] and n_worse[S[i]] == n_worse[S[j]]:
            # if yes increase counter to the next element
            j += 1

        # the current element
        ranks[S[i:j]] = (np.arange(i, j) + 1).mean()

        i = j

    return ranks
