from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.core.deps import get_current_active_user
from src.core.security import create_access_token, get_password_hash, verify_password
from src.db.session import get_session
from src.models.emprendedor import Emprendedor
from src.models.plan import Plan
from src.models.rubro import Rubro
from src.models.usuario import Usuario
from src.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario (Cliente o Emprendedor)",
)
def register(
    register_in: RegisterRequest,
    session: Session = Depends(get_session),
) -> TokenResponse:
    """
    Registra una nueva cuenta.
    Permite registrarse directamente como 'cliente' o como 'emprendedor'.
    Si se registra como emprendedor, se inicializa su perfil de puesto.
    """
    # 1. Verificar si el email ya existe
    existing_user = session.exec(select(Usuario).where(Usuario.email == register_in.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario registrado con este correo electrónico",
        )

    # 2. Validar rol solicitado (por seguridad el registro público no permite autoproclamarse admin)
    rol = register_in.rol.lower().strip()
    if rol not in ["cliente", "emprendedor"]:
        rol = "cliente"

    # 3. Crear el usuario
    nuevo_usuario = Usuario(
        email=register_in.email,
        password_hash=get_password_hash(register_in.password),
        nombre_completo=register_in.nombre_completo,
        rol=rol,
        activo=True,
    )
    session.add(nuevo_usuario)
    session.commit()
    session.refresh(nuevo_usuario)

    # 4. Si es emprendedor, crear su perfil comercial inicial
    if rol == "emprendedor":
        # Asegurar plan base por defecto (ID 1 o primer plan activo)
        plan_base = session.exec(select(Plan).where(Plan.activo == True)).first()
        if not plan_base:
            plan_base = Plan(
                nombre="Gratuito",
                limite_productos=5,
                precio_mensual=0.0,
                permite_destacados=False,
                descripcion="Plan inicial con hasta 5 productos",
            )
            session.add(plan_base)
            session.commit()
            session.refresh(plan_base)

        # Asegurar rubro inicial
        rubro_id = register_in.rubro_id
        if not rubro_id:
            rubro_base = session.exec(select(Rubro).where(Rubro.activo == True)).first()
            if not rubro_base:
                rubro_base = Rubro(nombre="General", descripcion="Rubro general de emprendimientos")
                session.add(rubro_base)
                session.commit()
                session.refresh(rubro_base)
            rubro_id = rubro_base.id

        perfil_emprendedor = Emprendedor(
            usuario_id=nuevo_usuario.id,
            nombre_fantasia=register_in.nombre_fantasia or nuevo_usuario.nombre_completo,
            telefono_whatsapp=register_in.telefono_whatsapp or "",
            rubro_id=rubro_id,
            feria_id=register_in.feria_id,
            plan_id=plan_base.id,
            activo=True,
        )
        session.add(perfil_emprendedor)
        session.commit()

    # 5. Generar token JWT de acceso
    access_token = create_access_token(
        subject=nuevo_usuario.id,
        extra_claims={"rol": nuevo_usuario.rol, "email": nuevo_usuario.email},
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        rol=nuevo_usuario.rol,
        usuario_id=nuevo_usuario.id,
        nombre_completo=nuevo_usuario.nombre_completo,
    )


from fastapi.security import OAuth2PasswordRequestForm


def _authenticate_and_create_token(
    email: str,
    password: str,
    session: Session,
) -> TokenResponse:
    statement = select(Usuario).where(Usuario.email == email)
    user = session.exec(statement).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo en el sistema",
        )

    access_token = create_access_token(
        subject=user.id,
        extra_claims={"rol": user.rol, "email": user.email},
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        rol=user.rol,
        usuario_id=user.id,
        nombre_completo=user.nombre_completo,
    )


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Obtener token JWT vía formulario OAuth2 (Compatible con botón Authorize de Swagger)",
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> TokenResponse:
    """
    Endpoint OAuth2 estándar para Swagger UI. Permite usar el botón 'Authorize'
    ingresando el email en 'username' y la contraseña en 'password'.
    """
    return _authenticate_and_create_token(
        email=form_data.username,
        password=form_data.password,
        session=session,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión con JSON y obtener JWT",
)
def login(
    login_in: LoginRequest,
    session: Session = Depends(get_session),
) -> TokenResponse:
    """
    Autentica credenciales enviadas como JSON (para consumo desde React, Postman o clientes REST).
    """
    return _authenticate_and_create_token(
        email=login_in.email,
        password=login_in.password,
        session=session,
    )


@router.get(
    "/me",
    response_model=Dict[str, Any],
    summary="Consultar datos del usuario autenticado",
)
def get_me(
    current_user: Usuario = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    """
    Retorna el perfil del usuario autenticado y su perfil de emprendedor (si aplica).
    """
    response_data: Dict[str, Any] = {
        "id": current_user.id,
        "email": current_user.email,
        "nombre_completo": current_user.nombre_completo,
        "rol": current_user.rol,
        "activo": current_user.activo,
        "created_at": current_user.created_at,
        "emprendedor": None,
    }

    if current_user.rol in ["emprendedor", "admin"]:
        statement = select(Emprendedor).where(Emprendedor.usuario_id == current_user.id)
        emprendedor = session.exec(statement).first()
        if emprendedor:
            response_data["emprendedor"] = emprendedor.model_dump()

    return response_data
