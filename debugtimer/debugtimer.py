import time

class TimeAccumulator:
    """
    Utility for accumulating time over multiple separate runs.
    Each time this is used in a context manager, it increments the total duration.
    """
    __slots__ = ("duration", "num_calls", "start")

    def __init__(self):
        self.duration = 0.0
        self.num_calls = 0

    def __enter__(self):
        self.num_calls += 1
        self.start = time.perf_counter()
    
    def __exit__(self, exc_type, exc_value, traceback):
        incremental_duration = time.perf_counter() - self.start
        self.duration += incremental_duration

class DebugTimer:
    """
    Utility for measuring how much time it takes to run a code block.
    When used as a context manager, it will measure the overall duration of the code in that block.
    Provides "accumulator" utilities to measure total running time of sub-blocks (including within loops).

    Args:
        name: An optional string to name the code block, which will be printed when complete
        accumulator_names: Iterable of names to give the accumulators (if you want any). You can then refer
            to the accumulator by name with self.accumulators[name].
        silent: Whether to print results upon completion or not. Defaults to False.

    Examples:

    simplest possible usage
    >>> with DebugTimer():
    >>>     1 + 2

    using accumulators
    >>> with DebugTimer(name="loop", accumulator_names=["func1", "func2"]) as timer:
    >>>     for i in range(1000):
    >>>         with timer.accumlators["func1"]:
    >>>             func1(i)
    >>>         some_other_func(i)
    >>>         with timer.accumlators["func2"]:
    >>>             func2(i)
    """
    __slots__ = ("name", "silent", "accumulators", "start", "duration_sec")

    def __init__(self, name: Optional[str]=None, accumulator_names: Optional[list[str]]=None, silent: bool=False):
        self.name = name
        self.silent = silent
        self.accumulators = {name: TimeAccumulator() for name in accumulator_names or []}
        # self.num_calls = 0
    
    def __enter__(self):
        # self.num_calls += 1
        self.start = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        end = time.perf_counter()
        self.duration_sec = duration_sec = end - self.start
        # format and print the durations
        if not self.silent:
            for coeff, unit in [(1e-9, "ns"), (1e-6, "us"), (1e-3, "ms"), (1, "s"), (60, "m"), (60*60, "h")]:
                duration = duration_sec / coeff
                if 0 < math.log10(duration) < 3:
                    break
            duration_fmt = f"{duration:.3f} {unit}"
            name = f" '{self.name}' " if self.name is not None else ' '
            print(f"Code block{name}took {duration_fmt}")
            for name, accumulator in self.accumulators.items():
                if accumulator.num_calls > 0:
                    duration_sec = accumulator.duration
                    for coeff, unit in [(1e-9, "ns"), (1e-6, "μs"), (1e-3, "ms"), (1, "s"), (60, "m"), (60*60, "h")]:
                        duration = duration_sec / coeff
                        if 0 < math.log10(duration) < 3:
                            break
                    duration_total_fmt = f"{duration:.3f} {unit}"
                    duration_sec = accumulator.duration / accumulator.num_calls
                    for coeff, unit in [(1e-9, "ns"), (1e-6, "μs"), (1e-3, "ms"), (1, "s"), (60, "m"), (60*60, "h")]:
                        duration = duration_sec / coeff
                        if 0 < math.log10(duration) < 3:
                            break
                    duration_per_call_fmt = f"{duration:.3f} {unit}"
                    name = f" '{name}' " if name is not None else ' '
                    # print(f"\tAccumlator{name}took {duration_fmt} (... per call)")
                    print(f"\tAccumlator{name}took {duration_total_fmt} out of {accumulator.num_calls} calls ({duration_per_call_fmt} per call)")

