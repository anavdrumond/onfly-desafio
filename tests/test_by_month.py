"""Testes adicionais: agregação mensal."""

from helpers import run_cli


def test_by_month_groups_confirmed_by_checkin_month_in_ascending_order(tmp_path):
    """Mês do check-in, só CONFIRMED, ordem ascendente inclusive entre anos."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "checkin_date": "2025-03-05", "checkout_date": "2025-03-07", "amount": "200.00"},
            {
                "reservation_id": "R-2",
                "checkin_date": "2025-01-30",
                "checkout_date": "2025-02-02",
                "rooms": "2",
                "amount": "600.00",
            },
            {
                "reservation_id": "R-3",
                "checkin_date": "2024-12-31",
                "checkout_date": "2025-01-01",
                "currency": "USD",
                "amount": "100.00",
            },
            {
                "reservation_id": "R-4",
                "status": "CANCELLED",
                "checkin_date": "2025-02-10",
                "checkout_date": "2025-02-12",
                "amount": "300.00",
            },
            {
                "reservation_id": "R-5",
                "status": "NO_SHOW",
                "checkin_date": "2025-01-10",
                "checkout_date": "2025-01-11",
                "amount": "400.00",
            },
            {"reservation_id": "R-6", "checkin_date": "2025-01-15", "checkout_date": "2025-01-16", "amount": "100.00"},
        ],
    )
    assert report["by_month"] == [
        {"month": "2024-12", "reservations": 1, "room_nights": 1, "total_brl": "542.00"},
        {"month": "2025-01", "reservations": 2, "room_nights": 7, "total_brl": "700.00"},
        {"month": "2025-03", "reservations": 1, "room_nights": 2, "total_brl": "200.00"},
    ]
