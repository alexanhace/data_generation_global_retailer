import json
import logging
import time
import urllib.request
from data_generation.shared.paths import PROJECT_ROOT

from babel.numbers import get_territory_currencies, get_currency_symbol

logger = logging.getLogger(__name__)

#----Contants ----
CACHE_PATH      = PROJECT_ROOT / 'data' / 'exchange_rates.json'
CACHE_MAX_AGE   = 30 * 86400  #30 days in seconds
API_URL         = 'https://api.frankfurter.app/latest?base=USD'

# ---- Exchange rate fetching and caching ----

def _is_cache_stale():
    """Return True if the cache is missing or older than CACHE_MAX_AGE."""
    if not CACHE_PATH.exists():
        return True
    age = time.time() - CACHE_PATH.stat().st_mtime
    return age > CACHE_MAX_AGE

def _fetch_rates():
    """Fetch latest USD exchange rates from frankfurter.app."""
    logger.info(f"Fetching exchange rates from {API_URL}")
    try:
        request = urllib.request.Request(
            API_URL,
            headers={'User-Agent': 'data-generation/1.0'}
        )
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())
        rates = data['rates']
        rates['USD'] = 1.00   #Base currency not included in response

        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_PATH, 'w') as f:
            json.dump({'fetched_at': time.time(), 'rates': rates}, f, indent=2)

        logger.info(f"Exchange rates cached to {CACHE_PATH} ({len(rates)} currencies)")
        return rates
    except Exception:
        logger.exception("Failded to fetch exchange rates from API")
        raise

def _load_rates():
    """Load exchange rates from cache, fetching if stale"""
    if _is_cache_stale():
        return _fetch_rates()
    
    logger.debug(f"Loading exchange rates from cache: {CACHE_PATH}")
    with open(CACHE_PATH) as f:
        data = json.load(f)
    return data['rates']

# ----Public API ---
def get_currency(country_code):
    """Return (currency_code, symbol, usd_exchange_rate) for a country code.
    
    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g. 'US', 'GB')
        
    Returns:
        Tuple of (currency, symbol, usd_exchange_rate)
        
    Raises:
        ValueError: If country code is not recognized by Babel
        KeyError: If the currency code is not in the exchange rate data
    """
    try:
        currency_code   = get_territory_currencies(country_code)[0]
        symbol          = get_currency_symbol(currency_code, locale='en')
    except Exception:
        raise ValueError(
            f"Could not resolve currency for country: {country_code!r}"
            f"Ensure it is a valid ISO 3166-1 alpha-2 country code."
        )
    
    rates = _load_rates()

    if currency_code not in rates:
        raise KeyError(
            f"No exchange rate found for currency: {currency_code!r}"
            f"(country: {country_code!r})"    
        )
    rate = rates[currency_code]
    logger.debug(f"Currency resolved: {country_code} → {currency_code} ({symbol}) @ {rate}")
    return currency_code, symbol, rate

def convert_usd(amount_usd, country_code):
    """Convert a USD amount to the local currency for a given country.
    
    Args:
        amount_usd:     Amount in USD
        country_code:   ISO 3166-1 alpha-2 country code
        
    Returns:
        Tuple of (converted_amount, currency_code, symbol)
    """
    currency_code, symbol, rate = get_currency(country_code)
    converted = round(amount_usd * rate, 2)
    return converted, currency_code, symbol