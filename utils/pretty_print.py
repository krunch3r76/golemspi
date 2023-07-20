# utils/pretty_print.py

from dataclasses import dataclass, asdict
import pprint


def pprint_dataclass(obj):
    if hasattr(obj, "__dataclass_fields__"):
        data = asdict(obj)
        print("{\n")
        for field, value in data.items():
            if isinstance(value, str) and len(value) > 40:
                value = value.replace(
                    "\n", " "
                )  # Replace newline characters to preserve formatting
            print(f"\t{field}: {value}")
            # print()  # Print a newline to separate fields
        print("}\n")
    else:
        print(obj)


def pprint_class(obj):
    class_name = type(obj).__name__
    attributes = {
        attr: getattr(obj, attr) for attr in obj.__dict__ if not attr.startswith("__")
    }
    print(f"{class_name}:")
    pprint.pprint(attributes, indent=4)


# def pprint_class(obj):
#     class_name = type(obj).__name__
#     if hasattr(obj, "__repr__") and callable(obj.__repr__):
#         attributes = obj.__repr__()
#         if isinstance(attributes, dict):
#             attributes_str = ", ".join(
#                 f"{attr}={value!r}"
#                 for attr, value in attributes.items()
#                 if not attr.startswith("__")
#             )
#             return f"{class_name}({attributes_str})"
#     return f"{class_name}(<non-printable>)"
