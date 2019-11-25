from PoECraft.item_rollers import ExplictlessItem, ExplicitModRoller
from PoECraft.utils.visualizations import statistics, discrete_cdf, plot_show
import numpy 
from collections import Counter
from tqdm import tqdm

base_item = ExplictlessItem("Stygian Vise", ilvl=25)

item_roller = ExplicitModRoller(base_item)

def affix_counter_simulation(item_roller: ExplicitModRoller, trial_N = 10 ** 6):

    mod_counter = Counter()
    for trial_idx in tqdm(range(trial_N)):
        item_roller.roll_item()
        for affix_key in item_roller.affix_keys_current:
            if affix_key not in mod_counter:
                mod_counter[affix_key] = 0
            mod_counter[affix_key] += 1
    return mod_counter

def divide_counter(counter:Counter, dividend):
    divided_counter = {}
    for key, value in counter.items():
        divided_counter[key] = value/dividend
    return divided_counter


def counter_to_percentages(counter:Counter):
    total_sum = 0
    for key, value in counter.items():
        total_sum += value
    return divide_counter(counter, total_sum)

trial_N = 10 ** 6
mod_counter = affix_counter_simulation(item_roller, trial_N = trial_N)
print(divide_counter(mod_counter, trial_N))