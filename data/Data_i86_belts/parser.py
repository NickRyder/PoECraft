
def import_i86_belts():
    directory = "Data_i86_belts"
    for filename in os.listdir(directory):
        if filename.endswith(".txt") or filename.endswith(".py"):
            text = open(directory + "/" + filename).read()

        else:
            continue

    clipboard_entries = text.split("\n&&&&&&&&&&&&&&&&&&&&\n")
    print(len(clipboard_entries))
    clipboard_entries_nonempty = set()
    for text in clipboard_entries:
        if text != "" and text != "\ufeff":
            if text in clipboard_entries_nonempty:
                print(text)
            clipboard_entries_nonempty.add(text)

    print(len(clipboard_entries_nonempty))

    mod_list = []
    for entry in clipboard_entries_nonempty:
        mod_possibilities = parse_clipboard(entry)
        assert len(mod_possibilities) == 1, "hybrid?"
        mod_list.append(parse_clipboard(entry)[0])

    print(mod_list)
    mod_counter = Counter()
    for mods in mod_list:
        for mod in mods:
            if mod not in mod_counter:
                mod_counter[mod] = 0
            mod_counter[mod] += 1
    print(mod_counter)

    print(len(clipboard_entries_nonempty))
    wand = get_base_item("Stygian Vise")
    wand_item = base_item(wand, ilvl=86, fossil_names=["Sanctified Fossil"])
    sorted_keys = sorted(wand_item.hash_weight_dict.base_dict.keys())
    for key in sorted_keys:
        if key not in mod_counter:
            print(0)
        else:
            print(mod_counter[key])