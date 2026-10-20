from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
import bcrypt
import jwt

from src.core.config import settings


def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro para la contraseña utilizando bcrypt.
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash almacenado.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict] = None,
) -> str:
    """
    Crea un token JWT firmado con claims y tiempo de expiración.
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida la firma y expiración de un token JWT.
    Retorna el payload decodificado o None si es inválido.
    """
    try:
        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return decoded
    except (jwt.PyJWTError, Exception):
        return None
