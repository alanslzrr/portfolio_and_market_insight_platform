"""
endpoints de portfolios.

proporciona:
- GET /: listar portfolios del usuario
- POST /: crear nuevo portfolio
- GET /{portfolio_id}: obtener portfolio con posiciones
- PUT /{portfolio_id}: actualizar portfolio
- DELETE /{portfolio_id}: eliminar portfolio

todos los endpoints requieren autenticacion y validan ownership.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.middleware.dependencies import get_db, get_current_active_user
from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
    PortfolioDetailResponse,
    PortfolioAssetResponse
)
from app.models.user import User
from decimal import Decimal


router = APIRouter(prefix="/portfolios", tags=["Portfolios"])


def _build_portfolio_response(portfolio) -> PortfolioResponse:
    """construye response de portfolio desde modelo orm."""
    return PortfolioResponse(
        id=portfolio.id,
        user_id=portfolio.user_id,
        name=portfolio.name,
        description=portfolio.description,
        base_currency=portfolio.base_currency,
        total_value=portfolio.total_value or Decimal("0"),
        total_cost=portfolio.total_cost or Decimal("0"),
        total_gain_loss=portfolio.total_gain_loss or Decimal("0"),
        total_gain_loss_percent=portfolio.total_gain_loss_percent or Decimal("0"),
        created_at=portfolio.created_at,
        updated_at=portfolio.updated_at
    )


def _build_portfolio_detail_response(portfolio) -> PortfolioDetailResponse:
    """construye response detallada de portfolio con posiciones."""
    assets = []
    
    for asset in portfolio.assets:
        position_value = asset.quantity * asset.current_price
        cost_basis = asset.quantity * asset.average_price
        gain_loss = position_value - cost_basis
        gain_loss_percent = (gain_loss / cost_basis * 100) if cost_basis > 0 else Decimal("0")
        
        assets.append(PortfolioAssetResponse(
            id=asset.id,
            asset_symbol=asset.asset_symbol,
            quantity=asset.quantity,
            average_price=asset.average_price,
            current_price=asset.current_price,
            position_value=position_value,
            gain_loss=gain_loss,
            gain_loss_percent=gain_loss_percent,
            updated_at=asset.updated_at
        ))
    
    return PortfolioDetailResponse(
        id=portfolio.id,
        user_id=portfolio.user_id,
        name=portfolio.name,
        description=portfolio.description,
        base_currency=portfolio.base_currency,
        total_value=portfolio.total_value or Decimal("0"),
        total_cost=portfolio.total_cost or Decimal("0"),
        total_gain_loss=portfolio.total_gain_loss or Decimal("0"),
        total_gain_loss_percent=portfolio.total_gain_loss_percent or Decimal("0"),
        created_at=portfolio.created_at,
        updated_at=portfolio.updated_at,
        assets=assets
    )


@router.get("/", response_model=List[PortfolioResponse])
def list_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    lista todos los portfolios del usuario autenticado.
    
    retorna lista de portfolios con metricas agregadas.
    no incluye posiciones individuales (usar GET /{id} para detalle).
    """
    portfolio_service = PortfolioService(db)
    portfolios = portfolio_service.list_user_portfolios(current_user.id)
    
    return [_build_portfolio_response(p) for p in portfolios]


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    portfolio_data: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    crea un nuevo portfolio para el usuario autenticado.
    
    **validaciones:**
    - nombre debe ser unico para el usuario
    - moneda debe ser codigo iso 4217 de 3 letras
    
    **returns:**
    - portfolio creado con id asignado
    """
    portfolio_service = PortfolioService(db)
    
    try:
        portfolio = portfolio_service.create_portfolio(
            user_id=current_user.id,
            name=portfolio_data.name,
            description=portfolio_data.description,
            base_currency=portfolio_data.base_currency
        )
        return _build_portfolio_response(portfolio)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/{portfolio_id}", response_model=PortfolioDetailResponse)
def get_portfolio(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    obtiene un portfolio con todas sus posiciones.
    
    incluye:
    - datos del portfolio
    - metricas agregadas
    - lista de posiciones con metricas individuales
    
    **validaciones:**
    - portfolio debe existir
    - portfolio debe pertenecer al usuario autenticado
    """
    portfolio_service = PortfolioService(db)
    portfolio = portfolio_service.get_portfolio(portfolio_id)
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="portfolio no encontrado"
        )
    
    # verificar ownership
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no tienes permiso para ver este portfolio"
        )
    
    return _build_portfolio_detail_response(portfolio)


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(
    portfolio_id: UUID,
    update_data: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    actualiza un portfolio existente.
    
    solo se actualizan los campos enviados (semantica PATCH).
    
    **campos actualizables:**
    - name: nombre del portfolio
    - description: descripcion
    - base_currency: moneda base
    
    **validaciones:**
    - portfolio debe existir y pertenecer al usuario
    """
    portfolio_service = PortfolioService(db)
    
    # verificar existencia y ownership
    portfolio = portfolio_service.get_portfolio(portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="portfolio no encontrado"
        )
    
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no tienes permiso para modificar este portfolio"
        )
    
    # actualizar
    updated = portfolio_service.update_portfolio(
        portfolio_id=portfolio_id,
        name=update_data.name,
        description=update_data.description
    )
    
    return _build_portfolio_response(updated)


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    elimina un portfolio y todas sus posiciones y operaciones.
    
    **advertencia:** esta accion es irreversible.
    
    **validaciones:**
    - portfolio debe existir y pertenecer al usuario
    """
    portfolio_service = PortfolioService(db)
    
    # verificar existencia y ownership
    portfolio = portfolio_service.get_portfolio(portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="portfolio no encontrado"
        )
    
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no tienes permiso para eliminar este portfolio"
        )
    
    portfolio_service.delete_portfolio(portfolio_id)
    return None

