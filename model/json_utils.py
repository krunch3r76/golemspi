import decimal
import json


def decimal_decoder(obj):
    if isinstance(obj, float):
        return decimal.Decimal(str(obj))
    return obj


def json_loads(s):
    return json.loads(s, parse_float=decimal.Decimal, object_hook=decimal_decoder)


def json_loadf(file):
    with open(file, "r") as f:
        return json.load(f, parse_float=decimal.Decimal, object_hook=decimal_decoder)
