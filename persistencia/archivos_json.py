import json
import os
import tempfile
import shutil


CARPETA_DATOS = None


class ErrorPersistencia(Exception):
    """Excepción personalizada para errores de guardado y carga de archivos JSON."""
    pass


def _ruta(nombre_archivo):
    """Devuelve la ruta completa al archivo JSON dentro de la carpeta de datos."""
    if CARPETA_DATOS is None:
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, "Datos", nombre_archivo)
    return os.path.join(CARPETA_DATOS, nombre_archivo)


def configurar_directorio(ruta_carpeta):
    """Define una carpeta distinta para leer/escribir archivos (útil en pruebas)."""
    global CARPETA_DATOS
    CARPETA_DATOS = ruta_carpeta
    os.makedirs(CARPETA_DATOS, exist_ok=True)


def obtener_directorio():
    """Devuelve la carpeta que se está usando actualmente."""
    return CARPETA_DATOS


def guardar(nombre_archivo, datos):
    """Guarda 'datos' como JSON en el archivo indicado de forma atómica.
    Primero escribe en un temporal, luego lo reemplaza solo si todo salió bien."""
    ruta_destino = _ruta(nombre_archivo)
    os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)

    try:
        fh, temporal = tempfile.mkstemp(dir=os.path.dirname(ruta_destino), suffix='.tmp')
        with os.fdopen(fh, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporal, ruta_destino)
    except (TypeError, ValueError, OSError) as e:
        if 'temporal' in locals() and os.path.exists(temporal):
            os.remove(temporal)
        raise ErrorPersistencia(f"No se pudo guardar {nombre_archivo}: {str(e)}") from e


def guardar_varios(lista_nombre_datos):
    """Guarda varios archivos a la vez. Si alguno falla, lanza ErrorPersistencia."""
    for nombre, datos in lista_nombre_datos:
        guardar(nombre, datos)


def leer_json(nombre_archivo, valor_por_defecto=None):
    """Lee y parsea un archivo JSON. Si no existe, devuelve el valor por defecto.
    Si está dañado, lanza ErrorPersistencia."""
    ruta_archivo = _ruta(nombre_archivo)

    if not os.path.exists(ruta_archivo):
        if valor_por_defecto is not None:
            return valor_por_defecto
        raise ErrorPersistencia(f"El archivo {nombre_archivo} no existe")

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ErrorPersistencia(f"El archivo {nombre_archivo} está dañado: {str(e)}") from e
    except OSError as e:
        raise ErrorPersistencia(f"No se pudo leer {nombre_archivo}: {str(e)}") from e
