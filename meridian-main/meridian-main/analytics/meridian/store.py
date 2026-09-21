"""Reading and forecast storage.

Thin wrapper over the SQLite store the collector writes into.  We do
not own the schema for `reading`; the C collector creates it.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Iterator, Sequence

FORECAST_DDL = """
CREATE TABLE IF NOT EXISTS forecast (
    stnid   TEXT NOT NULL,
    year    INTEGER NOT NULL,
    run_at  TEXT NOT NULL,
    yield_t REAL NOT NULL,
    ndays   INTEGER NOT NULL,
    model   TEXT NOT NULL,
    PRIMARY KEY (stnid, year)
)
"""

SERIES_DDL = """
CREATE TABLE IF NOT EXISTS forecast_daily (
    stnid TEXT NOT NULL,
    year  INTEGER NOT NULL,
    doy   INTEGER NOT NULL,
    sw    REAL, et REAL, drain REAL, biom REAL, lai REAL,
    PRIMARY KEY (stnid, year, doy)
)
"""


@dataclass(frozen=True)
class Reading:
    stnid: str
    year: int
    doy: int
    tmax: float
    tmin: float
    rain: float
    srad: float


class Store:
    def __init__(self, path: str):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(FORECAST_DDL)
        self.conn.execute(SERIES_DDL)
        self.conn.commit()

    def stations(self) -> list[str]:
        cur = self.conn.execute("SELECT DISTINCT stnid FROM reading ORDER BY stnid")
        return [r["stnid"] for r in cur]

    def years(self, stnid: str) -> list[int]:
        cur = self.conn.execute(
            "SELECT DISTINCT year FROM reading WHERE stnid = ? ORDER BY year", (stnid,)
        )
        return [r["year"] for r in cur]

    def readings(self, stnid: str, year: int) -> list[Reading]:
        cur = self.conn.execute(
            "SELECT stnid, year, doy, tmax, tmin, rain, srad "
            "FROM reading WHERE stnid = ? AND year = ? ORDER BY doy",
            (stnid, year),
        )
        return [
            Reading(r["stnid"], r["year"], r["doy"],
                    r["tmax"], r["tmin"], r["rain"], r["srad"])
            for r in cur
        ]

    def save_forecast(self, stnid, year, run_at, yield_t, ndays, model, daily):
        self.conn.execute(
            "INSERT OR REPLACE INTO forecast"
            " (stnid, year, run_at, yield_t, ndays, model)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (stnid, year, run_at, yield_t, ndays, model),
        )
        self.conn.executemany(
            "INSERT OR REPLACE INTO forecast_daily"
            " (stnid, year, doy, sw, et, drain, biom, lai)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [(stnid, year, d.doy, d.sw, d.et, d.drain, d.biom, d.lai) for d in daily],
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
