

from os.path import join, basename

import numpy as np
import scipy.stats
from prettytable import PrettyTable
from scipy.stats import anderson_ksamp

from benchmark.analyzer.groupby import GroupBy
from benchmark.analyzer.moo import MultiObjectiveAnalyzer
from benchmark.benchmarks import get_benchmark
from benchmark.config import ROOT
from benchmark.core.io import DefaultWriter, DefaultLoader
from benchmark.core.util import filter_by
from benchmark.deprecated.run2 import argsort, stat_dom

if __name__ == "__main__":

    # the benchmark to be executed
    benchmark = get_benchmark("ucmo")

    # the folder where the data are at
    FOLDER = join(ROOT, "data", basename(__file__)[:-3])

    # the loader for file that have been already saved
    LOADER = DefaultLoader(FOLDER)

    # the file writer for the runs
    WRITER = DefaultWriter(FOLDER)

    # -----------------------------------------------------
    # RUN (or load if data already available)
    # -----------------------------------------------------

    results = benchmark.run(writer=WRITER,
                            loader=LOADER,
                            run_if_loading_fails=False)

    # -----------------------------------------------------
    # ANALYZE
    # -----------------------------------------------------

    ALPHA = 0.05

    METRIC = "igd"

    # set the igd values for each of the problems
    MultiObjectiveAnalyzer().run(results, benchmark=benchmark, inplace=True)

    # now aggregate all the runs to have some representative values
    attrs = [(METRIC, np.array, METRIC),
             (METRIC, np.mean, "avg"),
             (METRIC, np.std, "std")]

    groups = GroupBy(attrs).run(results, group_by=["problem", "algorithm"])

    ranks = {}
    for scope, d in filter_by(groups, ["problem"], return_group=True):
        perf = [e[METRIC] for e in d]
        ranks[scope["problem"]] = stat_dom(perf)

    for scope, d in filter_by(groups, ["problem"], return_group=True):
        m = len(d)

        # calculate all the pvals for each pairwise comparison
        M = np.ones((m, m))
        for i in range(m):
            for j in range(m):
                if i != j:
                    _, _, M[i, j] = anderson_ksamp((d[i][METRIC], d[j][METRIC]))

        # FWER bonferroni correction here
        for i in range(m):
            M[i] = M[i] * m

        # calc. if the H0 is rejected or not
        M = M >= ALPHA

        # the average performance of each algorithm
        avg = [d[i][METRIC].mean() for i in range(m)]

        # sorted by their average performance
        sorted_by_avg = argsort(avg)

        # are all the relations in fact transitive?
        is_transitive = check_transitivity(M)

        if is_transitive:
            similar = [list(np.where(row)[0]) for row in M]

            groups = []

            I = list(sorted_by_avg)

            while len(I) > 0:
                j = I.pop(0)
                S = similar[j]
                I = [i for i in I if i not in S]
                groups.append(S)

        else:

            # number of times an algorithm is significantly score than others
            score = np.zeros(m, dtype=int)

            # for each algorithm
            for i in range(m):

                # check all other algorithms
                for j in range(m):

                    # if the algorithm performed significantly worse
                    if avg[j] > avg[i] and not M[j, i]:
                        score[i] += 1

            groups = {}
            for i, e in enumerate(score):
                if e not in groups:
                    groups[e] = []
                groups[e].append(i)

            groups = [groups[e] for e in sorted(groups.keys())[::-1]]

        rank = np.full(m, -1.0)

        cnt = 1
        for group in groups:
            rank[group] = np.arange(cnt, cnt + len(group)).mean()
            cnt += len(group)

        ranks[scope["problem"]] = rank

    for scope, d in filter_by(groups, ["problem"], return_group=True):

        # find the best algorithm for this problem
        l = sorted(d, key=lambda x: x["avg"])
        best = l[0][METRIC]

        t = PrettyTable()
        t.title = scope["problem"]
        t.field_names = ['Algorithm', 'avg', 'std', 'shapiro', 'levene', 't-test', 'wilcoxon']

        for i, e in enumerate(l):
            f = e[METRIC]

            _, pval = scipy.stats.shapiro(f)
            shapiro = "*" if pval >= 0.01 else ""

            _, pval = scipy.stats.levene(best, f)
            levene = "* (%.3f)" % pval if pval >= 0.05 else ""

            _, pval = scipy.stats.ttest_ind(f, best, alternative="greater")
            ttest = "* (%.3f)" % pval if pval >= 0.05 else ""

            if len(best) == len(f):
                _, pval = scipy.stats.wilcoxon(f, best, zero_method="zsplit", alternative="greater")
                wilcoxon = "* (%.3f)" % pval if pval >= 0.05 else ""
            else:
                wilcoxon = "x"

            t.add_row([e["algorithm"], "%.10f" % e["avg"], "%.10f" % e["std"], shapiro, levene, ttest, wilcoxon])

        print(t)
        print()
