def heat_index(temperature, humidity):
    assert temperature >= 27.0
    assert humidity >= 40.0

    c1 = -8.784695
    c2 = 1.61139411
    c3 = 2.338549
    c4 = -0.14611605
    c5 = -1.2308094e-2
    c6 = -1.6424828e-2
    c7 = 2.211732e-3
    c8 = 7.2546e-4
    c9 = -3.582e-6
    
    return c1 + \
        c2 * temperature + \
        c3 * humidity + \
        c4 * temperature * humidity + \
        c5 * temperature * temperature + \
        c6 * humidity * humidity + \
        c7 * temperature * temperature * humidity + \
        c8 * temperature * humidity * humidity + \
        c9 * temperature * temperature * humidity * humidity