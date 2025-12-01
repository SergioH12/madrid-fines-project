import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .cacheUrl import CacheUrl
import pandas as pd
from io import StringIO 
import numpy as np
import matplotlib.pyplot as plt
import locale

ROOT = 'https://datos.madrid.es'
MADRID_FINES_URL = "/sites/v/index.jsp?vgnextoid=fb9a498a6bdb9410VgnVCM1000000b205a0aRCRD&vgnextchannel=374512b9ace9f310VgnVCM100000171f5a0aRCRD"
locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")


def get_url(year:int, month:int) -> str:
    """Return the CSV URL for fines in Madrid for a given year and month

    Params:
        year (int): Year to retrieve (2017-2025)
        month (int): Month to retrieve (1-12)

    Returns:
        str: URL of the CSV file for the requested month

    Raises:
        MadridError: If year or month are out of range, if the main page cannot be retrieved,
                     or if no CSV is found for the specified year/month.

    Example:
        >>> try:
        ...     url = get_url(2024, 12) #doctest: +SKIP
        ...     url.startswith("https://datos.madrid.es/")
        ... except MadridError:
        ...     # Puede fallar si el sitio cambia o no hay conexión
        ...     True
        True
    """
    
    if not (2017 <= year <= 2025):
        raise MadridError(f"Año fuera de rango: {year}")
    if not (1 <= month <= 12):
        raise MadridError(f"Mes inválido: {month}")

    goal_date = datetime(year=year,month=month,day=1)
    try:
        resp = requests.get(ROOT + MADRID_FINES_URL)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise MadridError(f"No se pudo obtener la página principal: {e}")
    
    soup = BeautifulSoup(resp.text, "html.parser")

    for li in soup.select("li.asociada-item, li.asociada-item.hide"):
        p_fecha = li.find("p", class_="info-title")
        if not p_fecha:
            continue
        texto = p_fecha.get_text(strip=True)

        try:
            fecha = datetime.strptime(texto, "%Y %B")
        except ValueError:
            continue

        if fecha == goal_date:
            li_detalle = li.find("p", string="Detalle")
            if li_detalle and li_detalle.parent:
                link_tag = li_detalle.parent.find("a", class_="asociada-link ico-csv")
                if link_tag:
                    href = link_tag['href'] 
                    return ROOT + href
    raise MadridError(f"No se encontró CSV para {year}-{month:02d}")
             

    

