import decimal
import sqlite3


# Converter function for decimal.Decimal
def decimal_converter(value):
    return decimal.Decimal(value)


# Adapter function for decimal.Decimal
def decimal_adapter(decimal_obj):
    return str(decimal_obj)


# Register the converter and adapter functions
def register_database_types():
    sqlite3.register_converter("DECIMAL", decimal_converter)
    sqlite3.register_adapter(decimal.Decimal, decimal_adapter)
