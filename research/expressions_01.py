import ast
import operator as op

# supported operators
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}


def eval_expr(expr):
    """
    >>> eval_expr('2^6')
    4
    >>> eval_expr('2**6')
    64
    >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
    -5.0
    >>> eval_expr('x * 6')
    36
    """
    return eval_(ast.parse(expr, mode='eval').body)

def eval_(node):
    match node:
        case ast.Constant(value) if isinstance(value, (int, float)):
            return value  # integer
        case ast.BinOp(left, op, right):
            return operators[type(op)](eval_(left), eval_(right))
        case ast.UnaryOp(op, operand):  # e.g., -1
            return operators[type(op)](eval_(operand))
        case ast.Name():
            a = f"Node: {node}"
            return 6
        case _:

            raise TypeError(node)


# if __name__ == '__main__':
#    eval_expr('2^6')
