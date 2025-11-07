(uie_arquitectura_software) PS C:\Projects\UIE_GISI\arquitectura_software\portfolio_and_market_insight_platform\backend> python main.py
inicializando base de datos...
db lista


--- testing user service ---

creando usuarios...
(trapped) error reading bcrypt version
Traceback (most recent call last):
  File "C:\Users\alanslzr\anaconda3\envs\uie_arquitectura_software\Lib\site-packages\passlib\handlers\bcrypt.py", line 620, in _load_backend_mixin
    version = _bcrypt.__about__.__version__
              ^^^^^^^^^^^^^^^^^
AttributeError: module 'bcrypt' has no attribute '__about__'
usuario creado: juan.perez@example.com
usuario creado: maria.garcia@example.com
usuario creado: john.doe@example.com

listando usuarios...
total: 3
  Juan Perez (juan.perez@example.com)
  Maria Garcia (maria.garcia@example.com)
  John Doe (john.doe@example.com)

buscando usuario: juan.perez@example.com
encontrado: Juan Perez, verificado: False

actualizando perfil de juan.perez@example.com...
perfil actualizado: EUR, Europe/London

verificando email de juan.perez@example.com...
verificado: True

actualizando nombre de maria.garcia@example.com...
nombre actualizado

total usuarios en sistema: 3

desactivando john.doe@example.com...
usuario desactivado

--- testing portfolio service ---

creando portfolios...
portfolio creado: Portfolio Conservador
portfolio creado: Portfolio Agresivo
portfolio creado: Portfolio Diversificado

portfolios del usuario 1:
  Portfolio Conservador
  Portfolio Agresivo

registrando operaciones de compra...
  BUY 10 AAPL @ 150.50
  BUY 5 AAPL @ 155.00
  BUY 8 GOOGL @ 2800.00
  BUY 0.5 BTC @ 45000.00

portfolio Portfolio Conservador:
  valor: $47225.00
  costo: $47180.00
  ganancia: $45.00
  posiciones:
    AAPL: 15.00000000 @ $152.00
    GOOGL: 8.00000000 @ $2800.00
    BTC: 0.50000000 @ $45000.00

registrando venta...
  SELL 3 AAPL @ 160.00

historial de operaciones:
  SELL 3.00000000 AAPL @ $160.00
  BUY 0.50000000 BTC @ $45000.00
  BUY 8.00000000 GOOGL @ $2800.00
  BUY 5.00000000 AAPL @ $155.00
  BUY 10.00000000 AAPL @ $150.50

actualizando portfolio...
portfolio actualizado

eliminando portfolio Portfolio Agresivo...
portfolio eliminado

tests completados