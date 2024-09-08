import math

from cubedpandas.common import smart_round


# performance test for smart_round
def test_smart_round(count: int = 1000, loops: int = 1000):
    import datetime
    import random
    import time

    values = [random.random() * 1000000 + random.random() * 1000000 for _ in range(count)]

    start = time.time()
    for _ in range(loops):
        for v in values:
            smart_round(v)
    end = time.time()
    return end - start


def compare_results(count: int = 10):
    import random
    for n in range(-count, count):
        value = random.random() * math.pow(10, n)
        v1 = smart_round(value)
        print(f"{value:<24} {v1:<16} delta%: {(value - v1)/value:0.16f}")



if __name__ == "__main__":
    #print(f"smart_round( , 1) in {test_smart_round(1)} seconds.")
    #print(f"smart_round( , 2) in {test_smart_round(1)} seconds.")
    compare_results()