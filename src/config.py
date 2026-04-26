"""
Global configuration loader for the Pulse agent.
"""
import os
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")

def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_product_config(product_name: str) -> dict:
    config = load_config()
    product = config.get("products", {}).get(product_name.lower())
    if not product:
        raise ValueError(f"Product '{product_name}' not found in config.yaml")
    return product
