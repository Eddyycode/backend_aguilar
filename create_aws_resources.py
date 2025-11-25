#!/usr/bin/env python
"""
Crea los recursos necesarios de AWS Location Service
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import boto3
from decouple import config
from botocore.exceptions import ClientError

def create_place_index(client, index_name):
    """Crea un Place Index"""
    print(f"\n📍 Creando Place Index: {index_name}")
    print("-" * 70)

    try:
        response = client.create_place_index(
            IndexName=index_name,
            DataSource='Esri',  # Esri es gratuito para 100k requests/mes
            Description='Place Index para búsqueda de talleres mecánicos y lugares',
            PricingPlan='RequestBasedUsage',  # Pricing basado en uso
            Tags={
                'Project': 'VehiculosMantenimiento',
                'Environment': 'Development',
                'ManagedBy': 'Python'
            }
        )

        print(f"✅ Place Index creado exitosamente!")
        print(f"   ARN: {response['IndexArn']}")
        print(f"   Nombre: {response['IndexName']}")
        return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConflictException':
            print(f"⚠️  El Place Index '{index_name}' ya existe")
            return True
        else:
            print(f"❌ Error al crear Place Index: {e}")
            return False


def create_map(client, map_name):
    """Crea un Map"""
    print(f"\n🗺️  Creando Map: {map_name}")
    print("-" * 70)

    try:
        response = client.create_map(
            MapName=map_name,
            Configuration={
                'Style': 'VectorEsriNavigation'  # Estilo de navegación Esri
            },
            Description='Mapa para visualización de talleres y vehículos',
            PricingPlan='RequestBasedUsage',
            Tags={
                'Project': 'VehiculosMantenimiento',
                'Environment': 'Development',
                'ManagedBy': 'Python'
            }
        )

        print(f"✅ Map creado exitosamente!")
        print(f"   ARN: {response['MapArn']}")
        print(f"   Nombre: {response['MapName']}")
        return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConflictException':
            print(f"⚠️  El Map '{map_name}' ya existe")
            return True
        else:
            print(f"❌ Error al crear Map: {e}")
            return False


def create_route_calculator(client, calculator_name):
    """Crea un Route Calculator (opcional pero útil)"""
    print(f"\n🛣️  Creando Route Calculator: {calculator_name}")
    print("-" * 70)

    try:
        response = client.create_route_calculator(
            CalculatorName=calculator_name,
            DataSource='Esri',
            Description='Calculador de rutas para navegación a talleres',
            PricingPlan='RequestBasedUsage',
            Tags={
                'Project': 'VehiculosMantenimiento',
                'Environment': 'Development',
                'ManagedBy': 'Python'
            }
        )

        print(f"✅ Route Calculator creado exitosamente!")
        print(f"   ARN: {response['CalculatorArn']}")
        print(f"   Nombre: {response['CalculatorName']}")
        return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConflictException':
            print(f"⚠️  El Route Calculator '{calculator_name}' ya existe")
            return True
        else:
            print(f"❌ Error al crear Route Calculator: {e}")
            return False


def verify_resources(client, place_index, map_name):
    """Verifica que los recursos existan y estén listos"""
    print(f"\n🔍 Verificando recursos creados...")
    print("-" * 70)

    all_ok = True

    # Verificar Place Index
    try:
        response = client.describe_place_index(IndexName=place_index)
        print(f"✅ Place Index verificado: {place_index}")
        print(f"   Status: {response.get('Status', 'N/A')}")
    except Exception as e:
        print(f"❌ Place Index no encontrado: {e}")
        all_ok = False

    # Verificar Map
    try:
        response = client.describe_map(MapName=map_name)
        print(f"✅ Map verificado: {map_name}")
    except Exception as e:
        print(f"❌ Map no encontrado: {e}")
        all_ok = False

    return all_ok


def main():
    print("\n" + "=" * 70)
    print(" " * 15 + "CREACIÓN DE RECURSOS AWS LOCATION")
    print("=" * 70)

    # Obtener configuración
    place_index = config('AWS_LOCATION_PLACE_INDEX', default='vehiculos-place-index')
    map_name = config('AWS_LOCATION_MAP', default='vehiculos-map')
    route_calculator = 'vehiculos-route-calculator'

    print(f"\nRecursos a crear:")
    print(f"  1. Place Index: {place_index}")
    print(f"  2. Map: {map_name}")
    print(f"  3. Route Calculator: {route_calculator} (opcional)")

    try:
        # Crear cliente
        location_client = boto3.client(
            'location',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=config('AWS_REGION', default='us-east-1')
        )

        # Crear recursos
        place_ok = create_place_index(location_client, place_index)
        map_ok = create_map(location_client, map_name)
        route_ok = create_route_calculator(location_client, route_calculator)

        # Verificar
        if place_ok and map_ok:
            print("\n")
            if verify_resources(location_client, place_index, map_name):
                print("\n" + "=" * 70)
                print("✅ TODOS LOS RECURSOS CREADOS Y VERIFICADOS EXITOSAMENTE")
                print("=" * 70)
                print("\nAhora puedes usar los endpoints de AWS Location Service:")
                print(f"  - http://localhost:8000/api/aws-maps/buscar-lugares/")
                print(f"  - http://localhost:8000/api/aws-maps/buscar-talleres/")
                print(f"  - http://localhost:8000/api/aws-maps/geocodificar/")
                print(f"  - http://localhost:8000/api/aws-maps/geocodificar-inverso/")
                print(f"  - http://localhost:8000/api/aws-maps/validar-configuracion/")
                print()
            else:
                print("\n" + "=" * 70)
                print("⚠️  ALGUNOS RECURSOS NO SE PUDIERON VERIFICAR")
                print("=" * 70 + "\n")
        else:
            print("\n" + "=" * 70)
            print("❌ ERROR AL CREAR RECURSOS")
            print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}\n")


if __name__ == "__main__":
    main()
