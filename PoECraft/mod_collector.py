from RePoE import mods

'''This module is intended to take in a base item and construct a list of all possible mods that can roll on that base item
    through currency crafting in PoE. Excludes not spawnable mods like league specific mods and master-crafts'''


def _get_positive_spawn_weight_tags(affix, starting_tags) -> set:
    '''
    Takes in an affix dict and a set of starting_tags
    Finds all positive weight tags in spawn_weights

    When we run into one of our relevant starting_tags, we stop.
    This is because that condition will always be hit, no matter what tradjectory we take
    '''
    pos_spawn_weight_tags = set()
    for spawn_weight in affix["spawn_weights"]:

        if spawn_weight["weight"] == 0:
            pass
        elif spawn_weight["weight"] > 0:
            pos_spawn_weight_tags.add(spawn_weight["tag"])
        else:
            raise ValueError("spawn_weights should be nonnegative")
        
        if spawn_weight["tag"] in starting_tags:
            return pos_spawn_weight_tags, spawn_weight["tag"]

    raise ValueError("default should be in starting_tags and in the weights for this affix")


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
    
    added_tags = set()
    relevant_start_tags = set()
    while added_new_affixes:
    
        added_new_affixes = False

        current_tag_pool = added_tags.union(starting_tags)

        for key, affix in mod_pool.items():

            #important that we only block starting_tags here, as there could be routes of crafting which spawn some tags and not others which affects blocking
            pos_spawn_weights_tags, relevant_start_tag = _get_positive_spawn_weight_tags(affix, starting_tags)
            relevant_start_tags.add(relevant_start_tag)

            pos_spawn_weights_from_current_pool = pos_spawn_weights_tags.intersection(current_tag_pool)

            if len(pos_spawn_weights_from_current_pool) > 0:
                if key not in affixes:
                    affixes[key] = affix
                    added_new_affixes = True

                added_tags = added_tags.union(set(affix["adds_tags"]))
   
    #added tags don't need to include the relevant_start_tags
    added_tags = added_tags.difference(relevant_start_tags)

    print(f"relevant_start_tags {relevant_start_tags}") 
    print(f"added_tags {added_tags}")
    print(affixes.keys())
    return relevant_start_tags, added_tags, affixes

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
    relevant_starting_tags, added_tags, affixes = generate_all_possible_affixes_and_tags(starting_tags, mod_pool)

    return {**affixes, **appended_mod_dictionary}, relevant_starting_tags, added_tags
