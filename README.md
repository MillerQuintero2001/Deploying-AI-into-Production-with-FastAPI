# Deploying AI into Production with FastAPI

Repositorio del curso de **DataCamp**: *"Deploying AI into Production with FastAPI"*

Este repositorio contiene ejemplos prácticos y ejercicios progresivos que demuestran cómo construir y desplegar APIs de modelos de Machine Learning e IA usando **FastAPI**, desde conceptos básicos hasta mejores prácticas de producción.

---

## 📋 Estructura del Proyecto

```
📦 Deploying-AI-into-Production-with-FastAPI/
├── 1_Chapter/          # Fundamentos de FastAPI y Pydantic
├── 2_Chapter/          # Gestión de ciclo de vida y validación
├── 3_Chapter/          # Seguridad, autenticación y asincronía
├── 4_Chapter/          # Versionado, monitoreo y validaciones avanzadas
├── Presentations/      # Material de presentación del curso
├── LICENSE
├── pyproject.toml
└── README.md
```

---

## 📚 Contenido por Capítulo

### 🟢 **Capítulo 1: Fundamentos de FastAPI**

**Ubicación:** [`1_Chapter/`](1_Chapter/)

Este capítulo introduce los conceptos básicos de FastAPI y Pydantic para crear APIs simples de predicción.

#### Archivos:

- **[`penguin_api.py`](1_Chapter/penguin_api.py)** - API básica de clasificación de especies de pingüinos
  - Carga de modelos con `joblib`
  - Validación de entrada con `BaseModel` de Pydantic
  - Endpoint POST `/predict` para predicción de especies
  - Respuesta con especies predichas y niveles de confianza
  
- **[`coffee_api.py`](1_Chapter/coffee_api.py)** ⚠️ - API de calidad de café (*solo ilustrativo, sin modelo*)
  - Ejemplo de estructura de API para predicción de calidad
  - Validación de atributos: aroma, sabor, altitud
  - Respuesta con score de calidad y confianza
  - **Nota:** Este archivo es solo para demostración y no incluye un modelo entrenado
  
- **[`diabetes.py`](1_Chapter/diabetes.py)** ⚠️ - API de progresión de diabetes (*solo ilustrativo, sin modelo*)
  - Estructura básica de predicción médica
  - Entrada: edad, BMI, presión arterial
  - Predicción de progresión de diabetes
  - **Nota:** Este archivo es solo para demostración y no incluye un modelo entrenado
  
- **[`model_info.py`](1_Chapter/model_info.py)** - Sistema de registro de modelos
  - Uso de path parameters (`/model-info/{model_id}`)
  - Manejo de códigos de estado HTTP (404, 201)
  - Base de datos simulada para información de modelos
  - Endpoint GET y POST para consulta y registro

**Conceptos clave:** 
- Estructura básica de FastAPI
- Modelos Pydantic para validación
- Respuestas con `response_model`
- Códigos de estado HTTP
- Path y body parameters

---

### 🟡 **Capítulo 2: Gestión de Ciclo de Vida y Validación**

**Ubicación:** [`2_Chapter/`](2_Chapter/)

Este capítulo cubre la gestión del ciclo de vida de las aplicaciones, validaciones personalizadas y manejo de errores.

#### Archivos:

- **[`main_ml_api.py`](2_Chapter/main_ml_api.py)** - API de análisis de sentimiento con gestión de ciclo de vida
  - Uso de `lifespan` para carga de modelo en startup
  - **Uso de `app.state` para almacenar el modelo** (evita variables globales)
  - Manejo global de excepciones
  - Validación de entrada vacía
  - Respuestas estructuradas con confianza
  
- **[`sentiment_model.py`](2_Chapter/sentiment_model.py)** - Clase reutilizable de análisis de sentimiento
  - Implementación de modelo como clase callable (`__call__`)
  - Entrenamiento automático si no existe modelo
  - Feature engineering: conteo de palabras positivas/negativas
  - Serialización con `joblib`
  
- **[`main_validate_api.py`](2_Chapter/main_validate_api.py)** - Validaciones personalizadas con Pydantic
  - `@field_validator` para validación de campos específicos
  - `Field()` con restricciones de longitud
  - Validación de dominio de email personalizada
  - Manejo de errores de validación
  
- **[`main_text_api.py`](2_Chapter/main_text_api.py)** - Análisis de texto con detección de keywords
  - Procesamiento de texto sin modelo ML
  - Detección de contenido problemático (spam, hate, offensive, abuse)
  - Respuesta con issues encontrados y conteo
  
- **[`main_scorer_api.py`](2_Chapter/main_scorer_api.py)** - Sistema de scoring de confianza
  - Modelo de scoring basado en métricas de comentarios
  - Normalización de features (longitud, reputación, reportes)
  - Predicción de trust score (0-100)

