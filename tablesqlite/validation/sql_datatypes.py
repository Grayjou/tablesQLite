from typing import Set
from sortedcontainers import SortedDict
def upper_before_bracket(s: str) -> str:
    """
    Convert the first character before an opening bracket to uppercase.
    """
    if not s:
        return s
    partition = s.partition('(')
    return partition[0].upper() + partition[1] + partition[2]

all_types = (
'BIGINT(size)',
'BINARY(size)',
'BIT(size)',
'BLOB',
'BOOL',
'BOOLEAN',
'CHAR(size)',
'DATE',
'DATETIME(fsp)',
'DEC(p)',
'DECIMAL(p)',
'DOUBLE PRECISION(p)',
'DOUBLE(p)',
'ENUM(...)',
'FLOAT(p)',
'INT(size)',
'INTEGER(size)',
'LONGBLOB',
'LONGTEXT',
'MEDIUMBLOB',
'MEDIUMINT(size)',
'MEDIUMTEXT',
'REAL(p)',
'SET(...)',
'SMALLINT(size)',
'TEXT',
'TIME(fsp)',
'TIMESTAMP(fsp)',
'TINYBLOB',
'TINYINT(size)',
'TINYTEXT',
'VARBINARY(size)',
'VARCHAR(size)',
'YEAR')


def bracket_tuple_from_str(data_str: str) -> tuple[str, tuple]:
    if '(' not in data_str:
        return data_str.strip(), ()
    type_, args_str = data_str.split('(', 1)
    args_str = args_str.rstrip(')')
    args = tuple(arg.strip() for arg in args_str.split(',') if arg.strip())
    return type_.strip(), args

PLACEHOLDER_INT_KEYS = {"size", "fsp", "p"}



def match_bracket_tuple(data_str: str, pairs: Set[tuple[str, tuple]] = None) -> bool:
    if not pairs:
        return False
    type_, args = bracket_tuple_from_str(data_str)
    type_ = type_.strip().upper()

    for datatype, expected_args in pairs:
        if type_ != datatype.strip().upper():
            continue

        # Wildcard: accept anything
        if expected_args == ("...",):
            return True

        # Allow fewer args than expected (e.g., FLOAT → FLOAT(p))
        if len(args) > len(expected_args):
            return False

        for arg, expected in zip(args, expected_args):
            if expected == "...":
                continue
            if expected in PLACEHOLDER_INT_KEYS and not arg.isdigit():
                return False

        return True  # Valid even with missing optional args
    return False





def is_list_of_pairs(lst):
    """
    Check if the given list contains pairs of elements.
    """
    return all(isinstance(item, tuple) and len(item) == 2 for item in lst)

test_cases = [
    ("Enum(val1, val2)", True),
    ("CHAR(10)", True),
    ("INT(1,2,3,4))", False),
    ("FLOAT(10,2)", False),
    ("FLOAT(10)", True),
    ("FLOAT", True),
    ("VARCHAR(255)", True),
    ("BLOB(size)", False),  # size should be a number
    ("MEDIUMTEXT", True),
    ("SET(val1, val2)", True),
    ("DATE", True),
    ("TIMESTAMP(fsp)", False),
    ("BIT(size)", False),  # size should be a number
]
def validate_data_type_test():
    validator = Validator()
    for data_str, expected in test_cases:
        result = validator.validate_type(data_str)
        assert result == expected, f"Expected {expected} for '{data_str}', got {result}"
    validator.add_type("NEWTYPE(size)")
    assert validator.validate_type("NEWTYPE(size)") == False, "Failed to validate newly added type"
    assert validator.validate_type("NEWTYPE(123)") == True, "Failed to validate newly added type"
    print("All tests passed!")
class Validator(SortedDict):
    def __init__(self):
        super().__init__(set(bracket_tuple_from_str(string) for string in (all_types)))
    def validate_type(self, data_str: str) -> bool:
        """
        Validate if the given data type string matches any of the predefined types.
        
        Args:
            data_str (str): The data type string to validate.
        
        Returns:
            bool: True if the data type is valid, False otherwise.
        """
        return match_bracket_tuple(data_str, self.items())
    def add_type(self, data_str: str) -> None:
        """
        Add a new data type to the validator.
        
        Args:
            data_str (str): The data type string to add.
        """
        if not isinstance(data_str, str):
            raise TypeError("data_str must be a string")
        type_, args = bracket_tuple_from_str(data_str)
        self[type_.upper()] = args
    def remove_type(self, data_str: str) -> None:
        """
        Remove a data type from the validator.
        
        Args:
            data_str (str): The data type string to remove.
        """
        if not isinstance(data_str, str):
            raise TypeError("data_str must be a string")
        type_, _ = bracket_tuple_from_str(data_str)
        self.pop(type_.upper(), None)

_validator = None
def get_validator() -> Validator:
    """
    Get the singleton instance of the Validator.
    
    Returns:
        Validator: The singleton instance of the Validator.
    """
    global _validator
    if _validator is None:
        _validator = Validator()
    return _validator

def validate_data_type(data_str: str) -> bool:
    
    if not get_validator().validate_type(data_str):
        raise ValueError(f"Invalid data type: {data_str}")
    return True

def __getattr__(name: str, *args, **kwargs):
    """
    Get the validator instance or a specific method.
    
    Args:
        name (str): The name of the method or attribute to retrieve.
    
    Returns:
        Validator or method: The validator instance or the specified method.
    """
    if name == "validator":
        return get_validator()
    else:
        atr = get_validator().__getattribute__(name)
        if callable(atr):
            return atr(*args, **kwargs)
    return atr

def __contains__(data_str: str) -> bool:
    """
    Check if the data type is valid.
    
    Args:
        data_str (str): The data type string to check.
    
    Returns:
        bool: True if the data type is valid, False otherwise.
    """
    return get_validator().validate_type(data_str)

if __name__ == "__main__":
    validate_data_type_test()

    #All tests passed!



