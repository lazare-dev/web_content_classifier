# src\policies.py

import json

def load_policies(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            policies = json.load(file)
        return policies
    except Exception as e:
        return None
