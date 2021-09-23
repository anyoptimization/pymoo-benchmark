import numpy as np
import scipy.stats
from prettytable import PrettyTable

from benchmark.benchmarks import get_benchmark

if __name__ == "__main__":

    benchmark = get_benchmark("ucmo")

    results = benchmark.run(writer=WRITER,
                            loader=LOADER,
                            run_if_loading_fails=True)


    # set the igd values for each of the problems
    MultiObjectiveAnalyzer().run(results, benchmark=benchmark, inplace=True)

    # now aggregate all the runs to have some representative values
    attrs = [("igd", np.array, "igd"),
             ("igd", np.mean, "avg"),
             ("igd", np.std, "std")]

    igd = GroupBy(attrs).run(results, group_by=["problem", "algorithm"])

    for scope, d in filter_by(igd, ["problem"], return_group=True):

        # find the best algorithm for this problem
        l = sorted(d, key=lambda x: x["avg"])
        best = l[0]["igd"]

        t = PrettyTable()
        t.title = scope["problem"]
        t.field_names = ['Algorithm', 'avg', 'std', 'shapiro', 'levene', 't-test', 'wilcoxon']

        for i, e in enumerate(l):
            f = e["igd"]

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
