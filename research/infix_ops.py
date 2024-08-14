class Infix:
    def __init__(self, func, lhs=None):
        self.func = func
        self.lhs = lhs

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __ror__(self, lhs):
        return __class__(self.func, lhs)

    def __or__(self, rhs):
        return self(self.lhs, rhs)


add = Infix(lambda a, b: a+b)
print(4 | add | 5)
