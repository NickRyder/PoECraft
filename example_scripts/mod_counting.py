from PoECraft.item_rollers import ExplictlessItem, ExplicitModRoller
from PoECraft.utils.visualizations import statistics, discrete_cdf, plot_show
import numpy 


raise NotImplementedError("This script is defunct.")

#Here we generate a base item which is a ilvl 100 vaal regalia with a single synthesis implicit, and 30 quality
stygian_vise_item = ExplictlessItem("Stygian Vise")

#Now we set up the roller with the dense fossil:
vaal_regalia_dense_roller = ExplicitModRoller(stygian_vise_item, fossil_names=["Dense Fossil"])

#before we do a batch craft, we'll do one small craft:
#This is the equivalent of using our fossil:
vaal_regalia_dense_roller.roll_item()
print(f"First roll's affix names: {vaal_regalia_dense_roller.affix_keys_current}")
print(f"First roll's total stats: {vaal_regalia_dense_roller.get_total_stats()}")

#We pick the number of times to use our dense fossil
trial_N = 10 ** 4

#define a small helper function to extract the average local energy shield:
def average_one_stat(stat_values):
    stat_sums = stat_values.sum(axis=0)
    return numpy.mean(stat_sums)

print("starting crafting simulator")
#Main loop to roll the item:
average_local_energy_shield_results = []
for i in range(trial_N):
    #roll the item
    vaal_regalia_dense_roller.roll_item()
    #get the stats from the rolled item
    roll_stats = vaal_regalia_dense_roller.get_total_stats()
    #get local_energy_shield from these stats
    roll_local_energy_sheild = roll_stats.get("local_energy_shield", [[0,0]])
    #average the rolls and record
    average_local_energy_shield_results.append(average_one_stat(roll_local_energy_sheild))


def affix_counter_simulation(item_class, trial_N = 1000000):

    mod_counter = Counter()

    for trial_idx in tqdm(range(trial_N)):
        chaos_item(item_class)
        for affix_key in item_class.affix_keys:
            if affix_key not in mod_counter:
                mod_counter[affix_key] = 0
            mod_counter[affix_key] += 1
    for key in mod_counter.keys():
        mod_counter[key] = mod_counter[key]

    return mod_counter




#help us understand our data
statistics(average_local_energy_shield_results)
discrete_cdf(average_local_energy_shield_results)
plot_show()