import re
import logging

from typing import Optional, Union
from app.exceptions.custom_exceptions import InvalidRequestException
from app.service.supported_sql_functions import SUPPORTED_SQL_TRANSFORMATIONS


logger = logging.getLogger(__name__)

function_pattern = r"\b([A-Za-z_]\w*)\s*\((.*)\)" # Matches function names like TRIM, UPPER etc.
operator_pattern = r"\bNOT IN\b|\bIN\b|\bIS NOT NULL\b|\bIS NULL\b|<>|!=|=|<=|>=|<|>"  # Matches operators like =, <, >, != etc.
static_value_pattern = r'"([^"]*)"|(\d+)|NULL|null'  # Matches static values like 'abc', 123, 45.67 etc.
logical_operator_pattern = r"\b(AND|OR)\b"  # Matches logical operators like AND, OR

def convert_sql_expression_to_json(sql_expression: str) -> Optional[dict]:
    """
    Converts a SQL expression to a JSON representation.
    
    Args:
        sql_expression (str): The SQL expression to convert.
        
    Returns:
        Optional[dict]: A dictionary representing the JSON structure of the SQL expression, or None if conversion fails.
    """
    try:
        if not sql_expression:
            logger.error("Empty SQL expression provided.")
            return None
        
        # Remove all new line characters 
        sql_expression = sql_expression.replace("\n", " ").strip()

        # Replace multiple spaces with a single space
        sql_expression = re.sub(r'\s+', ' ', sql_expression)

        # Check if the expression starts or ends with a logical operator
        if expression_starts_with_logical_operator(sql_expression or expression_ends_with_logical_operator(sql_expression)):
            logger.error("SQL expression starts with a logical operator, which is not allowed.")
            raise InvalidRequestException(f"SQL expression '{sql_expression}' cannot start or end with a logical operator.")
        
        # Validate proper bracket closing
        if not validate_brackets_closer(sql_expression):
            logger.error(f"Please close all the brackets properly in the SQL expression '{sql_expression}'.")
            raise InvalidRequestException(f"Please close all the brackets properly in the SQL expression '{sql_expression}'.")
        
        # Initialize the JSON structure
        json_structure = {"conditions": []}

        # Fetch the logical operators
        logical_operator = fetch_logical_operator(sql_expression)
        if logical_operator:
            json_structure["logical_operator"] = logical_operator

        # Parse the SQL expression recursively
        parse_conditions(sql_expression, json_structure["conditions"])

        # If there is only one condition, remove the logical operator
        if len(json_structure["conditions"]) == 1:
            json_structure.pop("logical_operator", None) 
        
        return json_structure

    except InvalidRequestException as e:
        logger.error(f"{e.__class__.__name__}: {e.detail}")
        raise e
    

def expression_starts_with_logical_operator(sql_expression: str) -> bool:
    """
    Checks if the SQL expression starts with a logical operator.
    
    Args:
        sql_expression (str): The SQL expression to check.
        
    Returns:
        bool: True if the expression starts with a logical operator, False otherwise.
    """
    return bool(re.match(r"^\s*" + logical_operator_pattern, sql_expression, flags=re.IGNORECASE))


def expression_ends_with_logical_operator(sql_expression: str) -> bool:
    """
    Checks if the SQL expression ends with a logical operator.
    
    Args:
        sql_expression (str): The SQL expression to check.
        
    Returns:
        bool: True if the expression ends with a logical operator, False otherwise.
    """
    return bool(re.search(logical_operator_pattern + r"\s*$", sql_expression, flags=re.IGNORECASE))


def validate_brackets_closer(sql_expression: str) -> bool:
    """
    Validates that all brackets in the SQL expression are properly closed.
    
    Args:
        sql_expression (str): The SQL expression to validate.
        
    Returns:
        bool: True if all brackets are properly closed, False otherwise.
    """
    stack = []
    for char in sql_expression:
        if char == '(':
            stack.append(char)
        elif char == ')':
            if not stack or stack[-1] != '(':
                return False
            stack.pop()
    return len(stack) == 0


