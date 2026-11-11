import copy, datetime, io, os, shutil, sys, tempfile, unittest
from unittest import mock

from negocio.tienda import Tienda
from negocio.ventas import Carrito
from negocio.errores import ErrorNegocio, ErrorValidacion
from negocio.caja import resumen_sesion
from persistencia import archivos_json as db