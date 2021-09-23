from copy import deepcopy
from math import ceil

import numpy as np

from benchmark.core.io import DefaultExtractor
from pymoo.optimize import minimize
from pymoo.util.misc import from_dict


class Benchmark:

    def __init__(self,
                 n_runs=31,
                 recorder=None,
                 default_termination=None):

        super().__init__()

        self.default_callback = recorder
        self.default_runs = n_runs
        self.default_termination = default_termination

        self.writer = None
        self.loader = None
        self.extractor = None

        self.problems = {}
        self.runs = []

        self.results = []

    def add_problem(self, label, problem, termination=None):
        self.problems[label] = dict(label=label, obj=problem, termination=termination)

    def add_algorithm(self, label, algorithm, problems=None, n_runs=None, termination=None, callback=None):

        if callback is None:
            callback = self.default_callback

        if problems is None:

            if len(self.problems) == 0:
                raise Exception("No Problem have been added to run the algorithm on!")

            problems = list(self.problems.keys())
        elif not isinstance(problems, list):
            problems = [problems]

        if n_runs is None:
            n_runs = self.default_runs

        for problem in problems:

            if termination is None:
                termination = self.problems[problem]["termination"]

            if termination is None:
                termination = self.default_termination

            for run in range(1, n_runs + 1):
                args = dict(problem=self.problems[problem]["obj"], algorithm=algorithm, termination=termination,
                            seed=run, callback=callback)
                e = dict(problem=problem, algorithm=label, run=run, args=args)
                self.runs.append(e)

    def run(self, ordered_by="problem", batch=None, verbose=True, **kwargs):

        params = self.runs
        params.sort(key=lambda x: x[ordered_by])

        if batch is not None:
            batch, n_batches = [int(e) for e in batch.split("/")]
            assert 0 < batch <= n_batches, f"Batch number must be greater than 0 but less or equal to number of batches!"

            batch_size = ceil(len(params) / n_batches)
            i, j = (batch - 1) * batch_size, batch * batch_size
            params = params[i:j]

        if "extractor" not in kwargs:
            kwargs["extractor"] = DefaultExtractor()

        self.results = run_looped(params, batch=batch, verbose=verbose, **kwargs)
        # self.results = run_parallel(kwargs.get("starmap"), self, params, batch=batch, verbose=verbose, **kwargs)

        return self.results


# ---------------------------------------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------------------------------------


def run_looped(params,
               batch,
               verbose=False,
               loader=None,
               writer=None,
               extractor=None,
               mem_free=False,
               run_if_loading_fails=True,
               exception_if_not_available=False,
               **kwargs):

    ret = []
    for i, param in enumerate(params):

        problem, algorithm, run, args = from_dict(param, "problem", "algorithm", "run", "args")

        if verbose:
            line = f"{i + 1}/{len(params)} | {algorithm} | {problem} | {run}"
            if batch is not None:
                line = f"{batch} | {line}"
            print(line, end="")

        entry = None

        if loader is not None:
            entry = loader.load(param)
            if entry is not None:
                if verbose:
                    print(f" | Loaded")

        if entry is None:
            if run_if_loading_fails:

                res = execute(param)

                entry = extractor.extract(param, res)

                if verbose:
                    print(f" | {np.round(res.exec_time, 6)} s")

                if writer is not None:
                    writer.write(entry)

            else:
                if exception_if_not_available:
                    assert entry is not None, f"Error while loading {param}"
                if verbose:
                    print(f" | Failed")

        # if the algorithm should not keep anything in memory and just write files do that
        if entry is not None and not mem_free:
            ret.append(entry)

    return ret


def execute(param):
    args = deepcopy(param['args'])

    problem = args.pop("problem")
    algorithm = args.pop("algorithm")
    res = minimize(problem, algorithm, return_least_infeasible=True, **args)
    return res


