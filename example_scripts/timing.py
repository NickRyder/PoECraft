from PoECraft.item_rollers import ExplictlessItem, ExplicitModRoller
from time import monotonic
from contextlib import contextmanager

from tqdm import tqdm


@contextmanager
def timer():
    tic = monotonic()
    yield
    print(monotonic() - tic)


# from PoECraft.utils.performance import timer


# Here we generate a base item which is a ilvl 100 vaal regalia with a single synthesis implicit, and 30 quality
vaal_regalia_item = ExplictlessItem("Vaal Regalia")

# Now we set up the roller with the dense fossil:
vaal_regalia_roller = ExplicitModRoller(vaal_regalia_item)

# before we do a batch craft, we'll do one small craft:
# This is the equivalent of using our fossil:


def roll():
    trial_N = 10 ** 7
    for _ in tqdm(range(trial_N)):
        vaal_regalia_roller.roll_item()
        # count += len([x for x in vaal_regalia_roller.affix_keys_current if "Fire" in x])
        # assert (
        #     len([x for x in vaal_regalia_roller.affix_keys_current if "Fire" in x]) < 2
        #


with timer():
    roll()
