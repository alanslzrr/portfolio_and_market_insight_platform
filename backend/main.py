import warnings
warnings.filterwarnings('ignore')

from decimal import Decimal
from app.core.database import engine, Base
from app.core.database.session import SessionLocal
from app.services.user_service import UserService
from app.services.portfolio_service import PortfolioService
from app.models.operation import OperationType


def test_user_service():
    print("\n--- testing user service ---")
    
    db = SessionLocal()
    user_service = UserService(db)
    
    try:
        print("\ncreando usuarios...")
        
        user1 = user_service.create_user(
            email="juan.perez@example.com",
            password="Password123",
            full_name="Juan Perez",
            currency="USD",
            timezone="America/New_York",
            language="es"
        )
        print(f"usuario creado: {user1.email}")
        
        user2 = user_service.create_user(
            email="maria.garcia@example.com",
            password="SecurePass456",
            full_name="Maria Garcia",
            currency="EUR",
            timezone="Europe/Madrid",
            language="es"
        )
        print(f"usuario creado: {user2.email}")
        
        user3 = user_service.create_user(
            email="john.doe@example.com",
            password="MyPass789",
            full_name="John Doe",
            currency="USD",
            timezone="UTC",
            language="en"
        )
        print(f"usuario creado: {user3.email}")
        
        print("\nlistando usuarios...")
        all_users = user_service.list_all_users()
        print(f"total: {len(all_users)}")
        for user in all_users:
            print(f"  {user.full_name} ({user.email})")
        
        print(f"\nbuscando usuario: juan.perez@example.com")
        found_user = user_service.get_user_by_email("juan.perez@example.com")
        if found_user:
            print(f"encontrado: {found_user.full_name}, verificado: {found_user.is_verified}")
        
        print(f"\nactualizando perfil de {user1.email}...")
        updated = user_service.update_user_profile(
            user1.id,
            currency="EUR",
            timezone="Europe/London",
            preferences={"theme": "dark", "notifications": True}
        )
        if updated and updated.profile:
            print(f"perfil actualizado: {updated.profile.currency}, {updated.profile.timezone}")
        
        print(f"\nverificando email de {user1.email}...")
        user_service.verify_user_email(user1.id)
        verified_user = user_service.get_user_by_id(user1.id)
        print(f"verificado: {verified_user.is_verified}")
        
        print(f"\nactualizando nombre de {user2.email}...")
        user_service.update_user_info(
            user2.id,
            full_name="Maria Garcia Lopez"
        )
        print("nombre actualizado")
        
        total = user_service.count_users()
        print(f"\ntotal usuarios en sistema: {total}")
        
        print(f"\ndesactivando {user3.email}...")
        user_service.delete_user(user3.id)
        print("usuario desactivado")
        
        user1_id = user1.id
        user2_id = user2.id
        
        return user1_id, user2_id
        
    except Exception as e:
        print(f"error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def test_portfolio_service(user1_id, user2_id):
    print("\n--- testing portfolio service ---")
    
    db = SessionLocal()
    portfolio_service = PortfolioService(db)
    
    try:
        print("\ncreando portfolios...")
        
        portfolio1 = portfolio_service.create_portfolio(
            user_id=user1_id,
            name="Portfolio Conservador",
            description="Inversiones a largo plazo con bajo riesgo",
            base_currency="USD"
        )
        print(f"portfolio creado: {portfolio1.name}")
        
        portfolio2 = portfolio_service.create_portfolio(
            user_id=user1_id,
            name="Portfolio Agresivo",
            description="Trading activo y alta volatilidad",
            base_currency="USD"
        )
        print(f"portfolio creado: {portfolio2.name}")
        
        portfolio3 = portfolio_service.create_portfolio(
            user_id=user2_id,
            name="Portfolio Diversificado",
            description="Mix de activos balanceado",
            base_currency="EUR"
        )
        print(f"portfolio creado: {portfolio3.name}")
        
        print(f"\nportfolios del usuario 1:")
        user1_portfolios = portfolio_service.list_user_portfolios(user1_id)
        for p in user1_portfolios:
            print(f"  {p.name}")
        
        print("\nregistrando operaciones de compra...")
        
        op1 = portfolio_service.add_operation(
            portfolio_id=portfolio1.id,
            asset_symbol="AAPL",
            operation_type=OperationType.BUY,
            quantity=Decimal("10"),
            price=Decimal("150.50"),
            fees=Decimal("5.00"),
            notes="Compra inicial de Apple"
        )
        print(f"  BUY 10 AAPL @ 150.50")
        
        op2 = portfolio_service.add_operation(
            portfolio_id=portfolio1.id,
            asset_symbol="AAPL",
            operation_type=OperationType.BUY,
            quantity=Decimal("5"),
            price=Decimal("155.00"),
            fees=Decimal("2.50"),
            notes="Segunda compra de Apple"
        )
        print(f"  BUY 5 AAPL @ 155.00")
        
        op3 = portfolio_service.add_operation(
            portfolio_id=portfolio1.id,
            asset_symbol="GOOGL",
            operation_type=OperationType.BUY,
            quantity=Decimal("8"),
            price=Decimal("2800.00"),
            fees=Decimal("10.00"),
            notes="Compra de Google"
        )
        print(f"  BUY 8 GOOGL @ 2800.00")
        
        op4 = portfolio_service.add_operation(
            portfolio_id=portfolio1.id,
            asset_symbol="BTC",
            operation_type=OperationType.BUY,
            quantity=Decimal("0.5"),
            price=Decimal("45000.00"),
            fees=Decimal("50.00"),
            notes="Compra de Bitcoin"
        )
        print(f"  BUY 0.5 BTC @ 45000.00")
        
        print(f"\nportfolio {portfolio1.name}:")
        portfolio_detail = portfolio_service.get_portfolio(portfolio1.id)
        if portfolio_detail:
            print(f"  valor: ${portfolio_detail.total_value}")
            print(f"  costo: ${portfolio_detail.total_cost}")
            print(f"  ganancia: ${portfolio_detail.total_gain_loss}")
            print(f"  posiciones:")
            for asset in portfolio_detail.assets:
                print(f"    {asset.asset_symbol}: {asset.quantity} @ ${asset.average_price}")
        
        print("\nregistrando venta...")
        op5 = portfolio_service.add_operation(
            portfolio_id=portfolio1.id,
            asset_symbol="AAPL",
            operation_type=OperationType.SELL,
            quantity=Decimal("3"),
            price=Decimal("160.00"),
            fees=Decimal("2.00"),
            notes="Venta parcial de Apple"
        )
        print(f"  SELL 3 AAPL @ 160.00")
        
        print(f"\nhistorial de operaciones:")
        operations = portfolio_service.get_portfolio_operations(portfolio1.id)
        for op in operations:
            print(f"  {op.operation_type.value} {op.quantity} {op.asset_symbol} @ ${op.price}")
        
        print(f"\nactualizando portfolio...")
        portfolio_service.update_portfolio(
            portfolio1.id,
            name="Portfolio Conservador Actualizado",
            description="Inversiones de largo plazo - Actualizado"
        )
        print("portfolio actualizado")
        
        print(f"\neliminando portfolio {portfolio2.name}...")
        portfolio_service.delete_portfolio(portfolio2.id)
        print("portfolio eliminado")
        
    except Exception as e:
        print(f"error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    print("inicializando base de datos...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("db lista\n")
    
    try:
        user1_id, user2_id = test_user_service()
        test_portfolio_service(user1_id, user2_id)
        print("\ntests completados\n")
        
    except Exception as e:
        print(f"\nerror en tests: {e}\n")
        raise


if __name__ == "__main__":
    main()
