
from PoECraft.item_rollers import ExplictlessItem, ExplicitModRoller
from PoECraft.utils.visualizations import statistics, discrete_cdf, plot_show
from PoECraft.utils.performance import timer
import numpy 


#Here we generate a base item which is a ilvl 100 vaal regalia with a single synthesis implicit, and 30 quality
vaal_regalia_item = ExplictlessItem("Vaal Regalia")

#Now we set up the roller with the dense fossil:
vaal_regalia_dense_roller = ExplicitModRoller(vaal_regalia_item)

#before we do a batch craft, we'll do one small craft:
#This is the equivalent of using our fossil:

for _ in range(5):
    with timer("whole roll"):
        vaal_regalia_dense_roller.roll_item()
