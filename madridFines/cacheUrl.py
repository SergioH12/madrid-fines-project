from pathlib import Path
import requests
import hashlib
from .cache import Cache

class CacheUrl(Cache):
    """Cache storage for url that hashes url to store url content

    CacheUrl Inherits from cache, this class provides methods to check if the content exists, 
    load cached content and delete chached content

    """

    def __init__(self, app_name: str, obsolescence: int, cache_dir: Path = Path.home() / ".my_cache") -> None:
        super().__init__(app_name, obsolescence, cache_dir)

    
    def _hash(self, url: str) -> str:
        return hashlib.md5(url.encode("utf-8")).hexdigest()

    def get(self, url:str) -> str:
        """Return content from the cache if exists, otherwise download and store it

        Params:
            url (str): URL to fetch

        Returns:
            str: Content of the URL

        Raises:
            requests.RequestException: If the HTTP request fails
            CacheError: If storing or retrieving the cached file fails

        Example:
            >>> cache_url = CacheUrl("test_app", 10)
            >>> content = cache_url.get("https://datos.madrid.es/egob/catalogo/210104-403-multas-circulacion-detalle.csv") #depende de internet, preguntar
            >>> isinstance(content, str)
            True
        """
        url_hashed = self._hash(url)
        if super().exists(url_hashed):
            return super().load(url_hashed)
        else:
            response = requests.get(url)
            response.raise_for_status()
            super().set(url_hashed,response.text)
            return response.text
    
    def exists(self, url: str, **kwargs) -> bool:
        """Check if the cached content for the given URL exists

        Params:
            url (str): URL to check

        Returns:
            bool: True if the cached content exists, False otherwise

        Example:
            >>> cache_url = CacheUrl("test_app", 10)
            >>> fake_url = "http://example.com/data.csv"
            >>> hashed = hashlib.md5(fake_url.encode('utf-8')).hexdigest()
            >>> cache_url.set(hashed, "test content")
            >>> cache_url.exists(fake_url)
            True
            >>> cache_url.exists("http://example.com/no_exist.csv")
            False
        """
        url_hashed = self._hash(url)
        return super().exists(url_hashed)
    def load(self, url: str,**kwargs) -> str:
        """Load cached content for the given URL

        Params:
            url (str): URL to load

        Returns:
            str: Cached content

        Raises:
            CacheError: If the content is not cached

        Example:
            >>> cache_url = CacheUrl("test_app", 10)
            >>> fake_url = "http://example.com/data.csv"
            >>> hashed = hashlib.md5(fake_url.encode('utf-8')).hexdigest()
            >>> cache_url.set(hashed, "test content")
            >>> cache_url.load(fake_url)
            'test content'
        """
        url_hashed = self._hash(url)
        return super().load(url_hashed)
        
    def how_old(self, url: str) -> float:
        """Return the age in milliseconds of the cached content for the URL

        Params:
            url (str): URL to check

        Returns:
            float: Age in milliseconds

        Raises:
            CacheError: If the content is not cached

        Example:
            >>> import time
            >>> cache_url = CacheUrl("test_app", 10)
            >>> fake_url = "http://example.com/data.csv"
            >>> hashed = hashlib.md5(fake_url.encode('utf-8')).hexdigest()
            >>> cache_url.set(hashed, "test content")
            >>> age = cache_url.how_old(fake_url)
            >>> isinstance(age, float)
            True
            >>> age >= 0
            True
        """
        url_hashed = self._hash(url)
        return super().how_old(url_hashed)
    def delete(self, url: str) -> None:
        """Delete cached content for the given URL

        Params:
            url (str): URL to delete

        Raises:
            CacheError: If the content is not cached

        Example:
            >>> cache_url = CacheUrl("test_app", 10)
            >>> fake_url = "http://example.com/data.csv"
            >>> hashed = hashlib.md5(fake_url.encode('utf-8')).hexdigest()
            >>> cache_url.set(hashed, "test content")
            >>> cache_url.delete(fake_url)
            >>> cache_url.exists(fake_url)
            False
        """
        url_hashed = self._hash(url)
        return super().delete(url_hashed)

