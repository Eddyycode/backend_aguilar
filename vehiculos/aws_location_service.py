# vehiculos/aws_location_service.py
import boto3
from decimal import Decimal
from decouple import config
from typing import List, Dict, Tuple, Optional

import logging

logger = logging.getLogger(__name__)


class AWSLocationService:

    
    def __init__(self):
       
        self.client = boto3.client(
            'location',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=config('AWS_REGION', default='us-east-1')
        )
        
        self.place_index = config('AWS_LOCATION_PLACE_INDEX', default='vehiculos-place-index')
        self.map_name = config('AWS_LOCATION_MAP', default='vehiculos-map')
        self.route_calculator = config('AWS_LOCATION_ROUTE_CALCULATOR', default='vehiculos-route-calculator')
    
    def buscar_lugares(
        self, 
        texto: str, 
        latitud: Optional[float] = None,
        longitud: Optional[float] = None,
        max_resultados: int = 10,
        pais: str = 'MEX',
        use_cache: bool = True 
    ) -> List[Dict]:
        """
        Busca lugares (POI) usando texto libre con caché
        """
        if not use_cache:
            # Si no usar caché, ejecutar directamente
            return self._buscar_lugares_sin_cache(
                texto, latitud, longitud, max_resultados, pais
            )
        
        # Usar caché
        return cache_service.get_or_set(
            key_prefix='aws_lugares',
            fetch_function=self._buscar_lugares_sin_cache,
            timeout=CacheService.CACHE_TIMEOUT_LONG,
            texto=texto,
            latitud=latitud,
            longitud=longitud,
            max_resultados=max_resultados,
            pais=pais
        )
    
    def _buscar_lugares_sin_cache(
        self,
        texto: str,
        latitud: Optional[float] = None,
        longitud: Optional[float] = None,
        max_resultados: int = 10,
        pais: str = 'MEX'
    ) -> List[Dict]:
        """
        Método interno para buscar lugares sin caché
        """
        try:
            parametros = {
                'IndexName': self.place_index,
                'Text': texto,
                'MaxResults': max_resultados,
                'FilterCountries': [pais]
            }
            
            if latitud is not None and longitud is not None:
                parametros['BiasPosition'] = [longitud, latitud]
            
            respuesta = self.client.search_place_index_for_text(**parametros)
            
            lugares = []
            for resultado in respuesta.get('Results', []):
                place = resultado.get('Place', {})
                geometria = place.get('Geometry', {})
                punto = geometria.get('Point', [])
                
                lugar = {
                    'nombre': place.get('Label', ''),
                    'direccion': place.get('Label', ''),
                    'latitud': Decimal(str(punto[1])) if len(punto) > 1 else None,
                    'longitud': Decimal(str(punto[0])) if len(punto) > 0 else None,
                    'pais': place.get('Country', ''),
                    'municipio': place.get('Municipality', ''),
                    'codigo_postal': place.get('PostalCode', ''),
                    'relevancia': resultado.get('Relevance', 0),
                }
                
                if 'Categories' in place:
                    lugar['categorias'] = place['Categories']
                
                lugares.append(lugar)
            
            logger.info(f"Búsqueda exitosa: {len(lugares)} lugares encontrados")
            return lugares
        
        except Exception as e:
            logger.error(f"Error al buscar lugares: {str(e)}")
            return []
    
    def geocodificar_direccion(
        self,
        direccion: str,
        pais: str = 'MEX',
        use_cache: bool = True
    ) -> Optional[Dict]:
        """
        Geocodifica una dirección con caché
        """
        if not use_cache:
            return self._geocodificar_sin_cache(direccion, pais)
        
        return cache_service.get_or_set(
            key_prefix='aws_geocode',
            fetch_function=self._geocodificar_sin_cache,
            timeout=CacheService.CACHE_TIMEOUT_EXTRA_LONG,  # 24 horas
            direccion=direccion,
            pais=pais
        )
    
    def _geocodificar_sin_cache(
        self,
        direccion: str,
        pais: str = 'MEX'
    ) -> Optional[Dict]:
        """
        Método interno para geocodificar sin caché
        """
        try:
            respuesta = self.client.search_place_index_for_text(
                IndexName=self.place_index,
                Text=direccion,
                MaxResults=1,
                FilterCountries=[pais]
            )
            
            if respuesta.get('Results'):
                resultado = respuesta['Results'][0]
                place = resultado.get('Place', {})
                punto = place.get('Geometry', {}).get('Point', [])
                
                return {
                    'latitud': Decimal(str(punto[1])) if len(punto) > 1 else None,
                    'longitud': Decimal(str(punto[0])) if len(punto) > 0 else None,
                    'direccion_formateada': place.get('Label', ''),
                    'municipio': place.get('Municipality', ''),
                    'estado': place.get('Region', ''),
                    'pais': place.get('Country', ''),
                    'codigo_postal': place.get('PostalCode', ''),
                    'relevancia': resultado.get('Relevance', 0)
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error al geocodificar: {str(e)}")
            return None
        try:
            parametros = {
                'IndexName': self.place_index,
                'Text': texto,
                'MaxResults': max_resultados,
                'FilterCountries': [pais]
            }
            
            # Si se proporcionan coordenadas, usarlas como sesgo de búsqueda
            if latitud is not None and longitud is not None:
                parametros['BiasPosition'] = [longitud, latitud]  # AWS usa [lon, lat]
            
            respuesta = self.client.search_place_index_for_text(**parametros)
            
            lugares = []
            for resultado in respuesta.get('Results', []):
                place = resultado.get('Place', {})
                
                # Extraer coordenadas (AWS devuelve [lon, lat])
                geometria = place.get('Geometry', {})
                punto = geometria.get('Point', [])
                
                lugar = {
                    'nombre': place.get('Label', ''),
                    'direccion': place.get('Label', ''),
                    'latitud': Decimal(str(punto[1])) if len(punto) > 1 else None,
                    'longitud': Decimal(str(punto[0])) if len(punto) > 0 else None,
                    'pais': place.get('Country', ''),
                    'municipio': place.get('Municipality', ''),
                    'codigo_postal': place.get('PostalCode', ''),
                    'relevancia': resultado.get('Relevance', 0),
                }
                
                # Información adicional si está disponible
                if 'Categories' in place:
                    lugar['categorias'] = place['Categories']
                
                lugares.append(lugar)
            
            logger.info(f"Búsqueda exitosa: {len(lugares)} lugares encontrados para '{texto}'")
            return lugares
        
        except Exception as e:
            logger.error(f"Error al buscar lugares: {str(e)}")
            return []
    
    def buscar_talleres_cercanos(
        self,
        latitud: float,
        longitud: float,
        radio_km: float = 10,
        max_resultados: int = 20
    ) -> List[Dict]:
        """
        Busca talleres mecánicos cercanos a una ubicación
        
        Args:
            latitud: Latitud de la ubicación actual
            longitud: Longitud de la ubicación actual
            radio_km: Radio de búsqueda en kilómetros (default: 10)
            max_resultados: Número máximo de resultados
        
        Returns:
            Lista de talleres encontrados
        """
        # Términos de búsqueda comunes para talleres
        terminos_busqueda = [
            "taller mecánico",
            "taller automotriz",
            "mecánico",
            "servicio automotriz"
        ]
        
        talleres = []
        talleres_unicos = set()
        
        for termino in terminos_busqueda:
            resultados = self.buscar_lugares(
                texto=termino,
                latitud=latitud,
                longitud=longitud,
                max_resultados=max_resultados
            )
            
            for lugar in resultados:
                # Usar coordenadas como identificador único
                identificador = (lugar.get('latitud'), lugar.get('longitud'))
                
                if identificador not in talleres_unicos:
                    talleres_unicos.add(identificador)
                    lugar['tipo_busqueda'] = termino
                    talleres.append(lugar)
            
            if len(talleres) >= max_resultados:
                break
        
        return talleres[:max_resultados]
    
    def geocodificar_direccion(
        self,
        direccion: str,
        pais: str = 'MEX'
    ) -> Optional[Dict]:
        """
        Convierte una dirección de texto en coordenadas geográficas
        
        Args:
            direccion: Dirección completa (ej: "Av. Universidad 2000, Villahermosa, Tabasco")
            pais: Código ISO del país
        
        Returns:
            Diccionario con coordenadas y detalles del lugar, o None si no se encuentra
        
        Ejemplo:
            >>> service = AWSLocationService()
            >>> coords = service.geocodificar_direccion(
            ...     "Av. Universidad 2000, Villahermosa, Tabasco"
            ... )
            >>> print(coords['latitud'], coords['longitud'])
        """
        try:
            respuesta = self.client.search_place_index_for_text(
                IndexName=self.place_index,
                Text=direccion,
                MaxResults=1,
                FilterCountries=[pais]
            )
            
            if respuesta.get('Results'):
                resultado = respuesta['Results'][0]
                place = resultado.get('Place', {})
                punto = place.get('Geometry', {}).get('Point', [])
                
                return {
                    'latitud': Decimal(str(punto[1])) if len(punto) > 1 else None,
                    'longitud': Decimal(str(punto[0])) if len(punto) > 0 else None,
                    'direccion_formateada': place.get('Label', ''),
                    'municipio': place.get('Municipality', ''),
                    'estado': place.get('Region', ''),
                    'pais': place.get('Country', ''),
                    'codigo_postal': place.get('PostalCode', ''),
                    'relevancia': resultado.get('Relevance', 0)
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error al geocodificar dirección: {str(e)}")
            return None
    
    def geocodificar_inverso(
        self,
        latitud: float,
        longitud: float
    ) -> Optional[Dict]:
        """
        Convierte coordenadas geográficas en una dirección de texto
        (Reverse Geocoding)
        
        Args:
            latitud: Latitud
            longitud: Longitud
        
        Returns:
            Diccionario con la dirección y detalles, o None si no se encuentra
        """
        try:
            respuesta = self.client.search_place_index_for_position(
                IndexName=self.place_index,
                Position=[longitud, latitud],  # AWS usa [lon, lat]
                MaxResults=1
            )
            
            if respuesta.get('Results'):
                resultado = respuesta['Results'][0]
                place = resultado.get('Place', {})
                
                return {
                    'direccion': place.get('Label', ''),
                    'calle': place.get('Street', ''),
                    'numero': place.get('AddressNumber', ''),
                    'municipio': place.get('Municipality', ''),
                    'estado': place.get('Region', ''),
                    'pais': place.get('Country', ''),
                    'codigo_postal': place.get('PostalCode', ''),
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error en geocodificación inversa: {str(e)}")
            return None
    
    def buscar_refaccionarias(
        self,
        latitud: float,
        longitud: float,
        radio_km: float = 5,
        max_resultados: int = 10
    ) -> List[Dict]:
        """
        Busca refaccionarias cercanas

        Args:
            latitud: Latitud de la ubicación
            longitud: Longitud de la ubicación
            radio_km: Radio de búsqueda
            max_resultados: Número máximo de resultados

        Returns:
            Lista de refaccionarias encontradas
        """
        terminos = ["refaccionaria", "autopartes", "refacciones automotrices"]

        lugares = []
        lugares_unicos = set()

        for termino in terminos:
            resultados = self.buscar_lugares(
                texto=termino,
                latitud=latitud,
                longitud=longitud,
                max_resultados=max_resultados
            )

            for lugar in resultados:
                identificador = (lugar.get('latitud'), lugar.get('longitud'))

                if identificador not in lugares_unicos:
                    lugares_unicos.add(identificador)
                    lugares.append(lugar)

        return lugares[:max_resultados]

    def calcular_ruta(
        self,
        origen_lat: float,
        origen_lon: float,
        destino_lat: float,
        destino_lon: float,
        modo_viaje: str = 'Car',
        optimizar_para: str = 'FastestRoute'
    ) -> Optional[Dict]:
        """
        Calcula una ruta entre dos puntos usando AWS Location Service

        Args:
            origen_lat: Latitud del punto de origen
            origen_lon: Longitud del punto de origen
            destino_lat: Latitud del punto de destino
            destino_lon: Longitud del punto de destino
            modo_viaje: Modo de viaje ('Car', 'Truck', 'Walking')
            optimizar_para: Optimización ('FastestRoute' o 'ShortestRoute')

        Returns:
            Diccionario con la información de la ruta o None si hay error
        """
        try:
            respuesta = self.client.calculate_route(
                CalculatorName=self.route_calculator,
                DeparturePosition=[origen_lon, origen_lat],  # AWS usa [lon, lat]
                DestinationPosition=[destino_lon, destino_lat],
                TravelMode=modo_viaje,
                OptimizeFor=optimizar_para,
                IncludeLegGeometry=True
            )

            if 'Legs' in respuesta and len(respuesta['Legs']) > 0:
                leg = respuesta['Legs'][0]

                # Extraer coordenadas de la geometría
                geometry = leg.get('Geometry', {})
                line_string = geometry.get('LineString', [])

                # Convertir coordenadas de [lon, lat] a [lat, lon]
                coordenadas = [[punto[1], punto[0]] for punto in line_string]

                # Calcular información de la ruta
                distancia_metros = leg.get('Distance', 0)
                duracion_segundos = leg.get('DurationSeconds', 0)

                return {
                    'distancia_km': round(distancia_metros / 1000, 2),
                    'duracion_minutos': round(duracion_segundos / 60, 1),
                    'coordenadas': coordenadas,
                    'steps': leg.get('Steps', []),
                    'origen': {
                        'latitud': origen_lat,
                        'longitud': origen_lon
                    },
                    'destino': {
                        'latitud': destino_lat,
                        'longitud': destino_lon
                    }
                }

            return None

        except Exception as e:
            logger.error(f"Error al calcular ruta: {str(e)}")
            return None
    
    def obtener_url_mapa_estatico(
        self,
        latitud: float,
        longitud: float,
        zoom: int = 15,
        ancho: int = 600,
        alto: int = 400
    ) -> str:
        """
        Genera una URL para obtener un mapa estático de AWS Location Service
        
        Args:
            latitud: Latitud del centro del mapa
            longitud: Longitud del centro del mapa
            zoom: Nivel de zoom (1-20)
            ancho: Ancho de la imagen en píxeles
            alto: Alto de la imagen en píxeles
        
        Returns:
            URL del mapa estático
        
        Nota: Esto requiere configuración adicional de API Gateway
        """
        region = config('AWS_REGION', default='us-east-1')
        
        # Esta es una URL de ejemplo. En producción necesitarías:
        # 1. Configurar Amazon API Gateway
        # 2. Crear un endpoint que llame a GetMapTile
        # 3. Firmar las requests con SigV4
        
        return (
            f"https://maps.geo.{region}.amazonaws.com/maps/v0/maps/{self.map_name}/"
            f"tiles/{{z}}/{{x}}/{{y}}?key={{apikey}}"
        )
    
    def validar_configuracion(self) -> Dict[str, bool]:
        """
        Valida que la configuración de AWS esté correcta
        
        Returns:
            Diccionario con el estado de cada recurso
        """
        estado = {
            'place_index_existe': False,
            'map_existe': False,
            'credenciales_validas': False
        }
        
        try:
            # Verificar Place Index
            self.client.describe_place_index(IndexName=self.place_index)
            estado['place_index_existe'] = True
        except Exception as e:
            logger.error(f"Place Index no encontrado: {str(e)}")
        
        try:
            # Verificar Map
            self.client.describe_map(MapName=self.map_name)
            estado['map_existe'] = True
        except Exception as e:
            logger.error(f"Map no encontrado: {str(e)}")
        
        # Si alguno existe, las credenciales son válidas
        estado['credenciales_validas'] = (
            estado['place_index_existe'] or 
            estado['map_existe']
        )
        
        return estado


# Instancia global del servicio (Singleton)
aws_location_service = AWSLocationService()