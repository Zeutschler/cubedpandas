import ast
import operator as op


class Expression:
    # supported operators
    operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
                 ast.Div: op.truediv, ast.Pow: op.pow,
                 ast.And: op.and_, ast.Or: op.or_,
                 ast.Not: op.not_, ast.BitXor: op.xor,
                 ast.USub: op.neg}

    def __init__(self):
        from cubedpandas.cube import Cube
        from cubedpandas.dimension import Dimension
        from cubedpandas.measure import Measure

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return " Expression Evaluator"

    def eval(self, expression: str):
        if not isinstance(expression, str):
            raise TypeError("Expression must be a string")
        return self._eval(ast.parse(expression, mode='eval').body)


    def _eval(self, node):
        match node:
            case ast.Constant(value):
                return value
            case ast.BinOp(left, op, right):
                return self.operators[type(op)](self._eval(left), self._eval(right))
            case ast.UnaryOp(op, operand):  # e.g., -1
                return self.operators[type(op)](self._eval(operand))
            case ast.Name():
                return 6
            case _:
                raise TypeError(node)


if __name__ == '__main__':
    print(Expression().eval("x * 6"))
