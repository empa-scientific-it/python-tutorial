import numpy as np


def reference_minimize():
    from scipy.optimize import minimize

    def f(x):
        return 3 * x**2 - 5 * x - 4

    return minimize(f, 0)


def test_minimize(function_to_test):
    assert reference_minimize() == function_to_test()


def reference_root_finder():
    from scipy.optimize import root

    # 1. TODO: define the function here:
    def f(x):
        return x**3 - 6 * x**2 + 4 * x + 12

    # 2. TODO: call the root function here:
    sol1, sol2, sol3 = root(f, -1.0).x, root(f, 2.5).x, root(f, 4.5).x
    return sol1, sol2, sol3


def test_root_finder(function_to_test):
    sol_ref = reference_root_finder()
    sol_test = function_to_test()
    for i in range(3):
        assert sol_ref[i] == sol_test[i]


def reference_lu():
    from scipy.linalg import lu

    # 1. TODO: define the matrix a_ref here:
    a_ref = np.array([[9, 3, 3], [3, 2, 2], [3, 4, 2]])
    # 2. TODO: call the lu function here:
    p_matrix, l_matrix, u_matrix = lu(a_ref)

    # 3. TODO: return p, l, u matrices in this order here:
    return p_matrix, l_matrix, u_matrix


def test_lu(function_to_test):
    sol_ref = reference_lu()
    sol_test = function_to_test()
    for i in range(3):
        assert np.all(np.isclose(sol_ref[i], sol_test[i]))


def reference_svd():
    from numpy.linalg import svd

    # 1. TODO: define the matrix a_ref here:
    a_ref = np.array([[9, 3, 3], [3, 2, 2], [3, 4, 2]])
    # 2. TODO: call the svd function here:
    u, s, vh = svd(a_ref)
    return u, s, vh


def test_svd(function_to_test):
    sol_ref = reference_svd()
    sol_test = function_to_test()
    for i in range(3):
        assert np.all(np.isclose(sol_ref[i], sol_test[i]))


def reference_gaussian():
    from scipy.optimize import curve_fit

    xdata = [
        -10.0,
        -9.0,
        -8.0,
        -7.0,
        -6.0,
        -5.0,
        -4.0,
        -3.0,
        -2.0,
        -1.0,
        0.0,
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        7.0,
        8.0,
        9.0,
        10.0,
    ]
    ydata = [
        1.2,
        4.2,
        6.7,
        8.3,
        10.6,
        11.7,
        13.5,
        14.5,
        15.7,
        16.1,
        16.6,
        16.0,
        15.4,
        14.4,
        14.2,
        12.7,
        10.3,
        8.6,
        6.1,
        3.9,
        2.1,
    ]
    xdata = np.array(xdata)
    ydata = np.array(ydata)

    # 2. TODO: define the gaussian function here:
    def ref_gaussian_math(x, a, b):
        return a * np.exp(-b * x**2)

    # 3. TODO: call the curve_fit function here:
    parameters, covariance = curve_fit(ref_gaussian_math, xdata, ydata)
    return parameters, covariance


def test_gaussian(function_to_test):
    sol_ref = reference_gaussian()
    sol_test = function_to_test()
    for i in range(2):
        assert np.all(np.isclose(sol_ref[i], sol_test[i]))


def reference_dblquad():
    from scipy.integrate import dblquad

    # 1. TODO: define the function to integrate here:
    def f(y, x):
        return 3 * x + 2 * y

    # 2. TODO: define the upper and lower limits:

    # 3. TODO: call the dblquad function here:
    result, error = dblquad(func=f, a=0, b=2, gfun=lambda x: x, hfun=lambda x: 6 - x**2)

    # 4. TODO: return the result and the error in this order here:
    return result, error


def test_dblquad(function_to_test):
    assert np.isclose(function_to_test()[0], reference_dblquad()[0])
    # assert dblquad(function_to_test)[1] == reference_dblquad()[1]


def reference_odeint():
    import numpy as np
    from scipy.integrate import odeint

    # 1. TODO: define dydt here:
    k = 0.2

    def dydt(y, t):
        return -k * y

    # 2. TODO: define the initial condition here:
    y0 = 5

    # 3. TODO: define the time points here:
    t = np.linspace(0, 10, 101)

    # 4. TODO: call the odeint function here:
    y = odeint(dydt, y0, t)

    return y.T[0]


def test_odeint(function_to_test):
    assert np.all(np.isclose(reference_odeint(), function_to_test()))
