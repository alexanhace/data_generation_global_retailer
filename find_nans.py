from pathlib import Path
from datetime import datetime
import pandas as pd

#Define file to ingest
def get_file (file_name, dir_path="./output/data/"):
    file_path = Path(dir_path + file_name)
    df = pd.read_csv(
            file_path, sep=',', dtype=str, low_memory=False
    )
    return df

loc = "./output/data/"
file = "fake_data_GB_2026_02_22 22:08:18.csv"
gb_df = get_file(file, loc)

num_nas = gb_df.isna().sum()
total_num_nas = num_nas.sum()
na_column_list = gb_df.columns[gb_df.isna().any()].tolist()

#print(f"Before replacement:\n {gb_df.head(10)}")

#gb_df['street_address'] = gb_df['street_address'].replace('\n', ' ',regex=True)

print(f"These are the na counts:\n{num_nas}")
print(f"Total number of nas is: {total_num_nas}")
print(f"Columns with nas:\n{na_column_list}")


#upd_file_path = Path(loc + file.replace(".",f"_updated_{datetime.now().strftime('%Y_%m_%d %H:%M:%S')}."))

#gb_df.to_csv(upd_file_path,index=False)