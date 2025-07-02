SUPPORTED_SQL_TRANSFORMATIONS = {

    "TRIM": 0,      # Remove leading and trailing spaces
    "UPPER": 0,     # Convert a string to uppercase
    "UCASE": 0,     # Convert a string to uppercase (alias for UPPER)
    "LOWER": 0,     # Convert a string to lowercase
    "LENGTH": 0,    # Return the length of a string
    "INITCAP": 0,   # Convert the first character of a string to uppercase
    "IS_DATE": 0,   # Check if a value is a date and return
    "IS_NULL": 0,   # Check if a value is NULL and return 1 if true, 0 otherwise
    "IS_EMPTY": 0,  # Check if a value is empty and return

    "ROUND": 1,     # Round a number to a specified number of decimal places
    "FLOOR": 1,     # Round a number down to the nearest integer
    "CEIL": 1,      # Round a number up to the nearest integer
    "ABS": 1,       # Return the absolute value of a number
    "SQRT": 1,      # Return the square root of a number

    "SUBSTR": 2,  # Extract a substring from a string (start, length)
    "LPAD": 2,   # Left pad a string with spaces or specified characters (length, pad_char)
    "RPAD": 2,   # Right pad a string with spaces or specified characters (length, pad_char)
    "INSTR": 2,  # Insert a substring into a string at a specified position (substring, position)
    "REPLACE": 2,  # Replace occurrences of a substring in a string with another substring (old, new)

}