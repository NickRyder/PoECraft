# repoe_files = {"base_items", "characters", "crafting_bench_options", "default_monster_stats", "essences", "gem_tags", "gem_tooltips", "gems", "item_classes", "mods", "stat_translations", "stats", "tags", "mod_types", "fossils"}
# repoe_data = {}

# import json, urllib.request, urllib.error
# for file in repoe_files:
#     url = 'https://raw.githubusercontent.com/brather1ng/RePoE/master/data/' + file + '.json'
#     try:
#         response = urllib.request.urlopen(url)
#     except urllib.error.HTTPError:
#         print(f"HTTPError: {url}")
#     data = json.loads(response.read())
#     repoe_data[file] = data

# print("json loaded...")

# # print("i86 mods")
# # for key, mod in repoe_data["mods"].items():
# #     if mod["required_level"] > 86 and mod["generation_type"] in ["prefix", "suffix"] and mod["domain"] == "item" and mod["name"]:
# #         pos_tags = set([])
# #         for weight in mod["spawn_weights"]:
# #             if weight["weight"] > 0:
# #                 pos_tags.add(weight["tag"])
# #         stats = set([])
# #         for stat in mod["stats"]:
# #             stats.add(stat["id"])
# #         print(pos_tags, stats)


