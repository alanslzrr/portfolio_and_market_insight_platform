"""
schemas pydantic (dtos) para validacion de requests/responses.

este paquete contiene todos los schemas para:
- validacion de entrada (requests)
- serializacion de salida (responses)
- documentacion automatica de la api (openapi)

estructura:
- auth.py: registro, login, tokens
- user.py: perfil de usuario
- portfolio.py: carteras y posiciones
- operation.py: operaciones de compra/venta
- market.py: datos de mercado
- analysis.py: analisis con ia
"""
# schemas de autenticacion
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    PasswordReset,
    EmailVerification
)

# schemas de usuario
from app.schemas.user import (
    UserProfileData,
    UserResponse,
    UserProfileResponse,
    UserUpdate,
    PasswordChange
)

# schemas de portfolio
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioAssetResponse,
    PortfolioResponse,
    PortfolioDetailResponse
)

# schemas de operaciones
from app.schemas.operation import (
    OperationCreate,
    OperationUpdate,
    OperationResponse,
    OperationFilter
)

# schemas de mercado
from app.schemas.market import (
    AssetInfo,
    PricePoint,
    CurrentPriceResponse,
    HistoricalPriceResponse,
    AssetSearchResult
)

# schemas de analisis
from app.schemas.analysis import (
    TechnicalIndicators,
    AnalysisRequest,
    AnalysisResponse,
    AnalysisRequestStatus
)

__all__ = [
    # Auth
    "UserRegister",
    "UserLogin",
    "TokenResponse",
    "RefreshTokenRequest",
    "PasswordReset",
    "EmailVerification",
    # User
    "UserProfileData",
    "UserResponse",
    "UserProfileResponse",
    "UserUpdate",
    "PasswordChange",
    # Portfolio
    "PortfolioCreate",
    "PortfolioUpdate",
    "PortfolioAssetResponse",
    "PortfolioResponse",
    "PortfolioDetailResponse",
    # Operation
    "OperationCreate",
    "OperationUpdate",
    "OperationResponse",
    "OperationFilter",
    # Market
    "AssetInfo",
    "PricePoint",
    "CurrentPriceResponse",
    "HistoricalPriceResponse",
    "AssetSearchResult",
    # Analysis
    "TechnicalIndicators",
    "AnalysisRequest",
    "AnalysisResponse",
    "AnalysisRequestStatus",
]
