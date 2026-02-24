from faker import Faker
import argparse


#******Define Argument Parser******
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="method to generate fake PII data")
  parser.add_argument("--locale", type=str, default = 'en-US', help="The first argument specifying a language and country to use for generating data. [default: en-US]")
  parser.add_argument("--record_number", type=int, default = 100, help="The second argument specifying the number of rows desired in output [default: 100]")

#******Parse arguments
args = parser.parse_args()

locale = args.locale
num_rows = args.record_number


fake_data = Faker(locale)

for i in range(num_rows):
  print(f'administrative_unit in {locale} is {fake_data.administrative_unit()}')
  print(f'state in {locale} is {fake_data.state()}')

