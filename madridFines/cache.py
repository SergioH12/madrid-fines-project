from pathlib import Path
import time

class CacheError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    
class Cache:
    """Cache class for storing string data in an app directory.

    Attributes:
        app_name (str): Name of the application
        obsolescence (int): Maximum age of cached files
        cache_dir (Path): Path to the cache directory

    Raises:
        CacheError: If obsolescence is negative.
    """
    def __init__(self, app_name:str, obsolescence: int, cache_dir:Path = Path.home() / ".my_cache") -> None:
        """Initialize the cache for a specific application

        Params:
            app_name (str): Application name
            obsolescence (int): Maximum file age
            cache_dir (Path): Base directory for cache. Default path is ~/.my_cache

        Raises:
            CacheError: If obsolescence is negative

        Example:
            >>> cache = Cache("test_app", 10)
            >>> isinstance(cache.cache_dir, Path)
            True
        """
        if obsolescence < 0:
            raise CacheError("La obsolescencia no puede ser negativa")
        self.__app_name = app_name
        self.__obsolescence = obsolescence
        self.__cache_dir = cache_dir / self.__app_name
        self.create_app_dir(self.cache_dir)

    #Getters
    @property
    def app_name(self):
        """Return cache aplication name
        """
        return self.__app_name
    @property
    def obsolescence(self):
        """Return maximum file age
        """
        return self.__obsolescence
    @property
    def cache_dir(self):
        """Return base cache directory
        """
        return self.__cache_dir

    def set(self, name:str, data:str) -> None:
        """Store string data in a file inside the cache with the specified name.

        Params:
            name (str): File name
            data (str): Content to store

        Example:
            >>> cache = Cache("test_app", 10)
            >>> cache.set("file.txt", "hello")
            >>> cache.exists("file.txt")
            True
        """
        file = self.__cache_dir / name
        with open(file, 'w') as f:
            f.write(data)
    
    def exists(self, name:str) -> bool:
        """Check if a file exists in the cache.

        Params:
            name (str): File name

        Returns:
            bool: True if the file exists, False otherwise

        Example:
            >>> cache = Cache("test_app", 10)
            >>> cache.set("file.txt", "data")
            >>> cache.exists("file.txt")
            True
        """
        path = self.__cache_dir / name
        return path.exists()
    
    def load(self, name:str) -> str:
        """Load data from a cache

        Params:
            name (str): File name

        Returns:
            str: File content

        Raises:
            CacheError: If file does not exist.

        Example:
            >>> cache = Cache("test_app", 10)
            >>> cache.set("file.txt", "hello")
            >>> cache.load("file.txt")
            'hello'
        """
        path = self.__cache_dir / name
        if path.exists():
            with open(path) as f:
                return f.read()
        else:
            raise CacheError(f"No existe el archivo '{name}' en cache.")

    def how_old(self, name:str) -> float:
        """Return the age of a cached file in milliseconds

        Params:
            name (str): File name

        Returns:
            float: Age in milliseconds

        Raises:
            CacheError: If file does not exist

        Example:
            >>> import time
            >>> cache = Cache("test_app", 10)
            >>> cache.set("file.txt", "data")
            >>> age = cache.how_old("file.txt")
            >>> isinstance(age, float)
            True
            >>> age >= 0
            True
        """
        path = self.__cache_dir / name
        if path.exists():
            #Parece que dependiendo del sistema operativo, esta operacion lanzar AttributeError
            try:
                created_time =path.stat().st_birthtime
            except AttributeError:
                created_time = path.stat().st_mtime
            age = time.time() - created_time
            return age * 1000
        else:
            raise CacheError(f"No existe el archivo '{name}' en cache.")
        

    def delete(self, name:str) -> None:
        """Delete the file with the specified name

        Params:
            name (str): File name

        Raises:
            CacheError: If file does not exist
        Example:
            >>> cache = Cache("test_app", 10)
            >>> cache.set("file.txt", "data")
            >>> cache.exists("file.txt")
            True
            >>> cache.delete("file.txt")
            >>> cache.exists("file.txt")
            False
        """
        path = self.__cache_dir / name
        if path.exists():
            path = self.__cache_dir / name
            path.unlink()
        else: 
            raise CacheError

    def clear(self) -> None:
        """Delete all files in the cache directory.
        Raises:
            OSError: If a file cannot be deleted.
        
        Example:
            >>> cache = Cache("test_app", 10)
            >>> cache.set("file.txt", "data")
            >>> cache.clear()
            >>> cache.exists("file.txt")
            False
        """
        for f in self.__cache_dir.iterdir():
            f.unlink()

    @staticmethod
    def create_app_dir(cache_dir:Path) -> None:
        """Create cache app directory

        Params:
            cache_dir(Path): cache directory path
        Example:
            >>> from pathlib import Path
            >>> cache_dir = Path.home() / ".my_cache" / "app_test"
            >>> Cache.create_app_dir(cache_dir)
        
        """
        path = cache_dir
        path.mkdir(parents=True, exist_ok=True)