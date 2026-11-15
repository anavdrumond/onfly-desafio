"""Execução do CLI com argumentos arbitrários, para testes de contrato e da amostra."""

from __future__ import annotations

import csv
import os
import subprocess
import sys
from pathlib import Path

from helpers import BASE, COLUMNS, PROJECT_ROOT, SRC_DIR

DATA_DIR = PROJECT_ROOT / "data"
RATES_FILE = DATA_DIR / "taxas_cambio.csv"


def write_reservations(path: Path, rows: list[dict[str, str]]) -> Path:
    """Grava um CSV de reservas partindo da linha base dos testes fornecidos."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows({**BASE, **row} for row in rows)
    return path


def run_module(args: list[str], cwd: Path = PROJECT_ROOT) -> subprocess.CompletedProcess:
    """Executa `python -m onfly_report` sem exigir sucesso."""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + environment.get("PYTHONPATH", "")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "onfly_report", *args],
        cwd=str(cwd),
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )
