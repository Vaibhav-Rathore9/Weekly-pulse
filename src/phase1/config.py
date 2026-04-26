"""
Groww App ID mappings for both storefronts.
"""

import os
from ..config import get_product_config

PRODUCT_NAME = "Groww"

_cfg = get_product_config("groww")
GROWW_APP_STORE_ID = _cfg["app_store_id"]
GROWW_PLAY_STORE_ID = _cfg["google_play_id"]
DEFAULT_REVIEW_WINDOW_WEEKS = _cfg["default_review_window_weeks"]
