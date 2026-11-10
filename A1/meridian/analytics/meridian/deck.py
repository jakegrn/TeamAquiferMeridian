"""Writes the fixed-width input deck the cropmod binary expects.

The format is defined by the FORMAT statements in model/cropmod.f and
is documented in docs/DECKFMT.txt.  It is column-exact.  If you change
a width here you must change it there, and the model has to be
re-validated afterwards, which is why nobody does.

    header 1 : A8   I4   F8.3        stnid, year, latitude
    header 2 : F8.2 F8.2             awc, rooting depth
    daily    : I3   F6.1 F6.1 F6.1 F6.2   doy, tmax, tmin, rain, srad
    trailer  : ' -1'
"""
from __future__ import annotations

from typing import Iterable, Sequence

DECK_NAME = "MERIDIAN.DAT"

# Soil parameters by station.  These live here rather than in the store
# because the 2008 schema has nowhere to put them.  MRD-91 is open to
# move them into a proper table.
SOIL = {
    # Station ids are the A8 fixed-width field in the deck, so <= 8 characters.
    "GUELPH":   (0.150, 1100.0),
    "KITCHNER": (0.142, 1050.0),
    "WATERLOO": (0.138, 1000.0),
    "CAMBRIDG": (0.155, 1200.0),
    "MILTON":   (0.148, 950.0),
    "BRANTFRD": (0.162, 900.0),
}
DEFAULT_SOIL = (0.145, 1000.0)

LATITUDE = {
    "GUELPH":   43.545,
    "KITCHNER": 43.451,
    "WATERLOO": 43.466,
    "CAMBRIDG": 43.360,
    "MILTON":   43.509,
    "BRANTFRD": 43.139,
}
DEFAULT_LAT = 43.545


def soil_for(stnid: str):
    return SOIL.get(stnid.upper(), DEFAULT_SOIL)


def latitude_for(stnid: str) -> float:
    return LATITUDE.get(stnid.upper(), DEFAULT_LAT)


def write_deck(path: str, stnid: str, year: int, readings: Sequence) -> int:
    awc, rdepth = soil_for(stnid)
    lat = latitude_for(stnid)

    lines = []
    lines.append("%-8s%4d%8.3f" % (stnid[:8], year, lat))
    lines.append("%8.2f%8.2f" % (awc, rdepth))

    n = 0
    for r in readings:
        lines.append("%3d%6.1f%6.1f%6.1f%6.2f" % (
            r.doy, r.tmax, r.tmin, r.rain, r.srad))
        n += 1

    lines.append(" -1")

    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return n
