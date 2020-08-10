from PoECraft.PoECraft._prng import bounded_rand

# from PoECraft.PoECraft._prng_numba import bounded_rand
from time import time


def _test_prng(trial_N=10 ** 2):
    tic = time()
    bound = 1000
    draws = [bounded_rand(bound) for _ in range(trial_N)]
    print(draws)
    counts = [0] * 1000
    for draw in draws:
        counts[draw] += 1 / trial_N
    abs_diffs = [abs(count - 1 / bound) for count in counts]
    print(f"max relative diff {max(abs_diffs)*bound}")
    print(f"time: {time() - tic}")


def _test_bisect():
    raise NotImplementedError


if __name__ == "__main__":
    _test_prng()

