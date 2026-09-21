"""Runs the numerical core for a station-year and stores the result.

The cropmod binary reads and writes files with fixed names in its
current working directory, so every run happens in a scratch directory
and runs are serialised.  This is the single largest constraint on the
whole platform and is why the nightly batch takes four hours.
See MRD-201.
"""
from __future__ import annotations

import datetime as _dt
import os
import shutil
import subprocess
import tempfile

from . import deck, parse
from .store import Store

MODEL_BINARY = os.environ.get(
    "MERIDIAN_CROPMOD",
    os.path.join(os.path.dirname(__file__), "..", "..", "model", "cropmod"),
)
RUN_TIMEOUT_S = 120


class ModelRunError(RuntimeError):
    pass


def run_station_year(store: Store, stnid: str, year: int, keep_scratch: bool = False):
    readings = store.readings(stnid, year)
    if not readings:
        raise ModelRunError("no readings for %s %d" % (stnid, year))

    scratch = tempfile.mkdtemp(prefix="cropmod-")
    try:
        deck_path = os.path.join(scratch, deck.DECK_NAME)
        n = deck.write_deck(deck_path, stnid, year, readings)

        binary = os.path.abspath(MODEL_BINARY)
        if not os.path.exists(binary):
            raise ModelRunError("cropmod binary not found at %s" % binary)

        proc = subprocess.run(
            [binary],
            cwd=scratch,
            capture_output=True,
            text=True,
            timeout=RUN_TIMEOUT_S,
        )
        if proc.returncode != 0:
            raise ModelRunError(
                "cropmod exited %d: %s" % (proc.returncode, proc.stderr.strip()[:200])
            )

        out_path = os.path.join(scratch, parse.OUT_NAME)
        if not os.path.exists(out_path):
            raise ModelRunError("cropmod wrote no output file")

        result = parse.parse_output(out_path)
        run_at = _dt.datetime.now().isoformat(timespec="seconds")

        store.save_forecast(
            stnid=stnid,
            year=year,
            run_at=run_at,
            yield_t=result["yield_t"],
            ndays=result["ndays"],
            model=result["model"],
            daily=result["rows"],
        )
        result["deck_days"] = n
        return result
    finally:
        if not keep_scratch:
            shutil.rmtree(scratch, ignore_errors=True)


def run_all(store: Store):
    out = []
    for stn in store.stations():
        for yr in store.years(stn):
            out.append(run_station_year(store, stn, yr))
    return out
