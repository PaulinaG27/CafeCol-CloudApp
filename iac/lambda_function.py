"""
CaféCol - Lambda Function: gestión de pedidos
Conectada a API Gateway (HTTP POST) y DynamoDB.
"""

import json
import uuid
import boto3
import os
from datetime import datetime

# Cliente DynamoDB (la región y tabla se leen desde variables de entorno)
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'cafecol-pedidos')


def lambda_handler(event, context):
    """Punto de entrada principal de la Lambda."""

    # CORS headers para permitir peticiones desde el frontend en S3
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',          # En producción: reemplaza por tu dominio S3
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }

    # Preflight OPTIONS (CORS)
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS' \
       or event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    http_method = (
        event.get('requestContext', {}).get('http', {}).get('method')
        or event.get('httpMethod', 'POST')
    )
    path = (
        event.get('requestContext', {}).get('http', {}).get('path')
        or event.get('path', '/pedidos')
    )

    try:
        if http_method == 'POST' and '/pedidos' in path:
            return crear_pedido(event, headers)
        elif http_method == 'GET' and '/pedidos' in path:
            return listar_pedidos(headers)
        else:
            return respuesta(404, {'error': 'Ruta no encontrada'}, headers)

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return respuesta(500, {'error': 'Error interno del servidor', 'detalle': str(e)}, headers)


# ─────────────────────────────────────────────
# POST /pedidos  →  crear un nuevo pedido
# ─────────────────────────────────────────────
def crear_pedido(event, headers):
    body_raw = event.get('body', '{}') or '{}'
    
    # API Gateway puede enviar el body codificado en base64
    if event.get('isBase64Encoded'):
        import base64
        body_raw = base64.b64decode(body_raw).decode('utf-8')

    body = json.loads(body_raw)

    # Validación básica
    nombre = body.get('nombre', '').strip()
    cafe   = body.get('cafe', '').strip()
    if not nombre or not cafe:
        return respuesta(400, {'error': 'Los campos "nombre" y "cafe" son obligatorios'}, headers)

    # Construir ítem para DynamoDB
    pedido_id = str(uuid.uuid4())[:8].upper()   # ID corto legible, ej: "A3F9C21B"
    timestamp = datetime.utcnow().isoformat() + 'Z'

    item = {
        'pedido_id':  pedido_id,
        'timestamp':  timestamp,
        'nombre':     nombre,
        'cafe':       cafe,
        'cantidad':   int(body.get('cantidad', 1)),
        'notas':      body.get('notas', '').strip(),
        'estado':     'RECIBIDO'
    }

    # Guardar en DynamoDB
    tabla = dynamodb.Table(TABLE_NAME)
    tabla.put_item(Item=item)

    print(f"Pedido creado: {pedido_id} | {nombre} | {cafe} x{item['cantidad']}")

    return respuesta(201, {
        'mensaje':   '¡Pedido registrado con éxito!',
        'pedido_id': pedido_id,
        'timestamp': timestamp
    }, headers)


# ─────────────────────────────────────────────
# GET /pedidos  →  listar los últimos pedidos
# ─────────────────────────────────────────────
def listar_pedidos(headers):
    tabla = dynamodb.Table(TABLE_NAME)
    result = tabla.scan(Limit=20)   # En producción usa Query con un índice GSI
    items = result.get('Items', [])

    # Ordenar por timestamp descendente
    items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    return respuesta(200, {'pedidos': items, 'total': len(items)}, headers)


# ─────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────
def respuesta(status_code, body, headers):
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(body, ensure_ascii=False, default=str)
    }
