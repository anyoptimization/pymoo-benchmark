import json
import os
import pickle

import numpy as np

from benchmark.core.util import at_least2d
from pymoo.util.misc import from_dict


class IO:

    def __init__(self, folder) -> None:
        super().__init__()
        self.folder = folder


class DefaultWriter(IO):

    def write(self, entry):

        problem, algorithm, run, callback = from_dict(entry, "problem", "algorithm", "run", "callback")

        folder = os.path.join(self.folder, algorithm, problem)
        if not os.path.exists(folder):
            os.makedirs(folder)

        for key in ["X", "CV", "F"]:
            np.savetxt(os.path.join(folder, f"{run}.{key.lower()}"), entry.get(key))

        path = os.path.join(folder, f"{run}.json")
        with open(path, 'w') as f:
            json.dump(entry.get("info"), f, ensure_ascii=False, indent=4)

        if callback is not None:
            pickle.dump(callback, open(os.path.join(folder, f"{run}.dat"), 'wb'))


class DefaultLoader(IO):

    def load(self, entry):

        problem, algorithm, run = from_dict(entry, "problem", "algorithm", "run")

        entry = dict(entry)
        del entry["args"]

        path = os.path.join(self.folder, algorithm, problem)
        if os.path.exists(path):

            for key in ["X", "CV", "F"]:
                file = os.path.join(path, f"{run}.{key.lower()}")
                if os.path.exists(file):
                    try:
                        vals = np.loadtxt(file)
                    except:
                        return None
                    if len(vals.shape) == 0:
                        vals = np.array([float(vals)])
                    entry[key] = at_least2d(vals, expand="r")
                else:
                    return None

            file = os.path.join(path, f"{run}.dat")
            if os.path.exists(file):
                entry["callback"] = pickle.load(open(file, 'rb'))

            return entry


class DefaultExtractor:

    def extract(self, param, res):
        opt = res.opt

        entry = {
            "problem": param["problem"],
            "algorithm": param["algorithm"],
            "run": param["run"],
            "X": opt.get("X"),
            "CV": opt.get("CV"),
            "F": opt.get("F"),
            "info": dict(time=res.exec_time),
        }

        if res.algorithm.callback is not None:
            entry["callback"] = res.algorithm.callback.data,

        return entry