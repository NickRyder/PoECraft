from PoECraft.item_rollers import ExplictlessItem, ExplicitModRoller
from PoECraft.utils.visualizations import statistics, discrete_cdf, plot_show
import numpy 
from collections import Counter
from tqdm import tqdm

stygian_vise_item = ExplictlessItem("Stygian Vise", ilvl=84)

stygian_vise_roller = ExplicitModRoller(stygian_vise_item)

def affix_counter_simulation(item_roller: ExplicitModRoller, trial_N = 10 ** 6):

    mod_counter = Counter()
    for trial_idx in tqdm(range(trial_N)):
        item_roller.roll_item()
        for affix_key in item_roller.affix_keys_current:
            if affix_key not in mod_counter:
                mod_counter[affix_key] = 0
            mod_counter[affix_key] += 1
    return mod_counter

def counter_to_percentages(counter:Counter):
    total_sum = 0
    for key, value in counter.items():
        total_sum += value
    percentages = {}
    for key, value in counter.items():
        percentages[key] = value / total_sum
    return percentages
    


mod_counter = affix_counter_simulation(stygian_vise_roller, trial_N = 10 ** 5)

print(counter_to_percentages(mod_counter))