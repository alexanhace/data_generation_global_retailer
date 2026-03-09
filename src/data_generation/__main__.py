
import argparse
import sys
import importlib

GENERATORS = {
    ('customers', 'customers'): 'data_generation.customers.customer_fakedata',
    ('retail', 'products'):     'data_generation.verticals.retail.retail_product_fakedata'
}

def main():
    parser = argparse.ArgumentParser(
        description="Data Generation - Global Retailer",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        '--vertical',
        type=str,
        required=True,
        choices=['customers', 'retail'],
        help="Vertical to generate data for :\n"
             "  customers   - cross-vertical customer data\n"
             "  retail      - retail product data"
    )
    parser.add_argument(
        '--generator',
        type=str,
        required=True,
        choices=['customers', 'products'],
        help="Generator to run: \n"
             "  customers   - generate customer records\n"
             "  products    - generate product records"
    )

    # Parse only the known args - remaining args are passed to the generator
    args, remaining = parser.parse_known_args()

    key = (args.vertical, args.generator)
    if key not in GENERATORS:
        print(f"Error: No generator found for --vertical={args.vertical} --generator={args.generator}")
        print(f"Valid combinations: {list(GENERATORS.keys())}")
        sys.exit(1)

    # Dynamically import and run the target generator
    module_path = GENERATORS[key]
    module = importlib.import_module(module_path)

    # Pass remaining args to the generator by updating sys.argv
    sys.argv = [module_path] + remaining

    # Temporarily add this for testing before module.main()
    #print(f"Running: {module_path}")
    #print(f"With args: {sys.argv}")
    module.main()

if __name__ == "__main__":
        main()