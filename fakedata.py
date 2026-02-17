#Process to generate a single locale of fake PII data
# #******Define Dependencies******
import random
import argparse
import sys
from faker import Faker
import pandas as pd
from datetime import datetime
from pathlib import Path

def locale_fnct(x):
  #split the input argument into two elements either using and underscore (_) or a dash (-) as the separator
  return x.split("_",2) if x.find("_") != -1 else (x.split("-",2) if x.find("-") != -1 else -1)

#******Define Argument Parser******
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="method to generate fake PII data")
  parser.add_argument("--locale", type=str, default = 'en-US', help="The first argument specifying a language and country to use for generating data. [default: en-US]")
  parser.add_argument("--record_number", type=int, default = 100, help="The second argument specifying the nubmer of rows desired in output [default: 10]")

#******Parse arguments
args = parser.parse_args()

#Save inputs
locale = args.locale  #'en-US' en-GB
rec_num = args.record_number

#split the input argument into two elements either using and underscore (_) or a dash (-) as the separator
#locale_fnct = lambda x: x.split("_",2) if x.find("_") != -1 else (x.split("-",2) if x.find("-") != -1 else -1)

locale_array = locale_fnct(locale)

#Validate locale argument
if locale_array[0] == 'en' and locale_array[1] in ('US','CA','UK','GB'):
  fake = Faker(locale)
else:
  raise ValueError(f"Currently, the process only accepts en for the language and UK, GB, US or CA for the country code.  You provided {locale}")
  sys.exit(1)

#Validate number of rows argument
if isinstance(rec_num, int):
  num_rows = rec_num
else:
  raise TypeError(f"Number of records must be a number.  you provided a {type(rec_num)}")
  sys.exit(1)

fake_data = []

#******Generate Data based on argument input********
for i in range(num_rows):
  Faker.seed(i)

  #Define fake data
  street_address = fake.street_address()
  city = fake.city()

  if locale_array[1] in ('GB', 'UK'):
    state = 'N/A'
    county = fake.county()
    province = 'N/A'
    country = 'United Kingdom'
    postal_code = fake.postcode()
    cell_phone = fake.cellphone_number()

  if locale_array[1] == 'US': 
    state = fake.state()
    county = 'N/A'
    province = 'N/A'
    country = 'United States'
    postal_code = fake.postalcode()
    cell_phone = fake.basic_phone_number()

  if locale_array[1] == 'CA':
    state = 'N/A'
    county = 'N/A'
    province = fake.province()
    country = 'Canada'
    postal_code = fake.postalcode()
    cell_phone = 'N/A'
  
  email = fake.free_email()
  phone_number = fake.phone_number()
  gender = random.choice(['M', 'F'])
  #print(f"gender: {gender}")
  person = fake.profile(['name'], sex = gender)
  dob = fake.date_between(start_date="-80y", end_date="-20y") #between 20 and 80 years old as of today


  new_row_data = {
      'name': person['name'],
      'street_address': street_address,
      'city': city,
      'county': county,
      'province': province,
      'state': state,
      'postal_code': postal_code,
      'country': country,
      'email': email,
      'phone': phone_number,
      'cell_phone': cell_phone,
      'gender': gender,
      'dob': dob
    }
  fake_data.append(new_row_data)

dir_path = './output/data/'
now = datetime.now()
now_str = now.strftime('%Y_%m_%d %H:%M:%S')
file_name = f"fake_data_{locale_array[1]}_{now_str}.csv"
file_path = dir_path + file_name
rel_file_path = Path(file_path)
full_path = rel_file_path.resolve()
#print(f"Full path of file is {full_path}") - #Use for full path when needed

df = pd.DataFrame(fake_data)
df.to_csv(file_path,index=False)

print(f"Saved {file_name} to {dir_path}")
