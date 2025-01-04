def variable_to_boolean(value: str | float | None | bool) -> bool:
    """
    Converts provided environment variable value to boolean if possible or raises value error.

    """
    match value:
        case str():
            if value.lower() in ("true", "yes"):
                return True
            if value.lower() in ("false", "no", "nil", "none", "null", "nan"):
                return False
            if value.isdigit():
                return bool(int(value))
        case float() | int():
            return bool(value)
        case None:
            return False
        case bool():
            return value
    raise ValueError("Provided data does not contain valid boolean value")
