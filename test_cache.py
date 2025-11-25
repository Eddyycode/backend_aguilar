#!/usr/bin/env python
"""
Test de configuración de Cache
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.cache import cache
from django.conf import settings
import time

def test_cache():
    print("\n" + "=" * 70)
    print(" " * 20 + "TEST DE CACHE DJANGO")
    print("=" * 70 + "\n")

    # Mostrar configuración
    print("📋 CONFIGURACIÓN DE CACHE:")
    print("-" * 70)
    cache_config = settings.CACHES['default']
    print(f"Backend: {cache_config['BACKEND']}")
    print(f"Location: {cache_config.get('LOCATION', 'N/A')}")
    print(f"Timeout: {cache_config.get('TIMEOUT', 'N/A')} segundos")
    print(f"Max Entries: {cache_config.get('OPTIONS', {}).get('MAX_ENTRIES', 'N/A')}")

    # Test 1: Set y Get básico
    print("\n🧪 TEST 1: Set y Get básico")
    print("-" * 70)
    cache.set('test_key', 'test_value', 60)
    value = cache.get('test_key')

    if value == 'test_value':
        print("✅ Cache Set/Get funciona correctamente")
        print(f"   Valor almacenado: '{value}'")
    else:
        print("❌ Cache Set/Get falló")

    # Test 2: Set con timeout
    print("\n🧪 TEST 2: Timeout de cache")
    print("-" * 70)
    cache.set('timeout_test', 'valor temporal', 2)  # 2 segundos
    value1 = cache.get('timeout_test')
    print(f"✓ Valor antes del timeout: '{value1}'")

    print("  Esperando 3 segundos...")
    time.sleep(3)

    value2 = cache.get('timeout_test')
    if value2 is None:
        print("✅ Timeout funciona correctamente (valor expirado)")
    else:
        print("❌ Timeout no funciona")

    # Test 3: Get con default
    print("\n🧪 TEST 3: Get con valor default")
    print("-" * 70)
    value = cache.get('nonexistent_key', 'default_value')
    if value == 'default_value':
        print("✅ Get con default funciona correctamente")
        print(f"   Valor default: '{value}'")
    else:
        print("❌ Get con default falló")

    # Test 4: Many operations
    print("\n🧪 TEST 4: Set/Get múltiples")
    print("-" * 70)
    data = {
        'vehiculo_1': {'placa': 'ABC-123', 'marca': 'Toyota'},
        'vehiculo_2': {'placa': 'DEF-456', 'marca': 'Honda'},
        'vehiculo_3': {'placa': 'GHI-789', 'marca': 'Ford'},
    }

    cache.set_many(data, 300)
    retrieved = cache.get_many(['vehiculo_1', 'vehiculo_2', 'vehiculo_3'])

    if len(retrieved) == 3:
        print(f"✅ Set/Get múltiples funciona correctamente")
        print(f"   Almacenados: {len(data)} elementos")
        print(f"   Recuperados: {len(retrieved)} elementos")
    else:
        print("❌ Set/Get múltiples falló")

    # Test 5: Delete
    print("\n🧪 TEST 5: Delete de cache")
    print("-" * 70)
    cache.set('delete_test', 'valor a eliminar', 300)
    cache.delete('delete_test')
    value = cache.get('delete_test')

    if value is None:
        print("✅ Delete funciona correctamente")
    else:
        print("❌ Delete falló")

    # Test 6: Increment/Decrement
    print("\n🧪 TEST 6: Increment/Decrement")
    print("-" * 70)
    try:
        cache.set('counter', 10, 300)
        cache.incr('counter', 5)
        value1 = cache.get('counter')

        cache.decr('counter', 3)
        value2 = cache.get('counter')

        if value1 == 15 and value2 == 12:
            print("✅ Increment/Decrement funciona correctamente")
            print(f"   Después de incr(5): {value1}")
            print(f"   Después de decr(3): {value2}")
        else:
            print("⚠️  Increment/Decrement tiene problemas")
    except Exception as e:
        print(f"⚠️  Increment/Decrement no soportado en este backend: {e}")

    # Test 7: Clear
    print("\n🧪 TEST 7: Clear cache")
    print("-" * 70)
    cache.set('clear_test_1', 'value1', 300)
    cache.set('clear_test_2', 'value2', 300)
    cache.clear()

    value1 = cache.get('clear_test_1')
    value2 = cache.get('clear_test_2')

    if value1 is None and value2 is None:
        print("✅ Clear funciona correctamente")
    else:
        print("❌ Clear falló")

    print("\n" + "=" * 70)
    print("✅ TESTS DE CACHE COMPLETADOS")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    test_cache()
