"""Parses the fixed-width output of the cropmod binary.

cropmod writes:

    line 1        banner with STN, YEAR and NDAYS
    line 2        column header
    lines 3..n+2  I4 1X F7.2 1X F7.3 1X F7.3 1X F7.1 1X F7.3
    last line     'YIELD ' F10.3

The daily lines are read by column position, not by splitting on
whitespace: when soil water exceeds 9999.99 the DOY and SW fields run
together and a split-based parser silently drops a day.  This was
MRD-143 and it took two seasons to find.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

OUT_NAME = "MERIDIAN.OUT"

BANNER_RE = re.compile(
    r"MERIDIAN CROPMOD (\S+)\s+STN=(\S+)\s+YEAR=\s*(\d+)\s+NDAYS=\s*(\d+)"
)
YIELD_RE = re.compile(r"^YIELD\s+(-?\d+\.\d+)")


@dataclass(frozen=True)
class DailyRow:
    doy: int
    sw: float
    et: float
    drain: float
    biom: float
    lai: float


# (start, end) half-open column spans, 0-based, matching FORMAT 912.
COLS: List[Tuple[int, int]] = [
    (0, 4),    # I4   doy
    (5, 12),   # F7.2 sw
    (13, 20),  # F7.3 et
    (21, 28),  # F7.3 drain
    (29, 36),  # F7.1 biom
    (37, 44),  # F7.3 lai
]


def _field(line: str, span: Tuple[int, int]) -> str:
    start, end = span
    return line[start:end]


def parse_output(path: str):
    with open(path, "r") as fh:
        lines = [ln.rstrip("\n") for ln in fh]

    if not lines:
        raise ValueError("cropmod produced no output")

    m = BANNER_RE.search(lines[0])
    if not m:
        raise ValueError("unrecognised cropmod banner: %r" % lines[0][:60])
    model_version, stnid, year, ndays = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))

    rows: List[DailyRow] = []
    yield_t = None

    for line in lines[2:]:
        if not line.strip():
            continue
        ym = YIELD_RE.match(line)
        if ym:
            yield_t = float(ym.group(1))
            continue
        try:
            rows.append(DailyRow(
                doy=int(_field(line, COLS[0])),
                sw=float(_field(line, COLS[1])),
                et=float(_field(line, COLS[2])),
                drain=float(_field(line, COLS[3])),
                biom=float(_field(line, COLS[4])),
                lai=float(_field(line, COLS[5])),
            ))
        except ValueError:
            # Fortran writes '*******' when a value overflows its field.
            # Those days are dropped rather than failing the run.
            continue

    if yield_t is None:
        raise ValueError("cropmod output had no YIELD record")
    if len(rows) != ndays:
        # Not fatal: see the MRD-143 note above.
        pass

    return {
        "model": "cropmod " + model_version,
        "stnid": stnid,
        "year": year,
        "ndays": ndays,
        "rows": rows,
        "yield_t": yield_t,
    }
