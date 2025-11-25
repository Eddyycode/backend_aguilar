#!/usr/bin/env python
"""
Lista TODOS los recursos de AWS Location Service en tu cuenta
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import boto3
from decouple import config
from botocore.exceptions import ClientError

def main():
    print("\n" + "=" * 70)
    print(" " * 15 + "LISTANDO TODOS LOS RECURSOS AWS LOCATION")
    print("=" * 70 + "\n")

    try:
        location_client = boto3.client(
            'location',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=config('AWS_REGION', default='us-east-1')
        )

        # Listar Place Indexes
        print("📍 PLACE INDEXES:")
        print("-" * 70)
        try:
            response = location_client.list_place_indexes(MaxResults=100)
            if response['Entries']:
                for idx, item in enumerate(response['Entries'], 1):
                    print(f"\n{idx}. {item['IndexName']}")
                    print(f"   Data Source: {item.get('DataSource', 'N/A')}")
                    print(f"   Description: {item.get('Description', 'Sin descripción')}")
                    print(f"   Created: {item.get('CreateTime', 'N/A')}")

                    # Obtener detalles completos
                    try:
                        details = location_client.describe_place_index(IndexName=item['IndexName'])
                        print(f"   Pricing Plan: {details.get('PricingPlan', 'N/A')}")
                    except:
                        pass
            else:
                print("   ⚠️  No hay Place Indexes creados")
        except ClientError as e:
            print(f"   ❌ Error: {e}")

        # Listar Maps
        print("\n\n🗺️  MAPS:")
        print("-" * 70)
        try:
            response = location_client.list_maps(MaxResults=100)
            if response['Entries']:
                for idx, item in enumerate(response['Entries'], 1):
                    print(f"\n{idx}. {item['MapName']}")
                    print(f"   Data Source: {item.get('DataSource', 'N/A')}")
                    print(f"   Description: {item.get('Description', 'Sin descripción')}")
                    print(f"   Created: {item.get('CreateTime', 'N/A')}")

                    # Obtener detalles completos
                    try:
                        details = location_client.describe_map(MapName=item['MapName'])
                        print(f"   Pricing Plan: {details.get('PricingPlan', 'N/A')}")
                    except:
                        pass
            else:
                print("   ⚠️  No hay Maps creados")
        except ClientError as e:
            print(f"   ❌ Error: {e}")

        # Listar Trackers
        print("\n\n📡 TRACKERS:")
        print("-" * 70)
        try:
            response = location_client.list_trackers(MaxResults=100)
            if response['Entries']:
                for idx, item in enumerate(response['Entries'], 1):
                    print(f"\n{idx}. {item['TrackerName']}")
                    print(f"   Description: {item.get('Description', 'Sin descripción')}")
                    print(f"   Created: {item.get('CreateTime', 'N/A')}")
            else:
                print("   ⚠️  No hay Trackers creados")
        except ClientError as e:
            print(f"   ❌ Error: {e}")

        # Listar Geofence Collections
        print("\n\n🚧 GEOFENCE COLLECTIONS:")
        print("-" * 70)
        try:
            response = location_client.list_geofence_collections(MaxResults=100)
            if response['Entries']:
                for idx, item in enumerate(response['Entries'], 1):
                    print(f"\n{idx}. {item['CollectionName']}")
                    print(f"   Description: {item.get('Description', 'Sin descripción')}")
                    print(f"   Created: {item.get('CreateTime', 'N/A')}")
            else:
                print("   ⚠️  No hay Geofence Collections creadas")
        except ClientError as e:
            print(f"   ❌ Error: {e}")

        # Listar Route Calculators
        print("\n\n🛣️  ROUTE CALCULATORS:")
        print("-" * 70)
        try:
            response = location_client.list_route_calculators(MaxResults=100)
            if response['Entries']:
                for idx, item in enumerate(response['Entries'], 1):
                    print(f"\n{idx}. {item['CalculatorName']}")
                    print(f"   Data Source: {item.get('DataSource', 'N/A')}")
                    print(f"   Description: {item.get('Description', 'Sin descripción')}")
                    print(f"   Created: {item.get('CreateTime', 'N/A')}")
            else:
                print("   ⚠️  No hay Route Calculators creados")
        except ClientError as e:
            print(f"   ❌ Error: {e}")

        print("\n" + "=" * 70)
        print("✅ LISTADO COMPLETADO")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}\n")


if __name__ == "__main__":
    main()
