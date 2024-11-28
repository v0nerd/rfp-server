def get_file_type_from_file_key(file_key: str) -> str:
    return file_key.lower().split(".")[-1]
