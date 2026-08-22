# RPA SRI — comprobantes electrónicos recibidos

Automatización en Python que usa Playwright para ingresar a **SRI en Línea** y descargar los reportes mensuales de comprobantes electrónicos recibidos. Está diseñada para ejecutarse de forma manual o diaria en macOS, sin duplicar archivos ya descargados.

## Qué hace

1. Inicia sesión en SRI en Línea con las credenciales configuradas localmente.
2. Abre el módulo de comprobantes electrónicos recibidos.
3. Selecciona automáticamente el mes y año actuales.
4. Descarga los reportes de Facturas, Notas de crédito, Notas de débito y Retenciones.
5. Los ordena por RUC, año y mes en `Desktop/Reportes_SRI/`.
6. Registra el resultado de cada ejecución y reintenta fallos transitorios.

No intenta resolver ni eludir CAPTCHA, verificaciones de seguridad ni controles del SRI. Si el portal los solicita, la ejecución termina y deja el detalle en los registros locales.

## Requisitos

- Python 3.11 o posterior.
- Acceso autorizado a SRI en Línea.
- macOS para la programación automática incluida. La ejecución manual puede funcionar en otros sistemas compatibles con Playwright.

## Instalación y configuración

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
# .venv\\Scripts\\activate

pip install -r requirements.txt
playwright install chromium

cp config/settings.example.py config/settings.py
```

Abra `config/settings.py` y complete únicamente `SRI_RUC` y `SRI_PASSWORD`. Ese archivo está excluido de Git por seguridad y **nunca debe publicarse**.

También puede ajustar la carpeta de salida, la hora diaria y los comprobantes incluidos desde el mismo archivo.

## Uso

Ejecute el proceso manualmente:

```bash
python main.py
```

Los reportes quedan en:

```text
Desktop/Reportes_SRI/<RUC>/<año>/<mes>_<Mes>/
```

Si el archivo de un comprobante ya existe y tiene contenido, el RPA lo conserva y no lo vuelve a descargar.

### Programación diaria en macOS

Una vez configurado el entorno, instale la tarea diaria:

```bash
python install_daily_schedule.py
```

Por defecto se ejecuta todos los días a las 10:00, usando la hora local del equipo. Para eliminar la tarea:

```bash
python install_daily_schedule.py --uninstall
```

## Pruebas

```bash
python -m unittest discover -s tests
```

## Estructura

- `main.py`: coordina la ejecución completa.
- `config/settings.example.py`: plantilla de configuración local sin credenciales.
- `install_daily_schedule.py`: instala o elimina la tarea diaria de macOS.
- `sri/`: inicio de sesión, navegación, filtros y descargas.
- `utils/`: fechas, nombres de archivos y registro de eventos.
- `tests/`: pruebas unitarias de utilidades.

## Seguridad

El repositorio ignora las credenciales locales, registros, cachés, binarios generados y paquetes portables. Antes de confirmar cambios, revise siempre que `config/settings.py`, archivos `.env` y cualquier reporte descargado no formen parte de Git.
