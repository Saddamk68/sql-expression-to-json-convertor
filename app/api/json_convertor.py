from fastapi import APIRouter
from app.service.converter import convert_sql_expression_to_json

router = APIRouter()

@router.get("/sql_expr_to_json_convertor")
async def sql_expr_to_json_convertor(sql_expression: str):
    """
    Convert string SQL expression to JSON format.
    """
    return convert_sql_expression_to_json(sql_expression)
