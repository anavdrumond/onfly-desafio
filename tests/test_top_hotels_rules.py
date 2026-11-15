"""Testes adicionais: regras do ranking de hotéis."""

from helpers import run_cli


def test_top_hotels_aggregate_only_confirmed(tmp_path):
    """Soma noites e valores por hotel; hotéis só com CANCELLED/NO_SHOW não entram."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "status": "CANCELLED", "amount": "5000.00"},
            {"reservation_id": "R-2", "hotel_id": "H02", "status": "NO_SHOW", "amount": "4000.00"},
            {"reservation_id": "R-3", "hotel_id": "H03", "hotel_name": "Hotel C", "amount": "100.00"},
            {
                "reservation_id": "R-4",
                "hotel_id": "H03",
                "hotel_name": "Hotel C",
                "currency": "EUR",
                "amount": "100.00",
                "checkin_date": "2025-01-20",
                "checkout_date": "2025-01-23",
            },
            {"reservation_id": "R-5", "hotel_id": "H03", "status": "CANCELLED", "amount": "999.00"},
            {"reservation_id": "R-6", "hotel_id": "H04", "hotel_name": "Hotel D", "amount": "50.00"},
        ],
    )
    assert report["top_hotels"] == [
        {"hotel_id": "H03", "hotel_name": "Hotel C", "room_nights": 4, "total_brl": "688.00"},
        {"hotel_id": "H04", "hotel_name": "Hotel D", "room_nights": 1, "total_brl": "50.00"},
    ]


def test_top_hotels_tie_breaks_by_hotel_id_ascending(tmp_path):
    """Empate em total_brl (mesmo valor exato, inclusive após câmbio) ordena por hotel_id ascendente."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H07", "amount": "542.00"},
            {"reservation_id": "R-2", "hotel_id": "H06", "currency": "USD", "amount": "100.00"},
            {"reservation_id": "R-3", "hotel_id": "H05", "amount": "542.00"},
            {"reservation_id": "R-4", "hotel_id": "H08", "amount": "1000.00"},
        ],
        top=3,
    )
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H08", "H05", "H06"]
    assert [hotel["total_brl"] for hotel in report["top_hotels"]] == ["1000.00", "542.00", "542.00"]
