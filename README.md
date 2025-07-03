# SQL Expression to JSON Converter

## Overview

**SQL Expression to JSON Converter** is a FastAPI-based web application that allows users to convert simple SQL expressions into their equivalent JSON representations. This tool is designed for developers and data engineers who need to parse and transform SQL queries into a structured JSON format for further processing or integration.

## Features

- Converts simple SQL expressions to JSON format
- Fast and lightweight API built with FastAPI
- Easy to integrate into existing workflows

## Getting Started

### Prerequisites

- Python 3.8 or higher
- `pip` (Python package manager)

### Installation

1. **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd sql-expression-to-json-convertor
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

### Running the Application

Start the FastAPI server using the following command:

```sh
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

- The API will be available at: `http://127.0.0.1:8080`

## API Usage

### Endpoint

`POST /convert`

### Request Body

| Field           | Type   | Description                  |
|-----------------|--------|------------------------------|
| sql_expression  | string | The SQL expression to parse  |

#### Example Request

```json
{
  "sql_expression": "ROUND(per, 2) = 77.89 AND (SUBSTR(UPPER(TRIM(field)), 0, 10) = 'Value' OR TRIM(field2) IN (\"val1\", 'val2')) AND UCASE(TRIM(field3)) = TRUE"
}
```

#### Example Response

```json
{
  "conditions": [
    {
      "transformations": [
        {
          "name": "ROUND",
          "params": [2],
          "sequence": 1
        }
      ],
      "operator": "=",
      "valueType": "string",
      "value": "77.89",
      "field": "per"
    },
    {
      "logical_operator": "OR",
      "conditions": [
        {
          "transformations": [
            {
              "name": "SUBSTR",
              "params": [0, 10],
              "sequence": 3
            },
            {
              "name": "UPPER",
              "params": [],
              "sequence": 2
            },
            {
              "name": "TRIM",
              "params": [],
              "sequence": 1
            }
          ],
          "operator": "=",
          "valueType": "string",
          "value": "Value",
          "field": "field"
        },
        {
          "transformations": [
            {
              "name": "TRIM",
              "params": [],
              "sequence": 1
            }
          ],
          "operator": "IN",
          "valueType": "string",
          "value": ["val1", "val2"],
          "field": "field2"
        }
      ]
    },
    {
      "transformations": [
        {
          "name": "UCASE",
          "params": [],
          "sequence": 2
        },
        {
          "name": "TRIM",
          "params": [],
          "sequence": 1
        }
      ],
      "operator": "=",
      "valueType": "string",
      "value": "TRUE",
      "field": "field3"
    }
  ],
  "logical_operator": "AND"
}
```

---

## JSON Output Structure

- **conditions**: List of condition objects or nested groups.
- **logical_operator**: Logical operator (`AND`/`OR`) applied at the current level.
- **transformations**: List of SQL functions applied to the field, with parameters and sequence.
- **operator**: Comparison operator (e.g., `=`, `IN`, `IS NULL`).
- **valueType**: Type of the value (currently always `"string"`).
- **value**: Value(s) for the condition.
- **field**: The field/column name being compared.

--

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for improvements.
