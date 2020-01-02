from PoECraft.item_rollers import ExplictlessItem, ExplicitModRoller
from PoECraft.utils.visualizations import statistics, discrete_cdf, plot_show
import numpy

# Here we generate a base item which is a ilvl 100 vaal regalia with a single synthesis implicit, and 30 quality
hubris_circlet_item = ExplictlessItem("Hubris Circlet", quality=20, influences=[])

# We view the implicit stats granted from this synthesis implicit
print(hubris_circlet_item.implicit_stats)  # {'local_energy_shield': [[25, 25]]}

# Now we set up the roller with the dense fossil:
hubris_circlet_roller = ExplicitModRoller(
    hubris_circlet_item, fossil_names=["Bound Fossil"]
)

# before we do a batch craft, we'll do one small craft:
# This is the equivalent of using our fossil:
hubris_circlet_roller.roll_item()
print(f"First roll's affix names: {hubris_circlet_roller.affix_keys_current}")
print(f"First roll's total stats: {hubris_circlet_roller.get_total_stats()}")

# We pick the number of times to use our dense fossil
trial_N = 10 ** 1


print("starting crafting simulator")
for i in range(trial_N):
    # roll the item
    hubris_circlet_roller.roll_item()
    # get the stats from the rolled item
    print(hubris_circlet_roller.affix_keys_current)


