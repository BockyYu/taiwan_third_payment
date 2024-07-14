import toml
from collections.abc import MutableMapping


def update_dict(base, updates):
    for key, value in updates.items():
        if isinstance(value, MutableMapping) and key in base:
            base[key] = update_dict(base.get(key, {}), value)
        else:
            base[key] = value
    return base


def load_config():
    base_path = "./config/config.base.toml"
    dev_path = "./config/config.dev.toml"
    base_config = toml.load(base_path)
    dev_config = toml.load(dev_path)

    final_config = update_dict(base_config, dev_config)
    return final_config


conf = load_config()
