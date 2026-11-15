"""Testes adicionais: exatidão monetária (Decimal, half-up e arredondamento só na serialização)."""

from helpers import run_cli


def test_money_rounds_half_up(tmp_path):
    """100.75 USD x 5.42 = 546.065 exatos; half-up dá 546.07 (half-even ou float dariam 546.06)."""
    report = run_cli(tmp_path, [{"currency": "USD", "amount": "100.75"}])
    assert report["summary"]["total_amount_brl"] == "546.07"
    assert report["summary"]["average_nightly_rate_brl"] == "546.07"
    assert report["top_hotels"][0]["total_brl"] == "546.07"
    assert report["by_month"][0]["total_brl"] == "546.07"


def test_amounts_are_summed_exactly_and_rounded_only_on_output(tmp_path):
    """Dois valores de 546.065 somam 1092.13; arredondar antes de somar daria 1092.14."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "currency": "USD", "amount": "100.75"},
            {"reservation_id": "R-2", "hotel_id": "H02", "currency": "USD", "amount": "100.75"},
        ],
    )
    assert report["summary"]["total_amount_brl"] == "1092.13"
    assert report["by_month"][0]["total_brl"] == "1092.13"
    assert report["summary"]["average_nightly_rate_brl"] == "546.07"
    assert [hotel["total_brl"] for hotel in report["top_hotels"]] == ["546.07", "546.07"]


def test_eur_is_converted_with_its_rate(tmp_path):
    """EUR usa a própria taxa (5.88)."""
    report = run_cli(tmp_path, [{"currency": "EUR", "amount": "100.00"}])
    assert report["summary"]["total_amount_brl"] == "588.00"
