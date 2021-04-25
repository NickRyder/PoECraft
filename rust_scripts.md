# Writing scripts in Rust for speed,
The following script runs 4x faster when we write it in rust.

The key paradigm here is to build an ExplicitModRoller in python land, and then pass it in as a mutable reference to rust. Because our ExplicitModRoller extends the Rust class, the commands work very similarly.

One difference is to get the current keys in python one does `roller.affix_keys_current` while in rust one does `roller.affix_keys_current().unwrap()`


`scripts/alteration_price.py`
```python
def get_alt_aug_count(
    roller,
    mod_name,
    generation_type,
    trial_n,
):
    count = 0
    alt = 0
    aug = 0

    for _ in tqdm(range(trial_n)):
        roller.roll_item_magic()
        alt += 1
        if mod_name in roller.affix_keys_current:
            count += 1
        else:
            aug_prefix = generation_type == "prefix" and roller.prefix_n == 0
            aug_suffix = generation_type == "suffix" and roller.suffix_n == 0
            if aug_prefix or aug_suffix:
                roller.roll_one_affix()
                aug += 1
                if mod_name in roller.affix_keys_current:
                    count += 1
    return alt, aug, count
```

`src/lib.rs`
```rust
 #[pyfn(m, "get_alt_aug_count")]
    fn get_alt_aug_count(
        roller: &mut ExplicitModRoller,
        mod_name: String,
        generation_type: String,
        trial_n: u32,
    ) -> (u32, u32, u32) {
        let mut count: u32 = 0;
        let mut alt: u32 = 0;
        let mut aug: u32 = 0;

        for _ in 0..trial_n {
            roller.roll_item_magic();
            alt += 1;
            if roller.affix_keys_current().unwrap().contains(&mod_name) {
                count += 1
            } else {
                let aug_prefix = (generation_type == "prefix") && (roller.prefix_n == 0);
                let aug_suffix = (generation_type == "suffix") && (roller.suffix_n == 0);
                if aug_prefix || aug_suffix {
                    roller.roll_one_affix();
                    aug += 1;
                    if roller.affix_keys_current().unwrap().contains(&mod_name) {
                        count += 1
                    }
                }
            }
        }
        (alt, aug, count)
    }
```
