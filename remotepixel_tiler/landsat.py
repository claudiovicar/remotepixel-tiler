"""app.landsat: handle request for Landsat-tiler."""

import json

from rio_tiler import landsat8
from rio_tiler.profiles import img_profiles
from rio_tiler.utils import array_to_image, get_colormap, expression

from .utils import _postprocess

from lambda_proxy.proxy import API

APP = API(app_name="landsat-tiler")


class LandsatTilerError(Exception):
    """Base exception class."""


@APP.route(
    "/bounds/<scene>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
def bounds(scene):
    """Handle bounds requests."""
    info = landsat8.bounds(scene)
    return ("OK", "application/json", json.dumps(info))


@APP.route(
    "/metadata/<scene>",
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
    info = landsat8.metadata(scene, pmin, pmax)
    return ("OK", "application/json", json.dumps(info))


@APP.route(
    "/tiles/<scene>/<int:z>/<int:x>/<int:y>.<ext>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
@APP.route(
    "/tiles/<scene>/<int:z>/<int:x>/<int:y>@<int:scale>x.<ext>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
def tiles(
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
    pan=False,
):
    """Handle tile requests."""
    if ext == "jpg":
        driver = "jpeg"
    elif ext == "jp2":
        driver = "JP2OpenJPEG"
    else:
        driver = ext

    if bands and expr:
        raise LandsatTilerError("Cannot pass bands and expression")
    if not bands and not expr:
        raise LandsatTilerError("Need bands or expression")

    if bands:
        bands = tuple(bands.split(","))

    tilesize = scale * 256

    pan = True if pan else False

    if expr is not None:
        tile, mask = expression(scene, x, y, z, expr, tilesize=tilesize)  # , pan=pan)

    elif bands is not None:
        tile, mask = landsat8.tile(
            scene, x, y, z, bands=bands, tilesize=tilesize  # , pan=pan
        )

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
