from PoECraft.item_rollers import ExplictlessItem, ExplicitModRoller
from PoECraft.utils.visualizations import statistics, discrete_cdf, plot_show
import numpy 

#Here we generate a base item which is a ilvl 100 vaal regalia with a single synthesis implicit, and 30 quality
vaal_regalia_item = ExplictlessItem("Vaal Regalia", quality = 30, implicits=["SynthesisImplicitFlatEnergyShield5_"])

#We view the implicit stats granted from this synthesis implicit
print(vaal_regalia_item.implicit_stats) #{'local_energy_shield': [[25, 25]]} 

#Now we set up the roller with the dense fossil:
vaal_regalia_dense_roller = ExplicitModRoller(vaal_regalia_item, fossil_names=["Dense Fossil"])

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


#help us understand our data
statistics(average_local_energy_shield_results)
discrete_cdf(average_local_energy_shield_results)
plot_show()