#functions


import pandas as pd

def clean(path, skiprows=16):
    df = pd.read_csv(
        path,
        delimiter=",",
        encoding="utf-8-sig",
        skiprows=skiprows,
        skip_blank_lines=True,
        on_bad_lines="skip",
        engine="python"
    )
    if df.columns[0].startswith('Unnamed') or df.columns[0] == '':
        df.drop(df.columns[0], axis=1, inplace=True)

    df.dropna(axis=1, how="all", inplace=True)
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("(", "")
        .str.replace(")", "")
    )
    return df
