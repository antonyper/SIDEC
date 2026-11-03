from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

# Valores de ejemplo de .env.example: si llegan a producción, cualquiera puede
# firmar tokens válidos. Se rechazan al arrancar en vez de aceptarlos en silencio.
SECRET_KEYS_DE_EJEMPLO = {"cambia-esta-clave", "cambia-esta-clave-en-produccion"}


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str

    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str = ""

    DATABASE_ECHO: bool = False

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12

    # Prefijo con el que el proxy publica la API (p. ej. "/api"). Solo afecta a
    # las URLs que genera FastAPI, como la de openapi.json que usa Swagger.
    API_ROOT_PATH: str = ""

    # Primer administrador. Se crea al arrancar solo si la tabla de usuarios está
    # vacía; después estas variables se ignoran y las cuentas se gestionan desde /usuarios.
    SIDEC_ADMIN_USERNAME: str = ""
    SIDEC_ADMIN_PASSWORD: str = ""
    SIDEC_ADMIN_NOMBRE: str = "Administrador"

    # Seed (app/services/seed_service.py). SIDEC_SEED_ADMIN_* crea un ADMIN adicional si no
    # existe (cuenta nominal para quien prueba). SIDEC_SEED_DEMO carga datos demo solo si no
    # hay agencias. Ambos son idempotentes y se ejecutan al arrancar o con `python -m app.seed`.
    SIDEC_SEED_ADMIN_USERNAME: str = ""
    SIDEC_SEED_ADMIN_PASSWORD: str = ""
    SIDEC_SEED_ADMIN_NOMBRE: str = "Administrador de pruebas"
    SIDEC_SEED_DEMO: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def validar_secret_key(cls, value: str) -> str:
        if value in SECRET_KEYS_DE_EJEMPLO or len(value) < 32:
            raise ValueError(
                "SECRET_KEY debe ser un valor propio de al menos 32 caracteres. "
                'Genera uno con: python3 -c "import secrets; print(secrets.token_urlsafe(48))"'
            )
        return value

    @property
    def database_url(self) -> URL:
        # URL.create escapa usuario y contraseña: una contraseña con @, / o : no
        # rompe la cadena de conexión.
        return URL.create(
            "postgresql+psycopg2",
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            database=self.DATABASE_NAME,
        )


settings = Settings()
