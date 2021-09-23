import numpy as np

from benchmark.analyzer.analyzer import Analyzer
from benchmark.core.util import fill_forward_if_nan
from pymoo.indicators.igd import IGD
from pymoo.util.misc import from_dict


class MultiObjectiveConvergenceAnalyzer(Analyzer):

    def __init__(self, nan_if_not_available=True, **kwargs) -> None:
        super().__init__(**kwargs)
        self.nan_if_not_available = nan_if_not_available

    def do(self, data, **kwargs):
        t = []
        for entry in data:
            t.extend([e['n_evals'] for e in entry["callback"]])
        t = sorted(list(set(t)))

        hash = {}
        for k, v in enumerate(t):
            hash[v] = k

        for i, entry in enumerate(data):

            igd = IGD(entry["pf"], zero_to_one=True)

            vals = np.full(len(t), np.nan)

            for v in entry["callback"]:
                _t, F = from_dict(v, "n_evals", "opt")
                vals[hash[_t]] = igd.do(F)

            fill_forward_if_nan(vals)

            entry["n_evals"] = t
            entry["conv"] = vals
