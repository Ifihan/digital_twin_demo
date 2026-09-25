"""Tool definitions the LLM can call (Week 3)."""
import ast
import operator
from datetime import datetime


def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%A, %d %B %Y, %H:%M")


OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def calculate(expression: str) -> str:
    """Calculate a maths expression, for example '8500 / 3' or '(12 + 4) * 2'."""
    def evaluate(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](evaluate(node.left), evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](evaluate(node.operand))
        raise ValueError("Unsupported expression")

    try:
        return str(evaluate(ast.parse(expression, mode="eval").body))
    except (ValueError, SyntaxError, ZeroDivisionError) as e:
        return f"Error: {e}"


TOOLS = [get_current_time, calculate]
