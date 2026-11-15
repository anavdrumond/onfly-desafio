"""Testes adicionais: relatório sem reservas faturáveis."""

import pytest
from helpers import run_cli

EMPTY_TOTALS = {
    "total_room_nights": 0,
    "total_amount_brl": "0.00",
    "average_nightly_rate_brl": "0.00",
}


@pytest.mark.parametrize(
    ("rows", "counts"),
    [
        ([], (0, 0, 0, 0)),
        (
            [
                {"reservation_id": "R-1", "status": "CANCELLED"},
                {"reservation_id": "R-2", "status": "NO_SHOW"},
            ],
            (2, 0, 1, 1),
        ),
    ],
    ids=["arquivo-so-com-cabecalho", "sem-confirmed"],
)
def test_report_without_billable_reservations_has_zero_totals(tmp_path, rows, counts):
    """Sem noites, a média é "0.00" e as agregações ficam vazias."""
    report = run_cli(tmp_path, rows)
    total, confirmed, cancelled, no_show = counts
    assert report["summary"] == {
        "total_reservations": total,
        "confirmed_reservations": confirmed,
        "cancelled_reservations": cancelled,
        "no_show_reservations": no_show,
        **EMPTY_TOTALS,
    }
    assert report["by_month"] == []
    assert report["top_hotels"] == []
