"""
endpoints de operaciones.

proporciona:
- GET /: listar operaciones de un portfolio con filtros
- POST /: crear nueva operacion (buy/sell)
- GET /{operation_id}: obtener detalle de operacion
- PUT /{operation_id}: actualizar operacion (solo notas y fecha)
- GET /stats/{portfolio_id}: estadisticas del portfolio

todos los endpoints requieren autenticacion y validan ownership del portfolio.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.middleware.dependencies import get_db, get_current_active_user
from app.services.portfolio_service import PortfolioService
from app.services.operation_service import OperationService
from app.schemas.operation import (
    OperationCreate,
    OperationUpdate,
    OperationResponse
)
from app.models.user import User
from app.models.operation import OperationType


router = APIRouter(prefix="/operations", tags=["Operaciones"])


def _verify_portfolio_ownership(portfolio_service: PortfolioService, 
                                  portfolio_id: UUID, 
                                  user_id: UUID) -> None:
    """verifica que el portfolio existe y pertenece al usuario."""
    portfolio = portfolio_service.get_portfolio(portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="portfolio no encontrado"
        )
    if portfolio.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no tienes permiso para operar en este portfolio"
        )


def _build_operation_response(operation) -> OperationResponse:
    """construye response de operacion desde modelo orm."""
    return OperationResponse(
        id=operation.id,
        portfolio_id=operation.portfolio_id,
        asset_symbol=operation.asset_symbol,
        operation_type=operation.operation_type,
        quantity=operation.quantity,
        price=operation.price,
        fees=operation.fees,
        total_amount=operation.total_amount,
        operation_date=operation.operation_date,
        notes=operation.notes,
        created_at=operation.created_at,
        updated_at=operation.updated_at
    )


@router.get("/", response_model=List[OperationResponse])
def list_operations(
    portfolio_id: UUID,
    asset_symbol: Optional[str] = Query(None, description="Filtrar por símbolo"),
    operation_type: Optional[OperationType] = Query(None, description="Filtrar por tipo (BUY/SELL)"),
    date_from: Optional[date] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    lista operaciones de un portfolio con filtros opcionales.
    
    **filtros disponibles:**
    - asset_symbol: filtrar por activo
    - operation_type: BUY o SELL
    - date_from/date_to: rango de fechas
    
    **paginacion:**
    - skip: registros a saltar
    - limit: maximo de registros (max 500)
    
    ordenado por fecha descendente (mas recientes primero).
    """
    portfolio_service = PortfolioService(db)
    operation_service = OperationService(db)
    
    # verificar ownership
    _verify_portfolio_ownership(portfolio_service, portfolio_id, current_user.id)
    
    # filtrar operaciones
    operations = operation_service.filter_operations(
        portfolio_id=portfolio_id,
        asset_symbol=asset_symbol,
        operation_type=operation_type,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit
    )
    
    return [_build_operation_response(op) for op in operations]


@router.post("/", response_model=OperationResponse, status_code=status.HTTP_201_CREATED)
def create_operation(
    operation_data: OperationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    crea una nueva operacion de compra o venta.
    
    **para BUY:**
    - crea o actualiza la posicion del activo
    - calcula precio promedio ponderado
    
    **para SELL:**
    - valida que haya cantidad suficiente
    - reduce la posicion
    - mantiene el precio promedio
    
    **calculo de total_amount:**
    - BUY: quantity × price + fees
    - SELL: quantity × price - fees
    """
    portfolio_service = PortfolioService(db)
    
    # verificar ownership
    _verify_portfolio_ownership(portfolio_service, operation_data.portfolio_id, current_user.id)
    
    try:
        operation = portfolio_service.add_operation(
            portfolio_id=operation_data.portfolio_id,
            asset_symbol=operation_data.asset_symbol,
            operation_type=operation_data.operation_type,
            quantity=operation_data.quantity,
            price=operation_data.price,
            fees=operation_data.fees,
            notes=operation_data.notes
        )
        return _build_operation_response(operation)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/stats/{portfolio_id}")
def get_portfolio_statistics(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    obtiene estadisticas de operaciones del portfolio.
    
    **incluye:**
    - total_operations: numero total
    - total_buys/total_sells: conteo por tipo
    - total_invested: suma de compras
    - total_withdrawn: suma de ventas
    - total_fees: comisiones pagadas
    - unique_assets: numero de activos distintos
    """
    portfolio_service = PortfolioService(db)
    operation_service = OperationService(db)
    
    # verificar ownership
    _verify_portfolio_ownership(portfolio_service, portfolio_id, current_user.id)
    
    stats = operation_service.get_portfolio_statistics(portfolio_id)
    
    # convertir decimals a strings para json
    return {
        "total_operations": stats["total_operations"],
        "total_buys": stats["total_buys"],
        "total_sells": stats["total_sells"],
        "total_invested": str(stats["total_invested"]),
        "total_withdrawn": str(stats["total_withdrawn"]),
        "total_fees": str(stats["total_fees"]),
        "unique_assets": stats["unique_assets"]
    }


@router.get("/{operation_id}", response_model=OperationResponse)
def get_operation(
    operation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    obtiene detalle de una operacion especifica.
    
    valida que la operacion pertenezca a un portfolio del usuario.
    """
    portfolio_service = PortfolioService(db)
    operation_service = OperationService(db)
    
    operation = operation_service.get_operation(operation_id)
    
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="operacion no encontrada"
        )
    
    # verificar ownership del portfolio
    _verify_portfolio_ownership(portfolio_service, operation.portfolio_id, current_user.id)
    
    return _build_operation_response(operation)


@router.put("/{operation_id}", response_model=OperationResponse)
def update_operation(
    operation_id: UUID,
    update_data: OperationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    actualiza una operacion existente.
    
    **solo se puede actualizar:**
    - notes: notas de la operacion
    - operation_date: fecha de la operacion
    
    los valores financieros (quantity, price, fees) son inmutables
    para mantener la integridad del historial.
    """
    portfolio_service = PortfolioService(db)
    operation_service = OperationService(db)
    
    operation = operation_service.get_operation(operation_id)
    
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="operacion no encontrada"
        )
    
    # verificar ownership
    _verify_portfolio_ownership(portfolio_service, operation.portfolio_id, current_user.id)
    
    # actualizar solo notas (por ahora)
    if update_data.notes is not None:
        updated = operation_service.update_operation_notes(operation_id, update_data.notes)
        return _build_operation_response(updated)
    
    return _build_operation_response(operation)

