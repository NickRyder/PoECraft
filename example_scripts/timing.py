from PoECraft.item_rollers import ExplictlessItem, ExplicitModRoller

from tqdm import tqdm

from poe_craft.rust_scripts import test_roll_batch

from PoECraft.utils.performance import timer

# Here we generate a base item which is a ilvl 100 vaal regalia with a single synthesis implicit, and 30 quality
vaal_regalia_item = ExplictlessItem("Vaal Regalia")

# Now we set up the roller with the dense fossil:
vaal_regalia_roller = ExplicitModRoller(vaal_regalia_item)


def roll(trial_n):
    for _ in tqdm(range(trial_n)):
        vaal_regalia_roller.roll_item()


trial_n = 10 ** 7

with timer():
    roll(trial_n)

# we get a 2.6x speed up from writing our simple script in rust
with timer():
    test_roll_batch(vaal_regalia_roller, trial_n)
