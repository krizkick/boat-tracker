import io
import math

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from PIL import Image, ImageDraw

# Skipsform i båtens eget system: x = styrbord, y = fremover
BAAT_FORM = [(0, 1), (0.6, 0.3), (0.6, -0.8), (-0.6, -0.8), (-0.6, 0.3)]


def _kart_bilde(proj, SIZE_KM, WIDTH, HEIGHT, DPI):
    """Land (svart) på hav (hvitt), gjort om til 1-bit uten antialiasing."""
    fig = plt.figure(figsize=(WIDTH / DPI, HEIGHT / DPI), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1], projection=proj)

    half_x = SIZE_KM / 2 * 1000
    half_y = half_x * HEIGHT / WIDTH
    ax.set_extent([-half_x, half_x, -half_y, half_y], crs=proj)
    ax.axis("off")
    ax.add_feature(cfeature.GSHHSFeature(scale="f", levels=[1]),
                   facecolor="black", edgecolor="none")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI, facecolor="white")
    plt.close(fig)
    buf.seek(0)

    img = Image.open(buf).convert("L").resize((WIDTH, HEIGHT))
    return img.point(lambda v: 255 if v >= 128 else 0).convert("1")


def _stiplet(draw, a, b, dash=6, gap=4, width=2):
    dx, dy = b[0] - a[0], b[1] - a[1]
    lengde = math.hypot(dx, dy)
    if lengde == 0:
        return
    ux, uy = dx / lengde, dy / lengde
    pos = 0
    while pos < lengde:
        slutt = min(pos + dash, lengde)
        draw.line([(a[0] + ux * pos, a[1] + uy * pos),
                   (a[0] + ux * slutt, a[1] + uy * slutt)], fill=0, width=width)
        pos += dash + gap


def _baat_punkter(cx, cy, kurs, skala):
    t = math.radians(kurs)
    pts = []
    for px, py in BAAT_FORM:
        ost = px * math.cos(t) + py * math.sin(t)
        nord = -px * math.sin(t) + py * math.cos(t)
        pts.append((cx + skala * ost, cy - skala * nord))
    return pts


def lag_kart(boat, SIZE_KM, WIDTH, HEIGHT, minutter=(),
             OUTPUT_PNG="kart.png", OUTPUT_BIN="kart.bin", DPI=256):
    proj = ccrs.LambertAzimuthalEqualArea(
        central_longitude=boat.longitude,
        central_latitude=boat.latitude
    )
    img = _kart_bilde(proj, SIZE_KM, WIDTH, HEIGHT, DPI)
    draw = ImageDraw.Draw(img)

    m_per_px = SIZE_KM * 1000 / WIDTH
    geo = ccrs.PlateCarree()

    def til_piksel(lat, lon):
        x, y = proj.transform_point(lon, lat, geo)
        return WIDTH / 2 + x / m_per_px, HEIGHT / 2 - y / m_per_px

    cx, cy = WIDTH / 2, HEIGHT / 2      # båten er alltid midt i kartet

    # Prognose
    prognoser = [boat.boat_future_position(m) for m in minutter]
    if prognoser:
        slutt = til_piksel(prognoser[-1]["future_latitude"],
                           prognoser[-1]["future_longitude"])
        draw.line([(cx, cy), slutt], fill=1, width=5)       # hvit kant under
        _stiplet(draw, (cx, cy), slutt)
        for p in prognoser:
            x, y = til_piksel(p["future_latitude"], p["future_longitude"])
            draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=1)
            draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=0)

    # Båt: hvit glorie, svart kant, hvit fyll
    draw.polygon(_baat_punkter(cx, cy, boat.course, 13), fill=1)
    pts = _baat_punkter(cx, cy, boat.course, 10)
    draw.polygon(pts, fill=0)
    draw.polygon(_baat_punkter(cx, cy, boat.course, 7), fill=1)

    img.save(OUTPUT_PNG)
    with open(OUTPUT_BIN, "wb") as f:
        f.write(img.tobytes())