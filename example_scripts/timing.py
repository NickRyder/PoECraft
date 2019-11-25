
from PoECraft.item_rollers import ExplictlessItem, ExplicitModRoller
from PoECraft.utils.visualizations import statistics, discrete_cdf, plot_show
from PoECraft.utils.performance import timer
import numpy 


#Here we generate a base item which is a ilvl 100 vaal regalia with a single synthesis implicit, and 30 quality
vaal_regalia_item = ExplictlessItem("Vaal Regalia")

#Now we set up the roller with the dense fossil:
vaal_regalia_roller = ExplicitModRoller(vaal_regalia_item)

#before we do a batch craft, we'll do one small craft:
#This is the equivalent of using our fossil:

trial_N = 10 ** 4
with timer(f" {trial_N} rolls"):
    for _ in range(trial_N):
        vaal_regalia_roller.roll_item()
