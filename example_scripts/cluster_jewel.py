from PoECraft.item_rollers import ExplictlessItem, ExplicitModRoller
from PoECraft.utils.visualizations import statistics, discrete_cdf, plot_show
import numpy

cluster_jewel_item = ExplictlessItem(
    "Medium Cluster Jewel", quality=30, extra_tags=["affliction_aura"]
)

cluster_jewel_roller = ExplicitModRoller(cluster_jewel_item)

# before we do a batch craft, we'll do one small craft:
# This is the equivalent of using our fossil:
cluster_jewel_roller.roll_item()
print(f"First roll's affix names: {cluster_jewel_roller.affix_keys_current}")

# We pick the number of times to use our dense fossil
trial_N = 10 ** 4

print("starting crafting simulator")
# Main loop to roll the item:
average_local_energy_shield_results = []
for i in range(trial_N):
    # roll the item
    cluster_jewel_roller.roll_item()
