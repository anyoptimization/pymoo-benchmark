from benchmark.core.benchmark import Benchmark
from benchmark.core.recoder import DefaultMultiObjectiveRecorder

from pymoo.algorithms.moo.moead import MOEAD
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.experimental.algorithms.gde3 import GDE3
from pymoo.factory import get_reference_directions
from pymoo.problems.many import WFG1
from pymoo.problems.multi import ZDT1, ZDT2, ZDT3, ZDT4, ZDT6, Kursawe


# UnConstrained Multi-Objective - ucmo
def setup(n_runs=31):

    # what should be recorded in each iteration
    recorder = DefaultMultiObjectiveRecorder()

    # initialize the benchmark
    benchmark = Benchmark(n_runs=n_runs, recorder=recorder)

    # -----------------------------------------------------
    # PROBLEMS
    # -----------------------------------------------------

    benchmark.add_problem("zdt1", ZDT1(), termination=("n_gen", 200))
    benchmark.add_problem("zdt2", ZDT2(), termination=("n_gen", 200))
    benchmark.add_problem("zdt3", ZDT3(), termination=("n_gen", 200))
    benchmark.add_problem("zdt4", ZDT4(), termination=("n_gen", 200))
    benchmark.add_problem("zdt6", ZDT6(), termination=("n_gen", 400))
    benchmark.add_problem("kur", Kursawe(), termination=("n_gen", 100))
    benchmark.add_problem("wfg1", WFG1(10, 2), termination=("n_gen", 200))

    # -----------------------------------------------------
    # ALGORITHMS
    # -----------------------------------------------------
    ref_dirs = get_reference_directions("das-dennis", 2, n_partitions=99)

    benchmark.add_algorithm("nsga2", NSGA2())
    benchmark.add_algorithm("gde3", GDE3())
    benchmark.add_algorithm("moead", MOEAD(ref_dirs))
    benchmark.add_algorithm("nsga3", NSGA3(ref_dirs))

    return benchmark
