"""Testes adicionais: leitura completa do arquivo de entrada."""

from helpers import run_cli


def test_all_reservations_in_file_are_processed(tmp_path):
    """total_reservations é o número de reservas no arquivo, sem teto de linhas."""
    total = 250
    report = run_cli(tmp_path, [{"reservation_id": f"R-{index}"} for index in range(1, total + 1)])

    summary = report["summary"]
    assert summary["total_reservations"] == total
    assert summary["confirmed_reservations"] == total
    assert summary["total_room_nights"] == total
    assert summary["total_amount_brl"] == "25000.00"
