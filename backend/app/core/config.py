from pathlib import Path
import os
import logging
import sys

ROOT_DIR = Path(__file__).resolve().parents[3]

# Load .env files before Settings is instantiated
try:
    from dotenv import load_dotenv
    _env_name = os.environ.get("ENV") or os.environ.get("HELIOS_ENV") or "development"
    for _path in [ROOT_DIR / f".env.{_env_name}", ROOT_DIR / ".env"]:
        try:
            if _path.exists():
                load_dotenv(str(_path))
                break
        except Exception:
            pass
except ImportError:
    pass

logger = logging.getLogger(__name__)

# ── Pydantic v1 / v2 compatibility ───────────────────────────────────────────
try:
    # pydantic-settings v2 (pydantic >= 2.0)
    from pydantic_settings import BaseSettings
    from pydantic import field_validator, model_validator
    _PYDANTIC_V2 = True
except ImportError:
    # pydantic v1 (pydantic < 2.0) — BaseSettings is in pydantic directly
    from pydantic import BaseSettings  # type: ignore[no-redef]
    _PYDANTIC_V2 = False

# ── Settings ─────────────────────────────────────────────────────────────────

class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: str = ""
    REDIS_URL: str = ""
    JWT_SECRET: str = ""
    API_V1_STR: str = "/api/v1"
    CORS_ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    if _PYDANTIC_V2:
        model_config = {"env_file_encoding": "utf-8", "case_sensitive": True}

        @field_validator("DATABASE_URL", mode="before")
        @classmethod
        def _set_default_database_url(cls, v):
            if v:
                return v
            db_path = ROOT_DIR / "data" / "helios.db"
            try:
                db_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
            return f"sqlite:///{db_path}"

        @field_validator("JWT_SECRET", mode="before")
        @classmethod
        def _ensure_jwt_secret(cls, v):
            if v:
                return v
            env_override = os.environ.get("HELIOS_JWT_SECRET")
            if env_override:
                return env_override
            logger.warning("JWT_SECRET not set; using insecure dev default.")
            return "dev_jwt_secret_change_me"

        @field_validator("CORS_ALLOWED_ORIGINS", mode="before")
        @classmethod
        def _assemble_cors(cls, v):
            if isinstance(v, str):
                return [s.strip() for s in v.split(",") if s.strip()] if v else []
            return list(v) if isinstance(v, (list, tuple)) else v
    else:
        # pydantic v1 validators
        class Config:
            env_file_encoding = "utf-8"
            case_sensitive = True

        try:
            from pydantic import validator as _validator

            @_validator("DATABASE_URL", pre=True, always=True)
            @classmethod
            def _set_default_database_url(cls, v):
                if v:
                    return v
                db_path = ROOT_DIR / "data" / "helios.db"
                try:
                    db_path.parent.mkdir(parents=True, exist_ok=True)
                except Exception:
                    pass
                return f"sqlite:///{db_path}"

            @_validator("JWT_SECRET", pre=True, always=True)
            @classmethod
            def _ensure_jwt_secret(cls, v):
                if v:
                    return v
                env_override = os.environ.get("HELIOS_JWT_SECRET")
                if env_override:
                    return env_override
                logger.warning("JWT_SECRET not set; using insecure dev default.")
                return "dev_jwt_secret_change_me"

            @_validator("CORS_ALLOWED_ORIGINS", pre=True)
            @classmethod
            def _assemble_cors(cls, v):
                if isinstance(v, str):
                    return [s.strip() for s in v.split(",") if s.strip()] if v else []
                return list(v) if isinstance(v, (list, tuple)) else v
        except Exception:
            pass


def _fail_startup(message: str) -> None:
    try:
        logging.getLogger("helios.startup").critical("%s", message)
    except Exception:
        print(message, file=sys.stderr)
    raise SystemExit(1)


def _validate_settings(s: Settings) -> None:
    env = (s.ENV or "").lower()
    if env == "production":
        errors = []
        db = (s.DATABASE_URL or "").strip()
        if not db:
            errors.append("DATABASE_URL must be set in production")
        elif db.startswith("sqlite"):
            errors.append("DATABASE_URL must not be sqlite in production")
        secret = s.JWT_SECRET or ""
        if not secret or secret == "dev_jwt_secret_change_me":
            errors.append("JWT_SECRET must be a strong secret in production")
        elif len(secret) < 16:
            errors.append("JWT_SECRET should be at least 16 characters")
        if errors:
            _fail_startup("Invalid configuration:\n- " + "\n- ".join(errors))


settings = Settings()
try:
    _validate_settings(settings)
except SystemExit:
    raise
except Exception as exc:
    _fail_startup(f"Configuration validation failed: {exc}")
