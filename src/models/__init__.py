from src.models.usuario import (
    Usuario,
    UsuarioBase,
    UsuarioPublic,
    UsuarioPublicNested,
    UsuarioCreate,
    UsuarioUpdate,
)
from src.models.rubro import (
    Rubro,
    RubroBase,
    RubroPublic,
    RubroPublicNested,
    RubroCreate,
    RubroUpdate,
)
from src.models.categoria import (
    Categoria,
    CategoriaBase,
    CategoriaPublic,
    CategoriaPublicNested,
    CategoriaCreate,
    CategoriaUpdate,
)
from src.models.feria import (
    Feria,
    FeriaBase,
    FeriaPublic,
    FeriaPublicNested,
    FeriaCreate,
    FeriaUpdate,
)
from src.models.contacto import (
    Contacto,
    ContactoBase,
    ContactoPublic,
    ContactoCreate,
    ContactoUpdate,
)
from src.models.emprendedor import (
    Emprendedor,
    EmprendedorBase,
    EmprendedorPublic,
    EmprendedorPublicNested,
    EmprendedorCreate,
    EmprendedorUpdate,
)
from src.models.producto import (
    Producto,
    ProductoBase,
    ProductoPublic,
    ProductoPublicNested,
    ProductoCreate,
    ProductoUpdate,
)

# Namespace común para resolver modelos anidados recíprocos
_types_namespace = {
    "Usuario": Usuario,
    "UsuarioPublic": UsuarioPublic,
    "UsuarioPublicNested": UsuarioPublicNested,
    "Rubro": Rubro,
    "RubroPublic": RubroPublic,
    "RubroPublicNested": RubroPublicNested,
    "Categoria": Categoria,
    "CategoriaPublic": CategoriaPublic,
    "CategoriaPublicNested": CategoriaPublicNested,
    "Feria": Feria,
    "FeriaPublic": FeriaPublic,
    "FeriaPublicNested": FeriaPublicNested,
    "Contacto": Contacto,
    "ContactoPublic": ContactoPublic,
    "Emprendedor": Emprendedor,
    "EmprendedorPublic": EmprendedorPublic,
    "EmprendedorPublicNested": EmprendedorPublicNested,
    "Producto": Producto,
    "ProductoPublic": ProductoPublic,
    "ProductoPublicNested": ProductoPublicNested,
}

UsuarioPublicNested.model_rebuild(_types_namespace=_types_namespace)
CategoriaPublicNested.model_rebuild(_types_namespace=_types_namespace)
RubroPublicNested.model_rebuild(_types_namespace=_types_namespace)
FeriaPublicNested.model_rebuild(_types_namespace=_types_namespace)
EmprendedorPublicNested.model_rebuild(_types_namespace=_types_namespace)
ProductoPublicNested.model_rebuild(_types_namespace=_types_namespace)

__all__ = [
    "Usuario",
    "UsuarioBase",
    "UsuarioPublic",
    "UsuarioPublicNested",
    "UsuarioCreate",
    "UsuarioUpdate",
    "Rubro",
    "RubroBase",
    "RubroPublic",
    "RubroPublicNested",
    "RubroCreate",
    "RubroUpdate",
    "Categoria",
    "CategoriaBase",
    "CategoriaPublic",
    "CategoriaPublicNested",
    "CategoriaCreate",
    "CategoriaUpdate",
    "Feria",
    "FeriaBase",
    "FeriaPublic",
    "FeriaPublicNested",
    "FeriaCreate",
    "FeriaUpdate",
    "Contacto",
    "ContactoBase",
    "ContactoPublic",
    "ContactoCreate",
    "ContactoUpdate",
    "Emprendedor",
    "EmprendedorBase",
    "EmprendedorPublic",
    "EmprendedorPublicNested",
    "EmprendedorCreate",
    "EmprendedorUpdate",
    "Producto",
    "ProductoBase",
    "ProductoPublic",
    "ProductoPublicNested",
    "ProductoCreate",
    "ProductoUpdate",
]

