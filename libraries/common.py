import os


def is_root():
    return os.geteuid() == 0


def convert_floats_to_ints(data):
    if isinstance(data, dict):
        return {k: convert_floats_to_ints(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_floats_to_ints(item) for item in data]
    elif isinstance(data, float) and data.is_integer():
        return int(data)
    else:
        return data


def load_allowed_ips(file_path: str):
    if not file_path or not os.path.isfile(file_path):
        raise (f"File {file_path} does not exist")

    allowed_ips = []
    try:
        with open(file_path, "r") as file:
            allowed_ips = [line.strip() for line in file if line.strip()]
    except Exception as e:
        raise (f"Error reading allowed IPs from file: {e}")

    return allowed_ips
