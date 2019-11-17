This project is intended to be a Python Package focused on performant crafting simulations for Path of Exile. All of the data is gathered from [RePoE](https://github.com/brather1ng/RePoE), which parses the `content.ggpk` file into json. 

# Crafting Model
This project presumes the following model in which the game crafts items.
- **Crafts one affix at a time** - Even when a currency orb puts multiple affixes on an item, it accomplishes this by randomly selecting a mod from the available mod pool one at time
- **1:4:7 split for total number of affixes** - For items with a max of 6 mods, extensive data farming has shown that there is a 1/12 chance for 6 mods, 4/12 chance for 5 mods, and 7/12 chance for 6 mods

## Affix Weights
There are multiple entities which influence the affix weighting.
- **Mod Groups** - In `RePoE.mods` every affix has a property `group`. Only one total mod can show up from each group on the item
- **Tags** - Every base item has tags on it which affect the weights in different ways:
    - **Base Item Tags** - Every base item comes with tags which can be found in `RePoE.base_items` under the property `tags`. 
    - **Added Tags** - Affixes can add tags upon being put on an item, which can be found in `RePoE.mods` under the property `adds_tags`
    - **Tags Influence Spawn Weights** - For each mod it comes with a list of `spawn_weights`, which associate to some tags the raw weight of the mod spawning. The game reads the `spawn_weights` in the order they are listed, and selects the `spawn_weight` corresponding to the first `tag` which is on the item.
    - **Generation Weights** - In `RePoE.mods` one can find the property `generation_weights`, which is a list of tags. The game looks through the list from top to bottom, and stops when it finds a `tag` already on the item. Then it takes `value`/100 and multiples the `spawn_weight`.
- **Mod Type Tags** - These behave very similarly to tags, and are mainly used in fossil crafting
    - **Mod to Mod Type** - Every affix in `RePoE.mods` has a property `type` which corresponds to a mod type found in `RePoE.mod_types`
    - **Mod Types to Tags** - Every mod type in `RePoE.mod_types` has a propety `tags` which corresponds to `spawn_weights`. These mod type tags affect spawn weight *before* the mod is rolled. 
    - **Mod Type Tag Multipliers in Fossils** - In `RePoE.fossils` there are `positive_mod_weights` and `negative_mod_weights` which after being divided by 100 tell the generation weight applied to a `spawn_weight` if that mod has that mod type tag.
- **Prefix/Suffix Cap**
    - Some items have a 1/1 cap, 2/2 cap, 3/3 cap, or 4/4 cap. Once the cap is reached, all other prefixes or suffixes are removed from the pool.
## Unknown Effects
- Currently do not have a working model of how *Sanctified Fossils* work


# Performant Crafting Simulator
The crafting process at it's core is a markov chain - one can imagine starting with a blank base and then rolling a random first mod, whose probabilities are described above. Then for each one of those we get new probabilities based on tags, groups, etc. There are two basic approaches to evaluating a function over this probability space
- **Exact Computation** - 