**Conceptos clave:**
- Context managers con `@asynccontextmanager`
- Gestión de lifespan (startup/shutdown)
- **Uso de `app.state` para gestión de modelos** (mejora sobre variables globales)
- Validadores personalizados de Pydantic
- Clases callable para modelos ML
- Manejo robusto de errores

---

### 🔵 **Capítulo 3: Seguridad, Autenticación y Asincronía**

**Ubicación:** [`3_Chapter/`](3_Chapter/)

Este capítulo se enfoca en seguridad, rate limiting, operaciones asíncronas y timeouts.

#### Archivos:

- **[`main_key_api.py`](3_Chapter/main_key_api.py)** - Autenticación básica con API Key
  - Uso de `APIKeyHeader` para autenticación
  - Validación de API key con variables de entorno
  - Protección de endpoints con `Depends()`
  - Respuesta 403 para claves inválidas
  
- **[`main_secure_api.py`](3_Chapter/main_secure_api.py)** - API segura de análisis de sentimiento
  - Integración de autenticación en endpoints ML
  - Función `verify_api_key` reutilizable
  - Protección completa de la aplicación
  
- **[`main_rate_limit_api.py`](3_Chapter/main_rate_limit_api.py)** - Implementación de rate limiting
  - Limitador de peticiones por minuto
  - Seguimiento por API key
  - Ventana deslizante de tiempo
  - Respuesta 429 cuando se excede el límite
  
- **[`main_async_api.py`](3_Chapter/main_async_api.py)** - Endpoints asíncronos
  - Uso de `async/await` para operaciones no bloqueantes
  - `asyncio.to_thread()` para código síncrono
  - Procesamiento en background con `BackgroundTasks`
  - Análisis batch de múltiples reviews
  
- **[`main_timeout_api.py`](3_Chapter/main_timeout_api.py)** - Manejo de timeouts
  - `asyncio.wait_for()` con límite de tiempo
  - Captura de `TimeoutError`
  - Respuesta 408 (Request Timeout)
  - Prevención de operaciones largas
  
- **[`sentiment_model.py`](3_Chapter/sentiment_model.py)** - Modelo con funcionalidades de seguridad
  - Integración de rate limiter
  - Función de verificación de API key
  - Método asíncrono `async_call()` con sleep configurable

**Conceptos clave:**
- Autenticación con headers
- Rate limiting personalizado
- Programación asíncrona
- Manejo de timeouts
- Background tasks
- Variables de entorno con `.env`

---

### 🔴 **Capítulo 4: Versionado, Monitoreo y Validaciones Avanzadas** ⭐

**Ubicación:** [`4_Chapter/`](4_Chapter/)

Este capítulo cubre técnicas avanzadas de producción: versionado de APIs, logging, middleware y validaciones complejas.

#### Archivos:

- **[`main_versioning_api.py`](4_Chapter/main_versioning_api.py)** - Versionado de API
  - Endpoints versionados: `/v1/` y `/v2/`
  - Modelos de entrada diferentes por versión
  - Compatibilidad backward con conversión automática
  - Manejo de formatos de datos distintos
  
- **[`main_input_validation.py`](4_Chapter/main_input_validation.py)** - Validaciones avanzadas con Pydantic
  - `@model_validator(mode="before")` para validación pre-procesamiento
  - `@model_validator(mode="after")` para validación post-procesamiento
  - Validaciones customizadas (lista no vacía, valores positivos)
  - Exception handler global para errores de validación
  - Modelos: `ModelInput`, `BatchInput`, `InventoryRecord`
  - Ejemplos curl para testing
  
- **[`main_log_monitor_api.py`](4_Chapter/main_log_monitor_api.py)** 🏆 - **API definitiva con mejores prácticas**
  - ✅ **Middleware HTTP** para logging de tiempo de procesamiento
  - ✅ **Logging estructurado** con logger de uvicorn
  - ✅ **Health check endpoint** (`/health`) con información del modelo
  - ✅ **Versionado de endpoints** (v1 y v2)
  - ✅ **Validaciones complejas** con Pydantic validators
  - ✅ **Autenticación** con API keys
  - ✅ **Rate limiting**
  - ✅ **Gestión de ciclo de vida mejorada** con `app.state.classifier` (sin variables globales)
  - ✅ **Manejo de errores** robusto con códigos HTTP apropiados
  - ✅ **Serialización segura** de parámetros del modelo
  - ✅ **Respuestas en texto plano** para health checks
  - ✅ **Exception handlers globales**
  
  **Este es el script que reúne todas las mejores prácticas del curso y representa una implementación production-ready.**
  
