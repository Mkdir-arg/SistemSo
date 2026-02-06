# Bienvenido a la Documentación de SistemSo

Sistema de gestión integral desarrollado con Django, diseñado para proporcionar una plataforma robusta y escalable.

## Navegación Rápida

### 📐 [Arquitectura](arquitectura/ARQUITECTURA_v1.0_2025-02-06.md)
Documentación técnica completa del sistema, incluyendo stack tecnológico, patrones de diseño y arquitectura de deployment.

### 🔄 [Pull Requests](prs/index.md)
Historial detallado de todos los Pull Requests del proyecto, con información técnica y funcional de cada cambio.

### 📦 [Versiones](versiones/index.md)
Documentación de cada versión liberada, incluyendo funcionalidades nuevas, correcciones y cambios técnicos.

### 📝 [CHANGELOG](../CHANGELOG.md)
Registro cronológico de todos los cambios del proyecto.

## Características Principales

- **Sistema de Mensajería en Tiempo Real**: WebSockets con Django Channels
- **API REST**: Django REST Framework con documentación automática
- **Arquitectura Híbrida**: Gunicorn (HTTP) + Daphne (WebSockets)
- **Cache Distribuido**: Redis para cache, sesiones y channel layers
- **Monitoreo**: Sistema de métricas y profiling integrado
- **Auditoría**: Tracking completo de acciones y accesos

## Stack Tecnológico

- **Backend**: Django 4.2 + Python 3.11
- **Base de Datos**: MySQL 8.0
- **Cache**: Redis 7
- **WebSockets**: Django Channels + Daphne
- **HTTP Server**: Gunicorn + gevent
- **Proxy**: Nginx
- **Contenedores**: Docker + Docker Compose

## Convenciones de Desarrollo

### Commits
Utilizamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat(modulo): descripción` - Nueva funcionalidad
- `fix(modulo): descripción` - Corrección de bug
- `refactor(modulo): descripción` - Refactorización
- `docs(modulo): descripción` - Documentación
- `perf(modulo): descripción` - Mejora de performance

### Versionado
Seguimos [Semantic Versioning](https://semver.org/):

- **MAJOR**: Cambios incompatibles
- **MINOR**: Nueva funcionalidad compatible
- **PATCH**: Correcciones compatibles

## Contribuir

1. Crear rama desde `Dev`
2. Realizar cambios siguiendo convenciones
3. Crear Pull Request
4. La documentación se genera automáticamente

---

*Última actualización: {{ git_revision_date_localized }}*
