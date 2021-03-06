"""app.sentinel: handle request for Sentinel-tiler."""

import json

from rio_tiler import sentinel2
from rio_tiler.profiles import img_profiles
from rio_tiler.utils import array_to_image, get_colormap, expression

from .utils import _postprocess

from lambda_proxy.proxy import API

APP = API(app_name="sentinel-tiler")


class SentinelTilerError(Exception):
    """Base exception class."""


@APP.route(
    "/s2/bounds/<scene>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
def bounds(scene):
    """Handle bounds requests."""
    info = sentinel2.bounds(scene)
    return ("OK", "application/json", json.dumps(info))


@APP.route(
    "/s2/metadata/<scene>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
def metadata(scene, pmin=2, pmax=98):
    """Handle metadata requests."""
    pmin = float(pmin) if isinstance(pmin, str) else pmin
    pmax = float(pmax) if isinstance(pmax, str) else pmax
    info = sentinel2.metadata(scene, pmin, pmax)
    return ("OK", "application/json", json.dumps(info))


@APP.route(
    "/s2/tiles/<scene>/<int:z>/<int:x>/<int:y>.<ext>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
@APP.route(
    "/s2/tiles/<scene>/<int:z>/<int:x>/<int:y>@<int:scale>x.<ext>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
def tile(
    scene,
    z,
    x,
    y,
    scale=1,
    ext="png",
    bands=None,
    expr=None,
    rescale=None,
    color_formula=None,
    color_map=None,
):
    """Handle tile requests."""
    if ext == "jpg":
        driver = "jpeg"
    elif ext == "jp2":
        driver = "JP2OpenJPEG"
    else:
        driver = ext

    if bands and expr:
        raise SentinelTilerError("Cannot pass bands and expression")
    if not bands and not expr:
        raise SentinelTilerError("Need bands or expression")

    if bands:
        bands = tuple(bands.split(","))

    tilesize = scale * 256

    if expr is not None:
        tile, mask = expression(scene, x, y, z, expr, tilesize=tilesize)

    elif bands is not None:
        tile, mask = sentinel2.tile(scene, x, y, z, bands=bands, tilesize=tilesize)

    rtile, rmask = _postprocess(
        tile, mask, tilesize, rescale=rescale, color_formula=color_formula
    )

    if color_map:
        color_map = get_colormap(color_map, format="gdal")

    options = img_profiles.get(driver, {})
    return (
        "OK",
        f"image/{ext}",
        array_to_image(rtile, rmask, img_format=driver, color_map=color_map, **options),
    )


@APP.route("/favicon.ico", methods=["GET"], cors=True)
def favicon():
    """Favicon."""
    return ("NOK", "text/plain", "")
