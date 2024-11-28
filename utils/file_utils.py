import csv
import os

import pandas as pd


def read_file(filename: str) -> dict:
    df = pd.read_csv(filename, low_memory=False)
    return df.set_index(df.columns[0]).to_dict(orient="index")


def write_file(
    folder_path: str, filename: str, data: list, headers: list[str] or None = None
):
    cwd = os.getcwd()
    dir_path = "{0:s}/{1:s}".format(cwd, folder_path)
    try:
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
    except Exception as err:
        print(f"Unknown file exception:\n{err}")
    with open(f"{dir_path}/{filename}", "w", newline="") as csvfile:
        wr = csv.writer(csvfile)
        if headers is not None:
            wr.writerow(headers)
        wr.writerows(data)
