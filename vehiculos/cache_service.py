# vehiculos/cache_service.py
from django.core.cache import cache
from typing import Optional, Any, Callable
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """
    Servicio de caché para optimizar llamadas a APIs externas
    """
    
    # Tiempos de expiración en segundos
    CACHE_TIMEOUT_SHORT = 300      # 5 minutos
    CACHE_TIMEOUT_MEDIUM = 1800    # 30 minutos
    CACHE_TIMEOUT_LONG = 3600      # 1 hora
    CACHE_TIMEOUT_EXTRA_LONG = 86400  # 24 horas
    
    @staticmethod
    def _generate_key(prefix: str, **kwargs) -> str:
        """
        Genera una clave única para el caché basada en los parámetros
        """
        # Ordenar kwargs para consistencia
        sorted_kwargs = json.dumps(kwargs, sort_keys=True)
        hash_value = hashlib.md5(sorted_kwargs.encode()).hexdigest()
        return f"{prefix}:{hash_value}"
    
    @staticmethod
    def get_or_set(
        key_prefix: str,
        fetch_function: Callable,
        timeout: int = CACHE_TIMEOUT_MEDIUM,
        **kwargs
    ) -> Any:
        """
        Obtiene datos del caché o ejecuta la función si no existen
        
        Args:
            key_prefix: Prefijo para la clave del caché
            fetch_function: Función a ejecutar si no hay datos en caché
            timeout: Tiempo de expiración en segundos
            **kwargs: Argumentos para generar la clave y pasar a la función
        
        Returns:
            Datos del caché o resultado de fetch_function
        """
        cache_key = CacheService._generate_key(key_prefix, **kwargs)
        
        # Intentar obtener del caché
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT para {cache_key}")
            return cached_data
        
        # Si no está en caché, ejecutar la función
        logger.info(f"Cache MISS para {cache_key}, ejecutando función...")
        try:
            data = fetch_function(**kwargs)
            
            # Guardar en caché
            cache.set(cache_key, data, timeout)
            logger.info(f"Datos guardados en caché: {cache_key}")
            
            return data
        except Exception as e:
            logger.error(f"Error al ejecutar función para caché: {str(e)}")
            raise
    
    @staticmethod
    def invalidate(key_prefix: str, **kwargs):
        """
        Invalida (elimina) una entrada del caché
        """
        cache_key = CacheService._generate_key(key_prefix, **kwargs)
        cache.delete(cache_key)
        logger.info(f"Caché invalidado: {cache_key}")
    
    @staticmethod
    def invalidate_pattern(pattern: str):
        """
        Invalida todas las claves que coincidan con un patrón
        Nota: Requiere backend de caché que soporte delete_pattern (como Redis)
        """
        try:
            cache.delete_pattern(f"{pattern}:*")
            logger.info(f"Caché invalidado con patrón: {pattern}")
        except AttributeError:
            logger.warning("El backend de caché no soporta delete_pattern")


# Instancia global
cache_service = CacheService()