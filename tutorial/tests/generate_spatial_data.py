import gstools as gs
from numpy.typing import ArrayLike


def generate_random_field(n: int) -> ArrayLike:
    # structured field with a size 100x100 and a grid-size of 1x1
    x = y = range(100)
    model = gs.Gaussian(dim=2, var=1, len_scale=10)
    srf = gs.SRF(model)
    srf((x, y), mesh_type="structured")
    srf.plot()
