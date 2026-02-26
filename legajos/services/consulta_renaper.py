import datetime
import logging
import random
import time
import unicodedata

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, RequestException
from urllib3.util.retry import Retry

from core.models import Provincia

logger = logging.getLogger(__name__)


def _clean_api_base(raw_url):
    if not raw_url:
        return ""
    return str(raw_url).strip().strip('"').strip("'").rstrip("/")


def _parse_positive_int(raw_value, default):
    try:
        value = int(raw_value)
        return value if value > 0 else default
    except (TypeError, ValueError):
        return default


def _normalizar_sexo(sexo):
    raw = (sexo or "").strip()
    norm = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode("utf-8").lower()
    mapping = {
        "m": "M",
        "masculino": "M",
        "hombre": "M",
        "f": "F",
        "femenino": "F",
        "mujer": "F",
        "x": "X",
        "no binario": "X",
        "nobinario": "X",
        "otro": "X",
    }
    return mapping.get(norm, raw.upper() if raw else "")


class APIClient:
    def __init__(self):
        self.username = settings.RENAPER_API_USERNAME
        self.password = settings.RENAPER_API_PASSWORD
        self.api_base = _clean_api_base(settings.RENAPER_API_URL)
        self.login_url = f"{self.api_base}/auth/login"
        self.consulta_url = f"{self.api_base}/consultarenaper"

        connect_timeout = _parse_positive_int(getattr(settings, "RENAPER_CONNECT_TIMEOUT", 10), 10)
        read_timeout = _parse_positive_int(getattr(settings, "RENAPER_TIMEOUT", 20), 20)
        self.timeout = (connect_timeout, read_timeout)

        self.token = None
        self.token_expiration = None
        self.session = requests.Session()
        retry_count = _parse_positive_int(getattr(settings, "RENAPER_RETRIES", 0), 0)
        retries = Retry(
            total=retry_count,
            connect=retry_count,
            read=retry_count,
            backoff_factor=0.8,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST"]),
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def login(self):
        try:
            response = self.session.post(
                self.login_url, json={"username": self.username, "password": self.password}, timeout=self.timeout
            )
        except ConnectionError:
            raise Exception("Error de conexión con el servicio.")
        except RequestException as e:
            raise Exception(f"No se pudo conectar al servicio de login: {str(e)}")

        if response.status_code != 200:
            raise Exception(f"Login fallido: {response.status_code} {response.text}")

        data = response.json()
        self.token = data.get("token")
        self.token_expiration = datetime.datetime.fromisoformat(
            data["expiration"].replace("Z", "+00:00")
        )

    def get_token(self):
        if (
            not self.token
            or datetime.datetime.now(datetime.timezone.utc) >= self.token_expiration
        ):
            self.login()
        return self.token

    def consultar_ciudadano(self, dni, sexo):
        try:
            token = self.get_token()
        except Exception:
            logger.exception("Error al obtener token RENAPER")
            return {"success": False, "error": "Error interno al obtener token"}

        headers = {"Authorization": f"Bearer {token}"}
        params = {"dni": dni, "sexo": _normalizar_sexo(sexo)}

        try:
            response = self.session.get(
                self.consulta_url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
        except ConnectionError:
            return {"success": False, "error": "Error de conexión al servicio."}
        except RequestException:
            logger.exception("RequestException al conectar con RENAPER")
            return {
                "success": False,
                "error": "Error interno de conexión al servicio.",
            }

        if response.status_code != 200:
            try:
                error_data = response.json()
            except Exception:
                error_data = (
                    response.text[:500]
                    if hasattr(response, "text")
                    else "Sin contenido"
                )
            return {
                "success": False,
                "error": f"Error HTTP {response.status_code}: Error en la respuesta del servicio.",
                "status_code": response.status_code,
                "raw_response": error_data,
            }

        try:
            data = response.json()
        except Exception:
            logger.exception("Respuesta RENAPER no es JSON válido")
            raw_text = (
                response.text[:500] if hasattr(response, "text") else "No response text"
            )
            return {
                "success": False,
                "error": "Error interno: respuesta no es JSON válido.",
                "raw_response": raw_text,
            }

        if not data.get("isSuccess", False):
            return {
                "success": False,
                "error": "Respuesta de Renaper no indica éxito.",
                "raw_response": data,
            }

        return {"success": True, "data": data["result"]}


def normalizar(texto):
    if not texto:
        return ""
    texto = texto.lower().replace("_", " ")
    texto = (
        unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    )
    return texto.strip()


def consultar_datos_renaper(dni, sexo):
    if getattr(settings, "RENAPER_TEST_MODE", False):
        # Simular delay de API real
        time.sleep(2)
        
        # Generar datos aleatorios diferentes cada vez
        nombres = ["Juan Carlos", "María Elena", "Roberto", "Ana Sofía", "Carlos Alberto", "Lucía", "Fernando", "Valentina"]
        apellidos = ["Pérez", "González", "Rodríguez", "López", "Martínez", "García", "Fernández", "Morales"]
        calles = ["Av. Corrientes", "Av. Santa Fe", "Rivadavia", "San Martín", "Belgrano", "Mitre", "9 de Julio"]
        provincias = ["Buenos Aires", "Córdoba", "Santa Fe", "Mendoza", "Tucumán"]
        
        nombre_random = random.choice(nombres)
        apellido_random = random.choice(apellidos)
        calle_random = random.choice(calles)
        numero_random = random.randint(100, 9999)
        provincia_random = random.choice(provincias)
        año_random = random.randint(1970, 2000)
        mes_random = random.randint(1, 12)
        dia_random = random.randint(1, 28)
        
        return {
            "success": True,
            "data": {
                "dni": dni,
                "nombre": nombre_random,
                "apellido": apellido_random,
                "fecha_nacimiento": f"{año_random}-{mes_random:02d}-{dia_random:02d}",
                "genero": _normalizar_sexo(sexo),
                "domicilio": f"{calle_random} {numero_random}",
                "provincia": random.randint(1, 24),
            },
            "datos_api": {
                "nombres": nombre_random,
                "apellido": apellido_random,
                "fechaNacimiento": f"{año_random}-{mes_random:02d}-{dia_random:02d}",
                "provincia": provincia_random,
                "calle": calle_random,
                "numero": str(numero_random),
            },
        }

    if not all([
        _clean_api_base(getattr(settings, "RENAPER_API_URL", None)),
        getattr(settings, "RENAPER_API_USERNAME", None),
        getattr(settings, "RENAPER_API_PASSWORD", None),
    ]):
        return {
            "success": False,
            "error": "Configuración RENAPER incompleta (URL/usuario/password).",
        }

    try:
        client = APIClient()
        response = client.consultar_ciudadano(dni, sexo)

        if not response["success"]:
            return {
                "success": False,
                "error": response.get("error", "Error al consultar RENAPER"),
                "status_code": response.get("status_code"),
                "datos_api": response.get("raw_response"),
            }

        datos = response["data"]

        if datos.get("mensaf") == "FALLECIDO":
            return {"success": False, "fallecido": True}

        EQUIVALENCIAS_PROVINCIAS = {
            "ciudad de buenos aires": "ciudad autonoma de buenos aires",
            "caba": "ciudad autonoma de buenos aires",
            "ciudad autonoma de buenos aires": "ciudad autonoma de buenos aires",
            "tierra del fuego": "tierra del fuego, antartida e islas del atlantico sur",
            "tierra del fuego antartida e islas del atlantico sur": "tierra del fuego, antartida e islas del atlantico sur",
        }

        provincia_api = datos.get("provincia", "")
        provincia_api_norm = normalizar(provincia_api)
        provincia_api_norm = EQUIVALENCIAS_PROVINCIAS.get(
            provincia_api_norm, provincia_api_norm
        )

        provincia = None
        for prov in Provincia.objects.all():
            nombre_norm = normalizar(prov.nombre)
            if provincia_api_norm == nombre_norm:
                provincia = prov
                break

        genero = _normalizar_sexo(sexo)
        datos_mapeados = {
            "dni": dni,
            "nombre": datos.get("nombres"),
            "apellido": datos.get("apellido"),
            "fecha_nacimiento": datos.get("fechaNacimiento"),
            "genero": genero if genero in ("M", "F", "X") else "X",
            "domicilio": f"{datos.get('calle', '')} {datos.get('numero', '')} {datos.get('piso', '')} {datos.get('departamento', '')}".strip(),
            "provincia": provincia.pk if provincia else None,
        }

        return {"success": True, "data": datos_mapeados, "datos_api": datos}

    except Exception:
        logger.exception("Error inesperado en consultar_datos_renaper")
        return {
            "success": False,
            "error": "Error interno inesperado al consultar Renaper",
        }
