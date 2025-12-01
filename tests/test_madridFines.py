from madridFines.madridFines import MadridFines, get_url, MadridError
import pytest
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
import requests


@pytest.fixture
def csv_data(datafiles):
    csv_file = Path(datafiles) / "multas_sample.csv"
    return csv_file.read_text(encoding="latin1")

#test de get_url
@pytest.mark.datafiles("tests/data/test_page.html")
def test_get_url(datafiles):
    html_file = Path(datafiles) / "test_page.html"
    html_simulado = html_file.read_text(encoding="utf-8")

    mock_response = Mock()
    mock_response.text = html_simulado
    mock_response.raise_for_status = Mock()

    with patch("madridFines.madridFines.requests.get", return_value=mock_response):
        url = get_url(2025, 4)

    assert url == "https://datos.madrid.es/egob/catalogo/210104-403-multas-circulacion-detalle.csv"

def test_get_url_year_out_of_range():
    with pytest.raises(MadridError, match="Año fuera de rango:"):
        get_url(2026, 5)

def test_get_url_invalid_month():
    with pytest.raises(MadridError, match="Mes inválido:"):
        get_url(2024, 13)


def test_get_url_request_exception():
    with patch("madridFines.madridFines.requests.get", side_effect=requests.RequestException("Fallo")):
        with pytest.raises(MadridError, match="No se pudo obtener la página principal:"):
            get_url(2024, 5)

def test_get_url_no_csv_found():
    mock_response = Mock()
    mock_response.text = ""
    mock_response.raise_for_status = Mock()

    with patch("madridFines.madridFines.requests.get", return_value=mock_response):
        with pytest.raises(MadridError, match="No se encontró CSV para"):
            get_url(2024, 4)

#test MadridFines

@pytest.fixture
def madrid():
    return MadridFines("test_app", 10)

@pytest.mark.datafiles("tests/data/multas_sample.csv")
def test_add_single_month(madrid, csv_data):
    with patch("madridFines.madridFines.get_url", return_value="fake_url"):
        madrid._MadridFines__cacheurl.get = MagicMock(return_value=csv_data)
        madrid.add(2025, 4)

    assert not madrid._MadridFines__data.empty
    assert madrid.loaded == [(4, 2025)]
    madrid._MadridFines__cacheurl.get.assert_called_once_with("fake_url")

@pytest.mark.datafiles("tests/data/multas_sample.csv")
def test_add_full_year(madrid, csv_data):
    with patch("madridFines.madridFines.get_url", return_value="fake_url"):
        madrid._MadridFines__cacheurl.get = MagicMock(return_value=csv_data)
        madrid.add(2025)  
    
    assert len(madrid.loaded) == 12
    months = [m for m, y in madrid.loaded]
    assert months == list(range(1,13))

def test_add_invalid_month(madrid):
    with pytest.raises(MadridError, match="Mes inválido:"):
        madrid.add(2024, 13)

@pytest.mark.datafiles("tests/data/multas_sample.csv")
def test_fines_calification(madrid, csv_data):
    with patch("madridFines.madridFines.get_url", return_value="fake_url"):
        madrid._MadridFines__cacheurl.get = MagicMock(return_value=csv_data)
        madrid.add(2025, 4)
    
    df_calif = madrid.fines_calification()
    assert "LEVE" in df_calif.columns
    assert "GRAVE" in df_calif.columns
    assert df_calif.sum().sum() == 211864

@pytest.mark.datafiles("tests/data/multas_sample.csv")
def test_total_payment(madrid, csv_data):
    with patch("madridFines.madridFines.get_url", return_value="fake_url"):
        madrid._MadridFines__cacheurl.get = MagicMock(return_value=csv_data)
        madrid.add(2025, 4)
    
    df_total = madrid.total_payment()
    assert "min_recaudo" in df_total.columns
    assert "max_recaudo" in df_total.columns
    min_expected = 15 
    max_expected = 500 
    assert df_total["min_recaudo"].iloc[0] == min_expected
    assert df_total["max_recaudo"].iloc[0] == max_expected

@pytest.mark.datafiles("tests/data/multas_sample.csv")
def test_fines_hour(madrid, csv_data, tmp_path):
    with patch("madridFines.madridFines.get_url", return_value="fake_url"):
        madrid._MadridFines__cacheurl.get = MagicMock(return_value=csv_data)
        madrid.add(2025, 4)
    
    fig_path = tmp_path / "fig.png"
    madrid.fines_hour(str(fig_path))
    assert fig_path.exists()