- **[`penguin_model.py`](4_Chapter/penguin_model.py)** - Modelo y utilidades reutilizables
  - Clase `PenguinClassifier` con método `__call__`
  - Clase `RateLimiter` con ventana deslizante
  - Funciones de autenticación: `verify_api_key`, `test_api_key`
  - Inicialización de rate limiter global
  - Manejo de DataFrame con pandas

**Conceptos clave:**
- Versionado de APIs
- Middleware personalizado
- Logging y monitoreo
- Health checks
- Validaciones en múltiples etapas
- Exception handlers globales
- Respuestas personalizadas (JSON, PlainText)
- Serialización segura de objetos complejos

---

## 🚀 Cómo Ejecutar

### Prerrequisitos

```bash
# Instalar dependencias
pip install fastapi uvicorn joblib scikit-learn pandas python-dotenv pydantic
```

### Ejecutar una API

Opción 1: Usando el CLI de uvicorn (recomendado)
```bash
cd 4_Chapter/
uvicorn main_log_monitor_api:app --reload --host 0.0.0.0 --port 8080
```

Opción 2: Ejecutando el script directamente
```bash
python 4_Chapter/main_log_monitor_api.py
```

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:
```env
API_KEY=your_secret_key
```

---

## 🧪 Testing con cURL

### Ejemplo: Clasificación de Pingüinos (v1)
```bash
curl -X POST "http://localhost:8080/v1/penguin_classifier" \
  -H "X-API-Key: your_secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "bill_length_mm": 39.1,
    "bill_depth_mm": 18.7,
    "flipper_length_mm": 181,
    "body_mass_g": 3750
  }'
```

### Ejemplo: Health Check
```bash
curl -X GET "http://localhost:8080/health"
```

### Ejemplo: Validación con error
```bash
curl -X POST "http://localhost:8080/v1/register_inventory" \
  -H "Content-Type: application/json" \
  -d '{"name": "apple", "quantity": -5}'
```

---

## 📊 Modelos ML Incluidos

| Modelo | Ubicación | Descripción |
|--------|-----------|-------------|
| **Penguin Classifier** | `4_Chapter/models/penguin_classifier.pkl` | Clasificación de especies de pingüinos (Adelie, Chinstrap, Gentoo) |
| **Sentiment Model** | `2_Chapter/models/sentiment_model.joblib` | Análisis de sentimiento (Positivo/Negativo) |

> ⚠️ **Nota:** Los scripts `coffee_api.py` y `diabetes.py` en el Capítulo 1 **no incluyen modelos entrenados** y son solo para fines ilustrativos de la estructura de una API.

---

## 🎓 Aprendizajes Clave del Curso

1. **Fundamentos de FastAPI**
   - Creación de endpoints RESTful
   - Validación automática con Pydantic
   - Documentación interactiva (Swagger UI)

2. **Gestión del Ciclo de Vida**
   - Carga de modelos en startup
   - **Uso de `app.state` en lugar de variables globales** para almacenar modelos
   - Limpieza de recursos en shutdown
   - Context managers asíncronos

3. **Seguridad y Autenticación**
   - API Keys con headers
   - Rate limiting por cliente
   - Variables de entorno seguras

4. **Asincronía y Performance**
   - Endpoints asíncronos
   - Background tasks
   - Manejo de timeouts

5. **Producción y Monitoreo**
   - Middleware personalizado
   - Logging estructurado
   - Health checks
   - Versionado de APIs
   - Exception handlers globales

---

## 🏆 API Definitiva: `main_log_monitor_api.py`

El archivo **[`4_Chapter/main_log_monitor_api.py`](4_Chapter/main_log_monitor_api.py)** representa la culminación del curso, integrando todas las mejores prácticas aprendidas:

- ✅ Arquitectura robusta y escalable
- ✅ Seguridad con autenticación y rate limiting
- ✅ Monitoreo con logging y middleware
- ✅ Validaciones exhaustivas en múltiples capas
- ✅ Versionado para compatibilidad
- ✅ Health checks para infraestructura
- ✅ Manejo de errores production-ready
- ✅ Código limpio y documentado

**Este script está listo para ser desplegado en producción** y sirve como referencia para implementaciones futuras.

---

## 📖 Recursos Adicionales

- [Documentación oficial de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación de Pydantic](https://docs.pydantic.dev/)
- [Uvicorn - ASGI Server](https://www.uvicorn.org/)
- [Curso en DataCamp](https://www.datacamp.com/)

---

## 📝 Licencia

Este proyecto está bajo la licencia especificada en el archivo [`LICENSE`](LICENSE).

---

## 👤 Autor

**Miller** - Estudiante del curso "Deploying AI into Production with FastAPI" de DataCamp

---

## 🌟 Agradecimientos

- **DataCamp** por el excelente contenido del curso
- **FastAPI** por crear un framework increíble para Python
- La comunidad open-source por las herramientas utilizadas
