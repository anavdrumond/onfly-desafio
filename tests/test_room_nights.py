"""Testes adicionais: noites de quarto (virada de ano, ano bissexto e múltiplos quartos)."""

import pytest
from helpers import run_cli


@pytest.mark.parametrize(
    ("checkin", "checkout", "rooms", "expected"),
    [
        ("2024-12-30", "2025-01-02", "1", 3),
        ("2024-02-28", "2024-03-01", "1", 2),
        ("2025-02-28", "2025-03-01", "1", 1),
        ("2025-01-10", "2025-01-13", "3", 9),
    ],
    ids=["virada-de-ano", "fevereiro-bissexto", "fevereiro-comum", "multiplos-quartos"],
)
def test_room_nights_use_calendar_difference_times_rooms(tmp_path, checkin, checkout, rooms, expected):
    """room_nights = (checkout - checkin).days * rooms, não inclusivo."""
    report = run_cli(tmp_path, [{"checkin_date": checkin, "checkout_date": checkout, "rooms": rooms}])
    assert report["summary"]["total_room_nights"] == expected


def test_average_nightly_rate_divides_by_room_nights(tmp_path):
    """A média usa noites de quarto (noites x quartos), não noites de estadia."""
    report = run_cli(
        tmp_path,
        [{"checkin_date": "2025-01-10", "checkout_date": "2025-01-13", "rooms": "2", "amount": "900.00"}],
    )
    assert report["summary"]["total_room_nights"] == 6
    assert report["summary"]["average_nightly_rate_brl"] == "150.00"
