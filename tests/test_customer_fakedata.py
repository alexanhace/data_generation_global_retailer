# tests/test_customer_fakedata.py - Tests for customer fake data generation

import pytest
import random
import uuid
import numpy as np
from unittest.mock import patch, MagicMock
from faker import Faker

from data_generation.customers.customer_fakedata import (
    locale_fnct,
    get_continent
)

#==========================================================
# locale_fnct
#==========================================================

class TestLoaleFnct:
    """Tests for the local parsing utility."""

    def test_underscore_separator(self):
        """Verify local_fnct accepts underscore as a valid separator"""
        assert locale_fnct('en_US') == ['en', 'US']

    def test_dash_separator(self):
        """Verify local_fnct accepts dash as a valid separator"""
        assert locale_fnct('en-US') == ['en', 'US']

    def test_non_dash_or_underscore_separator(self):
        """Verify local_fnct does not accept something other than a dash an an underscore as a valid separator"""
        assert locale_fnct('en+US') == ['en+US', "UNKNOWN"]

    def test_single_part_returns_unknown(self):
        """Verify that second array item is populated by default value when parsing is not complete"""
        result = locale_fnct('en')
        assert result == ['en', "UNKNOWN"]

    @pytest.mark.parametrize("locale_str, expected", [
        ('fr_FR', ['fr', 'FR']),
        ('de-DE', ['de', 'DE']),
        ('ja_JP', ['ja', 'JP']),
        ('pt_BR', ['pt', 'BR']),
        ('nl_NL', ['nl', 'NL']),
        ('it_IT', ['it', 'IT']),  
    ])
    def test_various_locales(self, locale_str, expected):
        """Verify the locale_fnct produces consisten results"""
        assert locale_fnct(locale_str) == expected

    def test_output_is_list_of_two(self):
        """Verify the locale is a list of two items"""
        result = locale_fnct('en_GB')
        assert isinstance(result, list)
        assert len(result) == 2

    def test_country_code_extraction(self):
        """Verify the country code (index 1) is what main() uses."""
        result = locale_fnct('en_GB')
        country_cd = result[1]
        assert country_cd == 'GB'

#==========================================================
# get_continent
#==========================================================

class TestGetContinent:
    """Tests for country-to-continent mapping."""

    @pytest.mark.parametrize("country_code, expected_continent", [
        ('US', 'North America'),
        ('CA', 'North America'),
        ('GB', 'Europe'),
        ('DE', 'Europe'),
        ('FR', 'Europe'),
        ('JP', 'Asia'),
        ('AU', 'Oceania'),
        ('BR', 'South America'),
        ('NG', 'Africa'),
    ])
    def test_known_countries(self, country_code, expected_continent):
        """Verify expected continent values"""
        assert get_continent(country_code) == expected_continent

    def test_invalid_country_returns_unknown(self):
        """Verify invalid country code returns 'Unknown' in result"""
        result = get_continent('XX')
        assert "Unkown" in result
    
    def test_return_type_is_string(self):
        """Verify get_continent function returns a string"""
        assert isinstance(get_continent('US'),str)

#==========================================================
# Record structure
#==========================================================
