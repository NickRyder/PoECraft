from RePoE import mods

'''This module is intended to take in a base item and construct a list of all possible mods that can roll on that base item
    through currency crafting in PoE. Excludes not spawnable mods like league specific mods and master-crafts'''


def _get_positive_spawn_weight_tags(affix, starting_tags) -> set:
    '''
    Takes in an affix dict and a set of starting_tags
    Finds all positive weight tags in spawn_weights
    Ignores all spawn_weights if one of our starting tags forces a spawn_weight of zero
    '''
    pos_spawn_weight_tags = set()
    for spawn_weight in affix["spawn_weights"]:
        if spawn_weight["weight"] == 0:
            #We read the spawn_weights in order they are listed
            #If we find one which gives matches a tag we have we in starting_tags, we ignore
            if spawn_weight["tag"] in starting_tags:
                break
        elif spawn_weight["weight"] > 0:
            pos_spawn_weight_tags.add(spawn_weight["tag"])
        else:
            raise ValueError("spawn_weights should be nonnegative")

    return pos_spawn_weight_tags


# TODO: MAYBE?: this should take in some generic item type and calculate the possible mods that 
# can roll on that item. This will allow support for items which have some odd non-spawnable
# mods on them (like league specific mod drops)
# TODO: currently includes more tags than necessary (includes all possible relevant tags)
def generate_all_possible_affixes_and_tags(starting_tags, mod_pool):
    '''
    :param starting_tags: set containing all the starting_tags on the item we are rolling
    :param mod_pool: a dictionary containing all possible mods possible to roll on our item
    :return: spawn_tags, affixes
            spawn_tags -   all possible tags which can spawn from rolling this item
            affixes -      final mod pool of all things that can spawn
    '''

    affixes = {}
    added_new_affixes = True

    while added_new_affixes:
    
        added_new_affixes = False

        total_pos_spawn_weights_tags = set()

        for key, affix in mod_pool.items():
            # We want to only consider affixes which have a positive spawn weight for one of our potential tags
            # We also want to keep track of which tags affect this affix, whether they show up as any spawn_weight (even 0)
            # or they show up as a generation_weight

            #important that we only block starting_tags here, as there could be routes of crafting which spawn some tags and not others which affects blocking
            pos_spawn_weights_tags = _get_positive_spawn_weight_tags(affix, starting_tags)
            total_pos_spawn_weights_tags = total_pos_spawn_weights_tags.union(pos_spawn_weights_tags)

            spawn_weight_tags = set([spawn_weight["tag"] for spawn_weight in affix["spawn_weights"]])
            assert pos_spawn_weights_tags.issubset(spawn_weight_tags), "pos_spawn_weight_tags should be subset of spawn_weight_tags"

            add_tags = set()
            if len(pos_spawn_weights_tags) > 0:
                if key not in affixes:
                    affixes[key] = affix
                    added_new_affixes = True

                add_tags = add_tags.union(set(affix["adds_tags"]))

    spawn_tags = set(starting_tags.copy())
    spawn_tags = spawn_tags.union(add_tags)    

    return spawn_tags, affixes

def _get_spawnable_mods_for_item(domains,ilvl):
    '''
    Trim by removing all affixes that can't be crafted and are in the wrong domains
    '''

    spawnable_mods = {}

    for affix_key in list(mods.keys()):
        affix_value = mods[affix_key]
        is_prefix_or_suffix = affix_value["generation_type"] in ["prefix", "suffix"]
        is_in_domains = affix_value["domain"] in domains
        is_not_essence = not affix_value["is_essence_only"]
        is_ilvl_appropriate = affix_value["required_level"] <= ilvl


        if is_prefix_or_suffix and is_in_domains and is_not_essence and is_ilvl_appropriate:
            spawnable_mods[affix_key] = affix_value
    return spawnable_mods



def collect_mods_and_tags(starting_tags, appended_mod_dictionary, domains, ilvl):
    spawnable_mods = _get_spawnable_mods_for_item(domains, ilvl)
    mod_pool = {**spawnable_mods, **appended_mod_dictionary}

    #further reduce the mod pool by looking at spawn weights and tags
    realized_spawn_tags, mod_pool = generate_all_possible_affixes_and_tags(starting_tags, mod_pool)

    return {**mod_pool, **appended_mod_dictionary}, realized_spawn_tags
