"""Testes adicionais: contrato do CLI e schema do relatório."""

import json
import re

import pytest
from cli_runner import RATES_FILE, run_module, write_reservations
from helpers import run_cli


@pytest.mark.parametrize(
    "extra_args",
    [["--top", "0"], ["--top", "-1"], ["--top", "abc"]],
    ids=["top-zero", "top-negativo", "top-nao-inteiro"],
)
def test_invalid_top_exits_with_code_2(tmp_path, extra_args):
    input_path = write_reservations(tmp_path / "reservas.csv", [{}])
    output_path = tmp_path / "report.json"
    process = run_module(
        ["--input", str(input_path), "--rates", str(RATES_FILE), "--output", str(output_path), *extra_args]
    )
    assert process.returncode == 2
    assert not output_path.exists()


@pytest.mark.parametrize("missing", ["--input", "--rates"])
def test_missing_required_argument_exits_with_code_2(tmp_path, missing):
    input_path = write_reservations(tmp_path / "reservas.csv", [{}])
    args = {"--input": str(input_path), "--rates": str(RATES_FILE), "--output": str(tmp_path / "report.json")}
    del args[missing]
    process = run_module([item for pair in args.items() for item in pair])
    assert process.returncode == 2


@pytest.mark.parametrize("missing_file", ["input", "rates"])
def test_nonexistent_input_file_exits_with_code_2(tmp_path, missing_file):
    input_path = write_reservations(tmp_path / "reservas.csv", [{}])
    paths = {"input": input_path, "rates": RATES_FILE, missing_file: tmp_path / "nao-existe.csv"}
    output_path = tmp_path / "report.json"
    process = run_module(
        ["--input", str(paths["input"]), "--rates", str(paths["rates"]), "--output", str(output_path)]
    )
    assert process.returncode == 2
    assert not output_path.exists()


def test_defaults_write_output_report_and_rank_top_5(tmp_path):
    """Sem --output/--top: grava em output/report.json (criando o diretório) e ranqueia 5 hotéis."""
    input_path = write_reservations(
        tmp_path / "reservas.csv",
        [
            {"reservation_id": f"R-{index}", "hotel_id": f"H0{index}", "amount": f"{index}00.00"}
            for index in range(1, 7)
        ],
    )
    process = run_module(["--input", str(input_path), "--rates", str(RATES_FILE)], cwd=tmp_path)

    assert process.returncode == 0, process.stderr
    assert process.stdout == "Reservas: 6 | Confirmadas: 6 | Noites: 6 | Total BRL: 2100.00\n"
    report = json.loads((tmp_path / "output" / "report.json").read_text(encoding="utf-8"))
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H06", "H05", "H04", "H03", "H02"]


def test_report_schema_and_formats(tmp_path):
    """Chaves, ordem, tipos, versão, offset de generated_at e dinheiro sem separador de milhar."""
    report = run_cli(tmp_path, [{"amount": "1234.50"}])

    assert list(report) == ["report_version", "generated_at", "summary", "by_month", "top_hotels"]
    assert report["report_version"] == "1.0"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-03:00", report["generated_at"])
    assert report["summary"] == {
        "total_reservations": 1,
        "confirmed_reservations": 1,
        "cancelled_reservations": 0,
        "no_show_reservations": 0,
        "total_room_nights": 1,
        "total_amount_brl": "1234.50",
        "average_nightly_rate_brl": "1234.50",
    }
    assert list(report["summary"]) == [
        "total_reservations",
        "confirmed_reservations",
        "cancelled_reservations",
        "no_show_reservations",
        "total_room_nights",
        "total_amount_brl",
        "average_nightly_rate_brl",
    ]
    assert report["by_month"] == [{"month": "2025-01", "reservations": 1, "room_nights": 1, "total_brl": "1234.50"}]
    assert list(report["by_month"][0]) == ["month", "reservations", "room_nights", "total_brl"]
    assert report["top_hotels"] == [
        {"hotel_id": "H01", "hotel_name": "Hotel Teste", "room_nights": 1, "total_brl": "1234.50"}
    ]
    assert list(report["top_hotels"][0]) == ["hotel_id", "hotel_name", "room_nights", "total_brl"]
