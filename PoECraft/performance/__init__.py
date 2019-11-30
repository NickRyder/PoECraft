from PoECraft.performance._prng import bounded_rand


def _test_prng(trial_N = 10 ** 8):
    bound = 1000
    draws = [bounded_rand(bound) for _ in range(trial_N)]
    counts = [0] * 1000
    for draw in draws:
        counts[draw] += 1 / trial_N
    abs_diffs = [abs(count - 1 / bound) for count in counts]
    print(f"max relative diff {max(abs_diffs)*bound}")

if __name__=="__main__":
    _test_prng()