class MadridFines:
    """Class to manage and analyze traffic fines in Madrid using cached CSV files

    Attributes:
        __cacheurl (CacheUrl): Cache for URLs
        __data (pd.DataFrame): Loaded fines data
        __loaded (list): List of loaded tuples (month, year)
    """
    def __init__(self,app_name:str, obsolecence:int) -> None:
        """Initialize MadridFines with cache

        Params:
            app_name (str): Name of the application for cache
            obsolecence (int): Maximum age for cache
        """
        self.__cacheurl = CacheUrl(app_name=app_name,obsolescence=obsolecence)
        self.__data = pd.DataFrame()   
        self.__loaded = []

    @property
    def loaded(self) -> list:
        """Return the list of tuples of loaded tuples (month,year)
        """
        return self.__loaded

    @staticmethod
    def load(year:int,month:int, cacheurl:CacheUrl) -> pd.DataFrame:
        """Load CSV data for a given year and month using the cache

        Args:
            year (int): Year to load
            month (int): Month to load
            cacheurl (CacheUrl): CacheUrl instance to fetch or store data

        Returns:
            pd.DataFrame: Loaded fines data

        Example (uso normal, puede requerir internet):
            >>> import pandas as pd
            >>> cacheurl = CacheUrl("test_app", 10)
            >>> try:
            ...     df = MadridFines.load(2024, 12, cacheurl)
            ...     isinstance(df, pd.DataFrame)
            ... except MadridError:
            ...     # Puede fallar si no hay internet o el portal cambia
            ...     True
            True
        """
        url = get_url(year=year,month=month)
        data = cacheurl.get(url)
        df = pd.read_csv(StringIO(data), sep=';', encoding='latin1') 
        return df
    
    @staticmethod
    def clean(df:pd.DataFrame) -> None:
        """Clean and normalize the fines DataFrame data and columns

        Processes columns: strips strings, converts string columns to numeric, 
        and computes a proper datetime column 'FECHA'.

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({"ANIO":[2025], "MES":[4], "HORA":[1230], "CALIFICACION":["A"], "DESCUENTO":["SI"], "HECHO_BOL":["X"], "DENUNCIANTE":["Y"], "VEL_LIMITE":[50], "VEL_CIRCULA":[60], "COORDENADA_X":["100"], "COORDENADA_Y":["200"]})
            >>> MadridFines.clean(df)
            >>> 'FECHA' in df.columns
            True
        """
        df.columns = df.columns.str.strip().str.replace('-', '_')

        df['CALIFICACION'] = df['CALIFICACION'].str.strip()
        df['DESCUENTO'] = df['DESCUENTO'].str.strip()
        df['HECHO_BOL'] = df['HECHO_BOL'].str.strip()
        df['DENUNCIANTE'] = df['DENUNCIANTE'].str.strip()
        df['VEL_LIMITE'] = pd.to_numeric(df['VEL_LIMITE'], errors='coerce')
        df['VEL_CIRCULA'] =  pd.to_numeric(df['VEL_CIRCULA'], errors = 'coerce')
        pd.to_numeric(df['COORDENADA_X'].str.strip())
        pd.to_numeric(df['COORDENADA_Y'].str.strip())
        df['COORDENADA_X'] = pd.to_numeric(df['COORDENADA_X'], errors='coerce')
        df['COORDENADA_Y'] =  pd.to_numeric(df['COORDENADA_Y'], errors = 'coerce')
        horas = df['HORA'].fillna(0).astype(int)   
        minutos = ((df['HORA'] - horas) * 100).astype(int) 

        df['FECHA'] = pd.to_datetime(
            pd.DataFrame({
                "year": df["ANIO"],
                "month": df["MES"],
                "day": 1,
                "hour": horas,
                "minute": minutos
            })
        )
        

    def add(self, year: int, month: int | None = None) -> None:
        """Add fines data for a specific year and month (or all months if month=None)

        Loads csv with CacheUrl, cleans the data, and appends it to fines DataFrame.

        Args:
            year (int): Year to add
            month (int | None): Month to add (1-12). If None, loads all months

        Raises:
            MadridError: If month is invalid.

        Example:
            >>> from madridFines.cacheUrl import CacheUrl
            >>> fines = MadridFines("test_app", 10)
            >>> cacheurl = CacheUrl("test_app", 10)
            >>> # Simula carga de datos
            >>> fines._MadridFines__data = pd.DataFrame({
            ...     "ANIO": [2025],
            ...     "MES": [4],
            ...     "HORA": [10],
            ...     "CALIFICACION": ["LEVE"],
            ...     "DESCUENTO": ["NO"],
            ...     "HECHO_BOL": ["H123"],
            ...     "DENUNCIANTE": ["AGENTE"],
            ...     "VEL_LIMITE": [50],
            ...     "VEL_CIRCULA": [70],
            ...     "COORDENADA_X": [12345],
            ...     "COORDENADA_Y": [67890],
            ...     "IMP_BOL": [100]
            ... })
            >>> fines.add(2025, 4)
            >>> isinstance(fines.loaded, list)
            True
        """
        if month is None:
            months = range(1, 13)
        elif 1 <= month <= 12:
            months = [month]
        else:
            raise MadridError(f"Mes inválido: {month}")

        for m in months:
            if (year, m) not in self.__loaded:
                df = self.load(year, m, self.__cacheurl)
                self.clean(df)
                self.__data = pd.concat([self.__data, df], ignore_index=True)
                self.__loaded.append((m,year))

    def fines_hour(self, fig_name:str) -> None:
        """Generate a line plot of fines per hour and save it as an image

        Params:
            fig_name (str): File path for the output figure (example, "fines.png").

        Example:
            >>> import os, pandas as pd
            >>> fines = MadridFines("test_app", 10)
            >>> fines._MadridFines__data = pd.DataFrame({
            ...     "ANIO": [2025, 2025, 2025],
            ...     "MES": [4, 4, 5],
            ...     "HORA": [10, 15, 20]
            ... })
            >>> fig_file = "test_plot.png"
            >>> fines.fines_hour(fig_file)
            >>> os.path.exists(fig_file)
            True
            >>> os.remove(fig_file)  # cleanup
        """
        graph_df = self.__data.copy()
        graph_df['ANIO-MES'] = graph_df['ANIO'].astype(str) + '-' + graph_df['MES'].astype(str).str.zfill(2)
        
        plt.figure(figsize=(12,6))

        for (year_month, group) in graph_df.groupby('ANIO-MES'):
            multas_int = group['HORA'].astype(int).value_counts().sort_index()
            plt.plot(multas_int.index, multas_int.values, label=f'{year_month}')

            plt.title("Sanciones por hora")
            plt.xlabel("Hora")
            plt.ylabel("Número de sanciones")

            plt.xticks(ticks=range(5, 25, 5))  
        plt.savefig(fig_name)  
        plt.close()
        
    def fines_calification(self) -> pd.DataFrame:
        """Return a table of fines counts grouped by month, year, and CALIFICACION.

        Returns:
            pd.DataFrame: Pivot table with counts

        Example:
            >>> import pandas as pd
            >>> fines = MadridFines("test_app", 10)
            >>> fines._MadridFines__data = pd.DataFrame({
            ...     "MES": [4, 4, 5],
            ...     "ANIO": [2025, 2025, 2025],
            ...     "CALIFICACION": ["A", "B", "A"]
            ... })
            >>> df = fines.fines_calification()
            >>> isinstance(df, pd.DataFrame)
            True
            >>> (4, 2025) in df.index or (5, 2025) in df.index
            True
            >>> all(c in df.columns for c in ["A", "B"])
            True
        """
        table_df = self.__data.groupby(['MES','ANIO','CALIFICACION']).size().unstack(fill_value=0)
        return table_df
    
    def total_payment(self) -> pd.DataFrame:
        """Calculate total payment per month and year, applying discounts

        Returns:
            pd.DataFrame: DataFrame with columns ['MES','ANIO','min_recaudo','max_recaudo'].

        Example (doctest-safe):
            >>> import pandas as pd
            >>> fines = MadridFines("test_app", 10)
            >>> fines._MadridFines__data = pd.DataFrame({
            ...     "MES": [4, 4, 5],
            ...     "ANIO": [2025, 2025, 2025],
            ...     "DESCUENTO": ["SI", "NO", "SI"],
            ...     "IMP_BOL": [100, 200, 300]
            ... })
            >>> df = fines.total_payment()
            >>> isinstance(df, pd.DataFrame)
            True
            >>> set(df.columns) == {"MES", "ANIO", "min_recaudo", "max_recaudo"}
            True
            >>> bool(df.loc[df["MES"] == 4, "min_recaudo"].iloc[0] == 50.0)
            True
            >>> bool(df.loc[df["MES"] == 4, "max_recaudo"].iloc[0] == 200.0)
            True
        """
        total_df = self.__data.copy()
        total_df['PRECIO_FINAL'] = np.where(
        total_df['DESCUENTO'] == 'SI',
        total_df['IMP_BOL'] * 0.5,
        total_df['IMP_BOL']
        )
        total_df = total_df.groupby(['MES','ANIO']).agg(
        min_recaudo = ('PRECIO_FINAL','min'),
        max_recaudo = ('PRECIO_FINAL', 'max'),
        ).reset_index()
        return total_df






class MadridError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

















