import pandas as pd
from app.config import settings

def load_body_function_options():
    df = pd.read_csv("data/body_function.json")
    options = {}
    for _, row in df.iterrows():
        body = row["body"]
        func_list = [f.strip() for f in row["function"].split(",") if f.strip()]
        options.setdefault(body, []).extend(func_list)
    return options


def fetch_functions_by_body(body_part):
    df = pd.read_csv("data/body_function.json")
    matched_rows = df[df["body"] == body_part]
    if matched_rows.empty:
        return []
    func_str = matched_rows.iloc[0]["function"]
    return [f.strip() for f in func_str.split(",") if f.strip()] 
