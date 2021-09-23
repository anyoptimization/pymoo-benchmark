import argparse
import sys
from os.path import join, dirname, abspath

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from benchmark.benchmarks import get_benchmark, all_benchmarks
from benchmark.config import ROOT
from benchmark.core.io import DefaultWriter, DefaultLoader

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='The tool to execute pymoo benchmarks')
    parser.add_argument('benchmark', help=f'Name of the benchmark: {all_benchmarks}')
    parser.add_argument('--batch', default=None, help=f'A string defining the batch to run, eg. 3/16 to run the 3rd batch out of 16.')
    parser.add_argument('--export', action='store_true', help="Exports each of the results to a zip file.")

    args = parser.parse_args()

    # the name of the benchmark
    name = args.benchmark

    # load the benchmark and its properties
    benchmark = get_benchmark(name)

    # the folder where the data should be written to or loaded from
    FOLDER = join(ROOT, "data", name)

    # the loader for file that have been already saved
    LOADER = DefaultLoader(FOLDER)

    # the file writer to store the runs
    WRITER = DefaultWriter(FOLDER)

    # -----------------------------------------------------
    # RUN (or load if data already available)
    # -----------------------------------------------------

    results = benchmark.run(writer=WRITER,
                            loader=LOADER,
                            run_if_loading_fails=True,
                            batch=args.batch)

    print("sdfsf")
