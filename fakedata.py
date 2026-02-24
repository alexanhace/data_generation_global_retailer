#Process to generate a single locale of fake PII data
# #******Define Dependencies******
import random
import argparse
import sys
from faker import Faker
from faker.config import AVAILABLE_LOCALES
import pandas as pd
from datetime import datetime
from pathlib import Path
import difflib
import pycountry_convert as pc
from geonames_addr import GeoLocator

#Functions
def locale_fnct(x):
  #Standardize input to use underscores, then split
  normalized = x.replace('-','_')
  parts = normalized.split('_')

  #Ensure we always return a list of at least two items to avoid index errors
  if len(parts) < 2:
    return [parts[0], "UNKNOWN"]
  return parts

def get_continent(country_code):
  try:
    # Convert country code (e.g., 'US') to continent code (e.g., 'NA')
    continent_code = pc.country_alpha2_to_continent_code(country_code)

    #Convert continent code to full name
    continent_names = {
      'AF': 'Africa',
      'AS': 'Asia',
      'EU': 'Europe',
      'NA': 'North America',
      'OC': 'Oceania',
      'SA': 'South America',
      'AN': 'Antarctica'
    }
    return continent_names[continent_code]
  except KeyError:
    suggestions = difflib.get_close_matches(country_code, continent_names.keys(), n=1)
    if not suggestions:
      return "Unknown Country Code"
    else:
      return f"Unknown Country Code.  Did you mean {suggestions[0]}"


#******Define Argument Parser******
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="method to generate fake PII data")
  parser.add_argument("--locale", type=str, default = 'en-US', help="The first argument specifying a language and country to use for generating data. [default: en-US]")
  parser.add_argument("--record_number", type=int, default = 100, help="The second argument specifying the number of rows desired in output [default: 100]")

#******Parse arguments
args = parser.parse_args()

#Save inputs
locale = args.locale  #'en-US' 'en-CA' 'en-GB' 'it_IT' 'nl_NL' 'fr_FR 'de_DE' 'en_AU'
rec_num = args.record_number
supported_locales = AVAILABLE_LOCALES


#split the input argument into two elements either using and underscore (_) or a dash (-) as the separator
#locale_fnct = lambda x: x.split("_",2) if x.find("_") != -1 else (x.split("-",2) if x.find("-") != -1 else -1)

locale_array = locale_fnct(locale)
clean_locale = locale_array[0] + '_' + locale_array[1]
country_cd = locale_array[1]

#Validate locale argument no matter what the separator is
if (clean_locale) in supported_locales:
  fake = Faker(clean_locale)
else:
  suggestions = difflib.get_close_matches(clean_locale, supported_locales, n=1)
  if not suggestions:
    raise ValueError(f"Currently, the process only accepts the following for the locales: {supported_locales}.  You provided {locale}")
    sys.exit(1)
  print(f"Did you mean '{suggestions[0]}")
  sys.exit(1)


#Validate number of rows argument
if isinstance(rec_num, int):
  num_rows = rec_num
else:
  raise TypeError(f"Number of records must be a number.  you provided a {type(rec_num)}")
  sys.exit(1)

fake_data = []

locator = GeoLocator([country_cd])
continent = get_continent(country_cd) 

Faker.seed(100)

#******Generate Data based on argument input********
for i in range(num_rows):
  
  loc = locator.get_random_location(country_cd)
  loc_df = pd.Series(loc)

  #While there is NAN data in the result, get another result for 5 tries
  cnt = 0
  while loc_df.isna().sum().sum() > 0 and cnt < 5:
    loc = locator.get_random_location(country_cd)
    loc_df = pd.Series(loc)
    cnt+=1

  if cnt > 4:
    print(f"Retries for clean data maxed out at {cnt} tries.")

  #Define fake data
  street_address = fake.street_address()
  city = loc['city']
  state = loc['state_province']
  state_code = loc['state_abbr']
  postal_code = loc['postal_code']
  country = loc['country']
  email = fake.free_email()
  phone_number = fake.phone_number()
  gender = random.choice(['M', 'F'])
  #print(f"gender: {gender}")
  person = fake.profile(['name'], sex = gender)
  dob = fake.date_between(start_date="-80y", end_date="-20y") #between 20 and 80 years old as of today


  new_row_data = {
      'name': person['name'],
      'street_address': street_address.replace('\n',' '),
      'city': city,
      #'county': county,
      #'province': province,
      'state': state,
      'state_code': state_code,
      'postal_code': postal_code,
      #'address': fake.address(),
      'country': country,
      'continent': continent,
      'email': email,
      'phone': phone_number,
      #'cell_phone': cell_phone,
      'gender': gender,
      'dob': dob
    }
  fake_data.append(new_row_data)

dir_path = './output/data/'
now = datetime.now()
now_str = now.strftime('%Y_%m_%d %H:%M:%S')
file_name = f"fake_data_{country_cd}_{now_str}.csv"
file_path = dir_path + file_name
rel_file_path = Path(file_path)
full_path = rel_file_path.resolve()
#print(f"Full path of file is {full_path}") - #Use for full path when needed

df = pd.DataFrame(fake_data)
df.to_csv(file_path,index=False)

print(f"Saved {file_name} to {dir_path}")
