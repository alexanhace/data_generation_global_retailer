import sys
import uuid
import random
import logging
import argparse
import tomllib
import numpy as np
import pandas as pd
import difflib
from pathlib import Path
from datetime import datetime
from faker import Faker
from faker.config import AVAILABLE_LOCALES

from data_generation.shared.currency import convert_usd, get_currency
from data_generation.shared.logger import setup_logger
from data_generation.shared.paths import PROJECT_ROOT

# ---- Constants ----
CATALOG_PATH    = Path(__file__).parent / 'catalog' / 'retail_products.toml'
OUTPUT_DIR      = PROJECT_ROOT / 'output' / 'retail' / 'data'
NAMESPACE       = uuid.UUID('231875a5-9246-45c1-a616-17fe00eaa045')

logger = logging.getLogger(__name__)

def locale_fnct(x):
  #Standardize input to use underscores, then split
  normalized = x.replace('-','_')
  parts = normalized.split('_')

  #Ensure we always return a list of at least two items to avoid index errors
  if len(parts) < 2:
    return [parts[0], "UNKNOWN"]
  return parts

# ---- Catalog loader ----
def load_catalog(path=CATALOG_PATH):
    """Load and return the product catalog from TOML file."""
    logger.info(f"Loading product catalog from {path}")
    if not path.exists():
        raise FileNotFoundError(f"Product catalog not found: {path}")
    with open(path, 'rb') as f:
        catalog = tomllib.load(f)
    logger.info(f"Catalog loaded: {len(catalog['categories'])} categories")
    return catalog

# ---- Product generator ----
def generate_products(catalog, country_code, seed):
    """Generate one product record per brand/product/color combination.
    
    Args:
        catalog:        Parsed TOML catalog dict
        country_code:   ISO 3166-1 alpha-2 country code for currency conversion
        seed:           Random seed for reproducibility
        
    Returns:
        List of product record dicts
    """
    random.seed(seed)
    np.random.seed(seed)
    Faker.seed(seed)

    currency_code, symbol, rate = get_currency(country_code)
    logger.info(f"Generating products for country: {country_code} | currency: {currency_code}")

    products = [] #List for products to be loaded
    idx = 0 # Global index for deterministic UUID generation

    for catkey, category in catalog['categories'].items():
        cat_id      = category['category_id']
        cat_name    = category['display_name']
        margin      = category['margin_pct']

        for subkey, sub in category['subcategories'].items():
            sub_id      = sub['subcategory_id']
            sub_name    = sub['display_name']
            cost_min, cost_max = sub['cost_range']

            for brand in sub['brands']:
                for product in sub['products']:
                    for color in sub['colors']:

                        # Reproducible cost within range
                        unit_cost_usd = round(random.uniform(cost_min, cost_max), 2)

                        # Price derived from margin: cost (1 - margin)
                        unit_price_usd = round(unit_cost_usd / (1 - margin), 2)

                        #Local currency conversion
                        unit_cost_local, _, _ = convert_usd(unit_cost_usd, country_code)
                        unit_price_local, _, _ = convert_usd(unit_price_usd, country_code)

                        products.append({
                            'product_id':       str(uuid.uuid5(NAMESPACE, str(idx))),
                            'product_name':     f"{brand} {product}",
                            'brand':            brand,
                            'color':            color,
                            'category_id':      cat_id,
                            'category':         cat_name,
                            'subcategory_id':   sub_id,
                            'subcategory':      sub_name,
                            'unit_cost_usd':    unit_cost_usd,
                            'unit_price_usd':   unit_price_usd,
                            'unit_cost_local':  unit_cost_local,
                            'unit_price_local': unit_price_local,
                            'currency_code':    currency_code,
                            'currency_symbol':  symbol,
                        })
                        idx += 1

    logger.info(f"Generated {len(products):,} product records")
    return products

# ---- Output ----

def save_products(products, country_code):
    """Save generated prodcutes to a timestamped CSV."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    now_str     =datetime.now().strftime('%Y_%m_%d_%H:%M:%S')
    file_name   =f"retail_products_{country_code}_{now_str}.csv"
    file_path   = OUTPUT_DIR / file_name

    df = pd.DataFrame(products)
    df.to_csv(file_path, index=False)

    logger.info(f"Saved {len(df):,} records to {file_path.resolve()}")
    return file_path

# ---- Entry point ----
def main():
    setup_logger()

    parser = argparse.ArgumentParser(description="Generate fake retail procuct data")
    parser.add_argument(
        '--locale',
        type=str,
        default='en-US',
        help="Locale for currency conversion e.g. en-US, en-GB [default: en-US]"
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=100,
        help="Random seed for reproducibility [default: 100]"
    )
    args = parser.parse_args()

    locale = args.locale
    seed = args.seed

    locale_array = locale_fnct(locale)
    clean_locale = locale_array[0] + '_' + locale_array[1]
    country_code = locale_array[1]
    supported_locales = AVAILABLE_LOCALES

    #Validation locale argument
    logger.info(f"Validating locale argument: {locale}")
    if clean_locale not in supported_locales:
        suggestions = difflib.get_close_matches(clean_locale, supported_locales, n=1)
        msg = f"Invalid locale: '{locale}'"
        if suggestions:
            msg += f" - did you mean '{suggestions[0]}'?"
            logger.error(msg)
            sys.exit(1)
    
    logger.info(f"Locale validated: {clean_locale}")

    #Validate seed argument
    if not isinstance(seed, int):
        logger.error(f"Seed must be a number.  you provided a {type(seed)}")
        sys.exit(1)

    logger.info(f"Seed validated: {seed}")

    # ---- Retail Product Generation ----
    logger.info(f"Starting retail product generation | locale={locale} | seed={seed}")

    try:
        catalog = load_catalog()
        products = generate_products(catalog, country_code, seed)
        save_products(products, country_code)
    except Exception:
        logger.exception("Product generation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()