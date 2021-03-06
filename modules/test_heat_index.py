import modules.heat_index
import math

def test_heat_index():
    '''

    Test table taken from:
    https://de.wikipedia.org/wiki/Hitzeindex#Warntabelle

    '''

    temps = [27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]
    humid = [40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]

    his = [
        [27, 28, 29, 30, 31, 32, 34, 35, 37, 39, 41, 43, 46, 48, 51, 54, 57],
        [27, 28, 29, 30, 32, 33, 35, 37, 39, 41, 43, 46, 49, 51, 54, 57],
        [27, 28, 30, 31, 33, 34, 36, 38, 41, 43, 46, 49, 52, 55, 58],
        [28, 29, 30, 32, 34, 36, 38, 40, 43, 46, 48, 52, 55, 59],
        [28, 29, 31, 33, 35, 37, 40, 42, 45, 48, 51, 55, 59],
        [28, 30, 32, 34, 36, 39, 41, 44, 48, 51, 55, 59],
        [29, 31, 33, 35, 38, 40, 43, 47, 50, 54, 58],
        [29, 31, 34, 36, 39, 42, 46, 49, 53, 58],
        [30, 32, 35, 38, 41, 44, 48, 52, 57],
        [30, 33, 36, 39, 43, 47, 51, 55],
        [31, 34, 37, 41, 45, 49, 54],
        [31, 35, 38, 42, 47, 51, 57],
        [32, 36, 40, 44, 49, 54],
    ]

    for hidx, row in enumerate(his):
        for tidx, val in enumerate(row):
            t = temps[tidx]
            h = humid[hidx]
            hi = modules.heat_index.heat_index(t,h)
            print(t, h, hi, val)
            assert val == round(hi)