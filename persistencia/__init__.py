"""Paquete de persistencia en archivos JSON"""
"""Paquete de persistencia en archivos JSON para el Sistema de Gestión de Supermercado"""

from .archivos_json import ErrorPersistencia, configurar_directorio, obtener_directorio
from .archivos_json import guardar, guardar_varios, leer_json


__all__ = [
    'ErrorPersistencia',
    'configurar_directorio',
    'obtener_directorio',
    'guardar',
    'guardar_varios',
    'leer_json',
]