def fetch_logical_operator(sql_expression: str) -> str:
    """
    Fetches the logical operator from the SQL expression.
    
    Args:
        sql_expression (str): The SQL expression to check.
        
    Returns:
        str: The logical operator if found, otherwise None.
    """
    # Check if the sql_expression starts with a logical paranthesis
    if sql_expression.startswith('('):
        open_brackets = 0
        for i, char in enumerate(sql_expression):
            if char == '(':
                open_brackets += 1
            elif char == ')':
                open_brackets -= 1
                if open_brackets == 0:
                    # Closing bracket found, check for logical operator after the closing bracket
                    remaining_expression = sql_expression[i + 1:].strip()
                    logical_operator_match = re.search(logical_operator_pattern, remaining_expression, flags=re.IGNORECASE)
                    return logical_operator_match.group(0).upper() if logical_operator_match else None
        # If no closing bracket is found, raise an error
        logger.error(f"Unmatched opening parenthesis in the SQL expression: {sql_expression}")
        raise InvalidRequestException(f"Unmatched opening parenthesis in the SQL expression: {sql_expression}")

    match = re.search(logical_operator_pattern, sql_expression, flags=re.IGNORECASE)
    return match.group(0).upper() if match else None


def parse_conditions(expression: str, conditions: list) -> None:
    while expression:
        # Handle nested expressions
        if expression.startswith('('):
            # Find the matching closing parenthesis
            opening_bracket_index = 0
            for i, char in enumerate(expression):
                if char == '(':
                    opening_bracket_index += 1
                elif char == ')':
                    opening_bracket_index -= 1
                    if opening_bracket_index == 0:
                        # Extract the nested expression
                        nested_expression = expression[1:i]
                        nested_conditions = []
                        parse_conditions(nested_expression, nested_conditions)

                        # Fetch the logical operator for the nested expression
                        nested_logical_operator = fetch_logical_operator(nested_expression)

                        # Append the nested conditions to the main conditions list
                        nested_group = {
                            "logical_operator": nested_logical_operator or "AND",
                            "conditions": nested_conditions
                        }
                        conditions.append(nested_group)

                        # Continue parsing the rest of the expression
                        expression = expression[i + 1:].strip()
                        break
            else:
                logger.error(f"Unmatched opening parenthesis in the SQL expression: {expression}")
                raise InvalidRequestException("Unmatched opening parenthesis in the SQL expression: {expression}")
        else:
            # Split the expression by logical operators
            match = re.search(logical_operator_pattern, expression, flags=re.IGNORECASE)
            if match:
                condition = expression[:match.start()].strip()
                match.group(0).upper()
                expression = expression[match.end():].strip()
            else:
                condition = expression.strip()
                expression = ""

            # Parse the individual condition
            if condition:
                condition_json = parse_condition(condition)
                
                # Fetch the logical operator for the condition
                # logical_operator = fetch_logical_operator(condition)
                # condition_json["logical_operator"] = logical_operator or ""

                conditions.append(condition_json)


