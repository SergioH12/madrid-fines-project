from madridFines.cache import Cache, CacheError
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock



#test de Cache
@pytest.mark.parametrize( "app_name, obsolescence, cache_dir", [
    ("madrid_file", 3, None),   
    ("barcelona_file", 5, Path("/tmp/cache")),
])
def test_cache_creation(app_name, obsolescence, cache_dir):
    if cache_dir is None:
        c = Cache(app_name, obsolescence)
        expected_dir = Path.home() / ".my_cache" / app_name
    else:
        c = Cache(app_name, obsolescence, cache_dir)
        expected_dir = cache_dir / app_name
    
    assert c.app_name == app_name
    assert c.obsolescence == obsolescence
    assert c.cache_dir == expected_dir
    assert c.cache_dir.exists()

@pytest.mark.parametrize(
    "app_name, obsolescence", [
        ("madrid_file", -1),
        ("barcelona_file", -5),
    ])
def test_cache_creation_except(app_name, obsolescence):
    with pytest.raises(CacheError):
        Cache(app_name, obsolescence)



def test_cache_set_and_load(tmp_path):
    c = Cache("testapp", 3, cache_dir=tmp_path)
    c.set("test.txt", "contenido de prueba")
    assert c.exists("test.txt")
    contenido = c.load("test.txt")
    assert contenido == "contenido de prueba"

def test_cache_load_nonexistent(tmp_path):
    c = Cache("testapp", 3, cache_dir=tmp_path)
    with pytest.raises(CacheError):
        c.load("no_existe.txt")


def test_cache_delete_and_clear(tmp_path):
    c = Cache("testapp", 3, cache_dir=tmp_path)
    c.set("a.txt", "1")
    c.set("b.txt", "2")

    c.delete("a.txt")
    assert not c.exists("a.txt")
    assert c.exists("b.txt")

    c.clear()
    assert not any(f.exists() for f in c.cache_dir.iterdir())



def test_cache_how_old(tmp_path):
    c = Cache("test_app", 10, cache_dir=tmp_path)

    # mock exists() para forzar que crea que el archivo existe
    c.exists = MagicMock(return_value=True)

    mock_stat = MagicMock()
    mock_stat.st_birthtime = 1000

    with patch("pathlib.Path.stat", return_value=mock_stat):
        with patch("time.time", return_value=5000):
            age_ms = c.how_old("archivo.txt")
            assert age_ms == (5000 - 1000) * 1000

            
def test_cache_how_old_cache_error(tmp_path):
    c = Cache("test_app", 10, cache_dir=tmp_path)
    c.exists = MagicMock(return_value=False)

    with pytest.raises(CacheError):
        c.how_old("archivo.txt")
