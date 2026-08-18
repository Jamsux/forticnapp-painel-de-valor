"""Persistência local simples dos dados coletados (tudo fica no disco do usuário)."""
import json
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def save_df(name, df):
    df.to_parquet(os.path.join(DATA_DIR, f"{name}.parquet"), index=False)


def load_df(name):
    path = os.path.join(DATA_DIR, f"{name}.parquet")
    if not os.path.exists(path):
        return None
    return pd.read_parquet(path)


def save_json(name, obj):
    with open(os.path.join(DATA_DIR, f"{name}.json"), "w") as fh:
        json.dump(obj, fh, indent=2, default=str)


def load_json(name):
    path = os.path.join(DATA_DIR, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)
