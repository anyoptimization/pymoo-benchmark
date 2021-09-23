import importlib
import os


def get_benchmark(name, **kwargs):
    try:
        module = importlib.import_module(f"benchmark.benchmarks.{name}")
        return getattr(module, "setup")(**kwargs)
    except:
        raise Exception(f"Benchmark {name} not found.")


def all_benchmarks():
    ret = []
    for fname in os.listdir(os.path.dirname(__file__)):
        if fname.endswith(".py") and fname != '__init__.py':
            ret.append(fname)
    return ret
