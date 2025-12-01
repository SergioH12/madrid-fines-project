from madridFines.cache import Cache
from madridFines.cacheUrl import CacheUrl
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import hashlib

#test de CacheURL

@pytest.fixture
def cache_url():
    return CacheUrl("test_app", 10, cache_dir=Path("/tmp/cache"))

def test_get_exists(cache_url):
    url = "http://example.com/data.csv"
    hashed = hashlib.md5(url.encode('utf-8')).hexdigest()

    # Mock de exists y load
    cache_url.exists = MagicMock(return_value=True)
    cache_url.load = MagicMock(return_value="contenido existente")

    result = cache_url.get(url)
    assert result == "contenido existente"
    cache_url.exists.assert_called_once_with(hashed)
    cache_url.load.assert_called_once_with(hashed)

def test_get_new(cache_url):
    url = "http://example.com/data.csv"
    hashed = hashlib.md5(url.encode('utf-8')).hexdigest()
    
    cache_url.exists = MagicMock(return_value=False)
    cache_url.set = MagicMock()
    
    mock_response = MagicMock()
    mock_response.text = "contenido nuevo"
    mock_response.raise_for_status = MagicMock()
    
    with patch("requests.get", return_value=mock_response) as mock_get:
        result = cache_url.get(url)
    
    assert result == "contenido nuevo"
    mock_get.assert_called_once_with(url)
    mock_response.raise_for_status.assert_called_once()
    cache_url.set.assert_called_once_with(hashed, "contenido nuevo")

def test_exists_hash(cache_url):
    url = "http://example.com/data.csv"
    hashed = hashlib.md5(url.encode('utf-8')).hexdigest()
    
    with patch.object(Cache, "exists", return_value=True) as mock:
        assert cache_url.exists(url) == True
        mock.assert_called_once_with(hashed)

def test_load_hash(cache_url):
    url = "http://example.com/data.csv"
    hashed = hashlib.md5(url.encode('utf-8')).hexdigest()
    
    with patch.object(Cache, "load", return_value="contenido") as mock:
        assert cache_url.load(url) == "contenido"
        mock.assert_called_once_with(hashed)

def test_delete_hash(cache_url):
    url = "http://example.com/data.csv"
    hashed = hashlib.md5(url.encode('utf-8')).hexdigest()
    
    with patch.object(Cache, "delete") as mock:
        cache_url.delete(url)
        mock.assert_called_once_with(hashed)

def test_how_old_hash(cache_url):
    url = "http://example.com/data.csv"
    hashed = hashlib.md5(url.encode('utf-8')).hexdigest()
    
    with patch.object(Cache, "how_old", return_value=12345) as mock:
        result = cache_url.how_old(url)
        assert result == 12345
        mock.assert_called_once_with(hashed)



