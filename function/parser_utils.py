# parser_utils.py

def parse_z_values(arg):
    """
    Parses the z_ini and z_fin arguments, converting them to None or integers.

    Parameters:
    arg (str): The argument passed from the command line, expected to be 'None' or an integer.

    Returns:
    None or int: None if the argument is 'None', otherwise the integer value.
    """
    if arg.lower() == 'none':
        return None
    try:
        return int(arg)
    except Exception as e:
        print(f'Invalid values for z_ini and z_fin: {e}', flush=True)
        sys.exit(1)

def str2bool(v):
    """
    Converts a string or integer representation of a boolean value to a boolean type.

    Parameters:
    v (str or int): The value to convert.

    Returns:
    bool: The converted boolean value.
    """
    return v in ("True", "true", 1)

def list_of_bools(arg):
    """
    Converts a comma-separated string of boolean values to a list of booleans.

    Parameters:
    arg (str): The comma-separated string of boolean values.

    Returns:
    list of bool: The list of boolean values.
    """
    return list(map(str2bool, arg.split(',')))

def list_of_ints(arg):
    """
    Converts a comma-separated string of integers to a list of integers.

    Parameters:
    arg (str): The comma-separated string of integers.

    Returns:
    list of int: The list of integer values.
    """
    return list(map(int, arg.split(',')))

def list_of_strings(arg):
    """
    Converts a comma-separated string to a list of strings.

    Parameters:
    arg (str): The comma-separated string.

    Returns:
    list of str: The list of strings.
    """
    return [feature.strip() for feature in arg.split(',')]

def int_or_none(value):
    """
    Attempts to convert the given value to an integer. 

    If the conversion fails due to a ValueError or AttributeError, it returns None 
    and prints a warning message.

    Parameters:
    value (any): The input value to be converted to an integer.

    Returns:
    int or None: The converted integer if successful, otherwise None.
    """
    try:
        return int(value)
    except (ValueError, AttributeError):
        return None
