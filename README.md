# ☕ CaféCol CloudApp

**Proyecto Final · Cloud Computing · UDEA 2026**

Aplicación web serverless para registro de pedidos de café, desplegada en AWS.

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | HTML/CSS/JS estático en **Amazon S3** |
| API | **Amazon API Gateway** (HTTP API) |
| Backend | **AWS Lambda** (Python 3.11) |
| Base de datos | **Amazon DynamoDB** (PAY_PER_REQUEST) |
| Monitoreo | **Amazon CloudWatch** (Logs + Metrics + Alarms) |
| IaC | **Serverless Framework v3** |

## Estructura

```
cafecol/
├── frontend/
│   └── index.html          ← Sitio web (subir a S3)
├── backend/
│   └── lambda_function.py  ← Lógica serverless
├── iac/
│   └── serverless.yaml     ← Infraestructura como Código
└── docs/
    ├── documento_tecnico.md
    └── arquitectura.html
```

## Despliegue rápido

```bash
# 1. Configurar AWS CLI
aws configure

# 2. Desplegar infraestructura
cd iac/
npm install -g serverless
sls deploy --stage prod

# 3. Copiar el API endpoint del output y pegarlo en frontend/index.html
# Busca: const API_URL = 'https://TU_API_GATEWAY_ID...'

# 4. Subir frontend a S3
aws s3 sync ../frontend/ s3://NOMBRE-DE-TU-BUCKET/ --acl public-read
```

## API

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/pedidos` | Crear nuevo pedido |
| GET | `/pedidos` | Listar pedidos recientes |

### Ejemplo POST

```json
{
  "nombre": "María García",
  "cafe": "Cappuccino",
  "cantidad": 2,
  "notas": "Sin azúcar"
}
```

### Respuesta

```json
{
  "mensaje": "¡Pedido registrado con éxito!",
  "pedido_id": "A3F9C21B",
  "timestamp": "2026-06-01T14:30:00Z"
}
```

---

*UDEA · Ingeniería de Sistemas · 2026*
