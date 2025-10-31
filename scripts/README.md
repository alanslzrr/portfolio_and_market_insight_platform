# Scripts de Utilidad

Este directorio contiene scripts de utilidad para tareas comunes de desarrollo, deployment y mantenimiento del sistema. Estos scripts automatizan procesos repetitivos y facilitan el trabajo con la plataforma.

## Archivos que Contendrá

- **setup_database.py**: Script para configuración inicial de base de datos:
  - Crea las tablas en la base de datos
  - Ejecuta migraciones iniciales
  - Crea índices necesarios
  - Inserta datos iniciales si es necesario

- **seed_data.py**: Script para poblar base de datos con datos de prueba:
  - Crea usuarios de prueba
  - Crea carteras de ejemplo
  - Crea operaciones de ejemplo
  - Útil para desarrollo y testing

- **migrate_database.py**: Script para ejecutar migraciones de base de datos:
  - Ejecuta migraciones pendientes
  - Rollback de migraciones si es necesario
  - Genera nuevas migraciones

- **backup_database.py**: Script para backup de base de datos:
  - Crea backup completo de PostgreSQL
  - Comprime backups
  - Gestiona retención de backups antiguos

- **clear_cache.py**: Script para limpiar caché:
  - Limpia caché de Redis
  - Invalida análisis cacheados
  - Limpia caché de precios expirados

- **sync_market_data.py**: Script para sincronización de datos de mercado:
  - Sincroniza precios de activos desde Alpha Vantage
  - Actualiza datos históricos
  - Útil para ejecutar como cron job

- **generate_docs.py**: Script para generación de documentación:
  - Genera documentación de API desde código
  - Genera documentación de modelos
  - Exporta esquemas OpenAPI

## Uso

Los scripts se ejecutan desde la raíz del proyecto:

```bash
python scripts/setup_database.py
python scripts/seed_data.py
python scripts/migrate_database.py
```

## Consideraciones

- Los scripts requieren configuración adecuada de variables de entorno
- Algunos scripts requieren permisos específicos (backup, migraciones)
- Los scripts incluyen validaciones para prevenir operaciones destructivas
- Los scripts incluyen logging para auditoría de operaciones

