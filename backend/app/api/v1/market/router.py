"""
endpoints de datos de mercado.

proporciona:
- GET /assets/search: buscar activos por simbolo o nombre
- GET /assets/{symbol}: obtener informacion de un activo
- GET /prices/{symbol}/current: obtener precio actual
- GET /prices/{symbol}/historical: obtener precios historicos

estos endpoints son publicos y no requieren autenticacion.
datos obtenidos desde alpha vantage api con cache en base de datos local.
"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.middleware.dependencies import get_db, get_optional_user
from app.repositories.asset import AssetRepository
from app.services.market_service import MarketDataService
from app.schemas.market import (
    AssetInfo,
    AssetSearchResult,
    CurrentPriceResponse,
    HistoricalPriceResponse,
    PricePoint
)
from app.models.user import User
from app.models.asset import AssetType


router = APIRouter(prefix="/market", tags=["Mercado"])


# ------------ // ------------
# ENDPOINTS DE ACTIVOS
# ------------ // ------------

@router.get("/assets/search", response_model=List[AssetSearchResult])
def search_assets(
    q: str = Query(..., min_length=1, max_length=50, description="Término de búsqueda"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de resultados"),
    db: Session = Depends(get_db)
):
    """
    busca activos por simbolo o nombre.
    
    busca primero en catalogo local, luego en alpha vantage si no hay resultados.
    
    **parametros:**
    - q: termino de busqueda (minimo 1 caracter)
    - limit: maximo de resultados a retornar (default 20, max 100)
    
    **returns:**
    - lista de activos que coinciden con la busqueda
    """
    market_service = MarketDataService(db)
    results = market_service.search_assets(q)
    
    # limitar resultados
    results = results[:limit]
    
    return [
        AssetSearchResult(
            symbol=result["symbol"],
            name=result["name"],
            asset_type=result["type"],
            currency=result.get("currency", "USD")
        )
        for result in results
    ]


@router.get("/assets/{symbol}", response_model=AssetInfo)
def get_asset_info(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    obtiene informacion detallada de un activo por su simbolo.
    
    retorna:
    - simbolo y nombre
    - tipo de activo (STOCK, ETF, CRYPTO)
    - moneda y exchange
    - descripcion
    
    **ejemplo:**
    ```
    GET /api/v1/market/assets/AAPL
    ```
    """
    asset_repo = AssetRepository(db)
    asset = asset_repo.get_by_symbol(symbol.upper())
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"activo '{symbol}' no encontrado en catalogo local. usa /search para buscar en alpha vantage"
        )
    
    return AssetInfo(
        symbol=asset.symbol,
        name=asset.name,
        asset_type=asset.asset_type,
        currency=asset.currency,
        exchange=asset.exchange,
        description=asset.description
    )


# ------------ // ------------
# ENDPOINTS DE PRECIOS
# ------------ // ------------

@router.get("/prices/{symbol}/current", response_model=CurrentPriceResponse)
def get_current_price(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    obtiene el precio actual de un activo.
    
    consulta alpha vantage para precio en tiempo real.
    resultado se cachea por 5 minutos.
    
    **ejemplo:**
    ```
    GET /api/v1/market/prices/AAPL/current
    ```
    """
    market_service = MarketDataService(db)
    
    price = market_service.get_current_price(symbol)
    
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no se pudo obtener precio para '{symbol}'. verifica que el simbolo sea valido y que alpha vantage este configurado"
        )
    
    return CurrentPriceResponse(
        symbol=symbol.upper(),
        price=price,
        timestamp=datetime.utcnow(),
        currency="USD"
    )


@router.get("/prices/{symbol}/historical", response_model=HistoricalPriceResponse)
def get_historical_prices(
    symbol: str,
    days: int = Query(30, ge=1, le=100, description="Número de días de histórico"),
    db: Session = Depends(get_db)
):
    """
    obtiene precios historicos de un activo.
    
    consulta alpha vantage y cachea resultados.
    retorna datos ohlcv (open, high, low, close, volume).
    
    **parametros:**
    - symbol: simbolo del activo
    - days: numero de dias de historico (default 30, max 100)
    
    **ejemplo:**
    ```
    GET /api/v1/market/prices/AAPL/historical?days=30
    ```
    """
    market_service = MarketDataService(db)
    asset_repo = AssetRepository(db)
    
    # verificar que el activo existe
    asset = asset_repo.get_by_symbol(symbol.upper())
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"activo '{symbol}' no encontrado"
        )
    
    price_history = market_service.get_historical_prices(symbol, days)
    
    if not price_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no se pudieron obtener datos historicos para '{symbol}'"
        )
    
    # construir lista de price points
    price_points = [
        PricePoint(
            timestamp=datetime.strptime(p["date"], "%Y-%m-%d"),
            open_price=Decimal(str(p["open"])),
            high_price=Decimal(str(p["high"])),
            low_price=Decimal(str(p["low"])),
            close_price=Decimal(str(p["close"])),
            volume=p["volume"]
        )
        for p in price_history
    ]
    
    return HistoricalPriceResponse(
        symbol=symbol.upper(),
        currency="USD",
        prices=price_points
    )


# ------------ // ------------
# ENDPOINT PARA CREAR ACTIVOS (ADMIN/INTERNO)
# ------------ // ------------

@router.post("/assets", response_model=AssetInfo, status_code=status.HTTP_201_CREATED)
def create_asset(
    symbol: str = Query(..., min_length=1, max_length=20, description="Símbolo del activo"),
    name: str = Query(..., min_length=1, max_length=255, description="Nombre del activo"),
    asset_type: AssetType = Query(..., description="Tipo de activo"),
    currency: str = Query("USD", min_length=3, max_length=3, description="Moneda (ISO 4217)"),
    exchange: Optional[str] = Query(None, description="Exchange/bolsa"),
    description: Optional[str] = Query(None, description="Descripción"),
    db: Session = Depends(get_db)
):
    """
    crea un nuevo activo en el catalogo.
    
    este endpoint es util para:
    - agregar activos manualmente al sistema
    - poblar el catalogo inicial
    
    **nota:** en uso normal, los activos se crean automaticamente
    cuando un usuario registra una operacion con un simbolo nuevo.
    
    **validaciones:**
    - el simbolo debe ser unico
    - el simbolo se convierte a mayusculas automaticamente
    """
    asset_repo = AssetRepository(db)
    
    # verificar que no existe
    existing = asset_repo.get_by_symbol(symbol.upper())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"el activo '{symbol}' ya existe"
        )
    
    # crear activo
    from app.models.asset import Asset
    asset = Asset(
        symbol=symbol.upper(),
        name=name,
        asset_type=asset_type,
        currency=currency.upper(),
        exchange=exchange,
        description=description
    )
    
    db.add(asset)
    db.commit()
    db.refresh(asset)
    
    return AssetInfo(
        symbol=asset.symbol,
        name=asset.name,
        asset_type=asset.asset_type,
        currency=asset.currency,
        exchange=asset.exchange,
        description=asset.description
    )
