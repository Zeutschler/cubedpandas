class Bar:
    @property
    def baz(self) -> int:
        return 1

class Foo:
    def __getattr__(self, name) -> Bar:
        return Bar()

f = Foo()
b = Bar()
assert (type(f.bar) == type(Bar()))
assert (type(f.xyz) == type(Bar()))


# Type hint for non-existing attribute `f.bar` shows the `baz` attribute 👍
print(f.bar)

# ...but for non-existing attribute `f.xyz` it doesn't 👎. Bug or feature?
print(f.xyz)


