import math


def softmax(xs):
    norm = sum(math.exp(x) for x in xs)
    return [math.exp(x) / norm for x in xs]