def parse_condition(condition: str) -> dict:
    """
    Parses a single condition from the SQL expression.
    
    Args:
        condition (str): The condition to parse.
        
    Returns:
        dict: A dictionary representing the parsed condition.
    """
    # Initialize the condition structure
    condition_json = {"transformations": []}
    
    # Match comparision operators
    operator_match = re.search(operator_pattern, condition, flags=re.IGNORECASE)
    if operator_match:
        condition_json["operator"] = operator_match.group(0).upper()
        
        # Split the condition into left and right parts
        operator_start_match = re.search(
            rf"(?<!\w){re.escape(operator_match.group(0))}(?!\w)",
            condition,
            flags=re.IGNORECASE
        )
        operator_start_index = operator_start_match.start()
        operator_substring = condition[operator_start_index + len(operator_match.group(0)):].strip()

        condition_json["valueType"] = "string"

        if condition_json["operator"] in {"IN", "NOT IN"}:
            # Handle array of values
            array_match = re.search(r"\(([^)]+)\)", operator_substring)
            if array_match:
                values = array_match.group(1).split(',')
                # Normalize each value in the array by removing quotes
                condition_json["value"] = [remove_quotes(value.strip()) for value in values]
        elif condition_json["operator"] in {"IS NULL", "IS NOT NULL"}:
            # Handle IS NULL and IS NOT NULL conditions
            condition_json["value"] = None
        else:
            if operator_substring.upper() in {"TRUE", "FALSE"}:
                condition_json["value"] = operator_substring.upper()
            else:
                condition_json["value"] = remove_quotes(operator_substring)

        # Extract the field name
        condition_json["field"] = condition[:operator_start_index].strip()
    else: 
        # If no operator is found, treat the entire condition as a field
        condition_json["field"] = condition.strip()

    # Extract transformations from the field if any (eg. TRIM, UPPER)
    field = condition_json["field"]
    transformations = []
    sequence = 1

    while re.search(function_pattern, field):
        function_match = re.search(function_pattern, field)
        if function_match:
            function_name = function_match.group(1).upper()
            function_args = function_match.group(2).strip() 

            # Extract parameters and update the field
            result = extract_params_from_function_string(function_args, function_name)

            # Update the remaining field
            condition_json["field"] = result["field"]

            # Add the transformation to the list
            transformations.append({
                "name": function_name,
                "params": result["params"],
                "sequence": sequence
            })
            sequence += 1

            # Update the field to remove the function part
            field = condition_json["field"]
        else:
            break

    # Assign sequence number from 1 to n (inner to outer)
    for i, transformation in enumerate(reversed(transformations), start=1):
        transformation["sequence"] = i
        condition_json["transformations"] = transformations[::-1]  # Reverse to maintain the order from inner to outer

    # Assign transformations to the condition JSON
    condition_json["transformations"] = transformations

    # Remove value and valueType if the value is None
    if condition_json.get("value") is None:
        condition_json.pop("value", None)
        condition_json.pop("valueType", None)

    return condition_json


def remove_quotes(value: str) -> str:
    """
    Normalizes multiple quotes from a string value.
    
    Args:
        value (str): The string value to process.
        
    Returns:
        str: The value without quotes.
    """
    if not isinstance(value, str):
        return value
    
    # Normalize double and single quotes
    value = re.sub(r'(^"+)|("+$)', '"', value)  
    value = re.sub(r"(^'+)|('+)$", "'", value)

    # Remove single pair of surrounding quotes (if any)
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]

    return value


def extract_params_from_function_string(function_args: str, function_name: str) -> dict:
    function_name = function_name.upper()
    if function_name not in SUPPORTED_SQL_TRANSFORMATIONS:
        logger.error(f"Unsupported SQL function: {function_name}")
        raise InvalidRequestException(f"Unsupported SQL function: {function_name}")
    
    # Extract the parameters using the count
    return extract_params_value(function_args, SUPPORTED_SQL_TRANSFORMATIONS[function_name])


def extract_params_value(function_args: str, count: int) -> dict:
    reversed_function_args = function_args[::-1]

    params = []
    remaining_args = reversed_function_args

    for _ in range(count):
        # Find the position of next comma
        comma_index = remaining_args.find(',')

        if comma_index == -1:
            logger.error(f"Invalid parameters provided, expected {count} parameters but got fewer.")
            raise InvalidRequestException(f"Invalid parameters provided, expected {count} parameters but got fewer.")
        
        # Extract the parameter up to the next comma
        param = remaining_args[:comma_index][::-1].strip()
        params.append(get_value(param))

        # Update the remaining arguments
        remaining_args = remaining_args[comma_index + 1:].strip()

    # Reverse the remaining arguments to maintain the original order
    updated_args = remaining_args[::-1].strip()

    return {
        "params": params[::-1],
        "field": updated_args
    }


def get_value(value: str) -> Union[str, int, float, bool]:
    # Remove quotes from the value
    value = remove_quotes(value)

    # Check if the value is boolean
    if value.upper() in {"TRUE", "FALSE"}:
        return value.upper() == "TRUE"
    
    # Check if the value is numeric
    if re.match(r"^-?\d+(\.\d+)?$", value):
        if '.' in value:
            return float(value)
        else:
            return int(value)

    # If none of the above, return as string
    return value

