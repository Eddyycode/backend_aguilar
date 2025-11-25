#!/usr/bin/env python
"""
Script para verificar la configuración de AWS Location Service
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import boto3
from decouple import config
from botocore.exceptions import ClientError, NoCredentialsError

def test_aws_credentials():
    """Verifica las credenciales de AWS"""
    print("=" * 60)
    print("1. VERIFICANDO CREDENCIALES DE AWS")
    print("=" * 60)

    try:
        # Obtener credenciales del .env
        access_key = config('AWS_ACCESS_KEY_ID')
        secret_key = config('AWS_SECRET_ACCESS_KEY')
        region = config('AWS_REGION', default='us-east-1')

        print(f"✓ AWS_ACCESS_KEY_ID: {access_key[:10]}... (oculto por seguridad)")
        print(f"✓ AWS_SECRET_ACCESS_KEY: {'*' * 20} (oculto por seguridad)")
        print(f"✓ AWS_REGION: {region}")

        # Crear cliente STS para verificar credenciales
        sts_client = boto3.client(
            'sts',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # Obtener identidad del usuario
        identity = sts_client.get_caller_identity()
        print(f"\n✓ Credenciales válidas!")
        print(f"  - User ARN: {identity['Arn']}")
        print(f"  - Account ID: {identity['Account']}")
        print(f"  - User ID: {identity['UserId']}")

        return True

    except NoCredentialsError:
        print("✗ ERROR: No se encontraron credenciales de AWS")
        return False
    except ClientError as e:
        print(f"✗ ERROR: Credenciales inválidas - {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def test_location_service():
    """Verifica el servicio de AWS Location"""
    print("\n" + "=" * 60)
    print("2. VERIFICANDO AWS LOCATION SERVICE")
    print("=" * 60)

    try:
        # Crear cliente de Location
        location_client = boto3.client(
            'location',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=config('AWS_REGION', default='us-east-1')
        )

        print("✓ Cliente de AWS Location Service creado exitosamente")

        # Listar todos los Place Indexes
        print("\n--- Place Indexes disponibles ---")
        try:
            place_indexes = location_client.list_place_indexes()
            if place_indexes['Entries']:
                for idx in place_indexes['Entries']:
                    print(f"  ✓ {idx['IndexName']}")
                    print(f"    - Data Source: {idx.get('DataSource', 'N/A')}")
                    print(f"    - Create Time: {idx.get('CreateTime', 'N/A')}")
            else:
                print("  ⚠ No hay Place Indexes creados")
        except ClientError as e:
            print(f"  ✗ Error al listar Place Indexes: {e}")

        # Listar todos los Maps
        print("\n--- Maps disponibles ---")
        try:
            maps = location_client.list_maps()
            if maps['Entries']:
                for map_item in maps['Entries']:
                    print(f"  ✓ {map_item['MapName']}")
                    print(f"    - Data Source: {map_item.get('DataSource', 'N/A')}")
                    print(f"    - Create Time: {map_item.get('CreateTime', 'N/A')}")
            else:
                print("  ⚠ No hay Maps creados")
        except ClientError as e:
            print(f"  ✗ Error al listar Maps: {e}")

        return True

    except NoCredentialsError:
        print("✗ ERROR: No se encontraron credenciales")
        return False
    except ClientError as e:
        print(f"✗ ERROR: {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def test_specific_resources():
    """Verifica los recursos específicos configurados"""
    print("\n" + "=" * 60)
    print("3. VERIFICANDO RECURSOS ESPECÍFICOS")
    print("=" * 60)

    place_index = config('AWS_LOCATION_PLACE_INDEX', default='vehiculos-place-index')
    map_name = config('AWS_LOCATION_MAP', default='vehiculos-map')

    print(f"\nRecursos configurados en .env:")
    print(f"  - Place Index: {place_index}")
    print(f"  - Map: {map_name}")

    try:
        location_client = boto3.client(
            'location',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=config('AWS_REGION', default='us-east-1')
        )

        # Verificar Place Index
        print(f"\n--- Verificando Place Index: {place_index} ---")
        try:
            response = location_client.describe_place_index(IndexName=place_index)
            print(f"  ✓ Place Index encontrado!")
            print(f"    - Data Source: {response.get('DataSource', 'N/A')}")
            print(f"    - Description: {response.get('Description', 'N/A')}")
            print(f"    - ARN: {response.get('IndexArn', 'N/A')}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"  ✗ Place Index '{place_index}' NO EXISTE")
                print(f"    Necesitas crear este recurso en AWS Console")
            else:
                print(f"  ✗ Error: {e}")

        # Verificar Map
        print(f"\n--- Verificando Map: {map_name} ---")
        try:
            response = location_client.describe_map(MapName=map_name)
            print(f"  ✓ Map encontrado!")
            print(f"    - Data Source: {response.get('DataSource', 'N/A')}")
            print(f"    - Description: {response.get('Description', 'N/A')}")
            print(f"    - ARN: {response.get('MapArn', 'N/A')}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"  ✗ Map '{map_name}' NO EXISTE")
                print(f"    Necesitas crear este recurso en AWS Console")
            else:
                print(f"  ✗ Error: {e}")

        return True

    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def test_iam_permissions():
    """Verifica los permisos IAM"""
    print("\n" + "=" * 60)
    print("4. VERIFICANDO PERMISOS IAM")
    print("=" * 60)

    try:
        iam_client = boto3.client(
            'iam',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=config('AWS_REGION', default='us-east-1')
        )

        # Obtener usuario actual
        print("\nIntentando obtener información del usuario IAM...")
        try:
            # Primero obtenemos el username del ARN
            sts = boto3.client(
                'sts',
                aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
                region_name=config('AWS_REGION', default='us-east-1')
            )
            identity = sts.get_caller_identity()
            arn = identity['Arn']
            username = arn.split('/')[-1]

            print(f"✓ Usuario IAM: {username}")

            # Listar políticas adjuntas al usuario
            print(f"\nPolíticas adjuntas al usuario '{username}':")
            attached_policies = iam_client.list_attached_user_policies(UserName=username)

            if attached_policies['AttachedPolicies']:
                for policy in attached_policies['AttachedPolicies']:
                    print(f"  ✓ {policy['PolicyName']}")
                    print(f"    ARN: {policy['PolicyArn']}")
            else:
                print("  ⚠ No hay políticas adjuntas directamente al usuario")

            # Listar grupos del usuario
            print(f"\nGrupos del usuario '{username}':")
            groups = iam_client.list_groups_for_user(UserName=username)

            if groups['Groups']:
                for group in groups['Groups']:
                    print(f"  ✓ {group['GroupName']}")
            else:
                print("  ⚠ El usuario no pertenece a ningún grupo")

        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                print("  ⚠ No tienes permisos para consultar información IAM")
                print("    Esto no afecta el uso de Location Service")
            else:
                print(f"  ✗ Error: {e}")

        return True

    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "VERIFICACIÓN AWS LOCATION SERVICE" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    # Ejecutar todas las verificaciones
    creds_ok = test_aws_credentials()

    if creds_ok:
        test_location_service()
        test_specific_resources()
        test_iam_permissions()

    print("\n" + "=" * 60)
    print("VERIFICACIÓN COMPLETADA")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
