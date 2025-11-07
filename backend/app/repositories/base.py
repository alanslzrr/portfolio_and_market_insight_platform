"""
repositorio base generico con operaciones crud comunes.

el patron repository separa la logica de acceso a datos de la logica de negocio.
beneficios:
- codigo reutilizable (dry - don't repeat yourself)
- testing mas facil (se puede mockear el repositorio)
- cambios en bd no afectan servicios (abstraccion)
- queries centralizadas y consistentes

este repositorio base es generico (usa typevar) para que pueda
trabajar con cualquier modelo orm.
"""
from typing import Generic, TypeVar, Type, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import Base


# typevar para hacer el repositorio generico
# t puede ser cualquier modelo que herede de base
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    repositorio base generico con operaciones crud estandar.
    
    proporciona metodos comunes que todos los repositorios necesitan:
    - create: crear nueva entidad
    - get_by_id: obtener por id
    - get_all: listar todas
    - update: actualizar entidad
    - delete: eliminar entidad
    - count: contar entidades
    
    los repositorios especificos heredan de esta clase y agregan
    metodos propios del dominio.
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        inicializa el repositorio.
        
        args:
            model: clase del modelo orm (ej: user, portfolio)
            db: sesion de sqlalchemy
        """
        self.model = model
        self.db = db
    
    def create(self, obj: ModelType) -> ModelType:
        """
        crea una nueva entidad en la base de datos.
        
        args:
            obj: instancia del modelo a crear
            
        returns:
            modeltype: la entidad creada con su id asignado
            
        raises:
            sqlalchemyerror: si hay error al insertar
        """
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)  # recargar para obtener valores generados (id, timestamps)
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """
        obtiene una entidad por su id.
        
        args:
            id: uuid de la entidad
            
        returns:
            la entidad si existe, none en caso contrario
        """
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        obtiene todas las entidades con paginacion.
        
        args:
            skip: numero de registros a saltar (para paginacion)
            limit: maximo numero de registros a retornar
            
        returns:
            lista de entidades
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, obj: ModelType) -> ModelType:
        """
        actualiza una entidad existente.
        
        args:
            obj: instancia del modelo con cambios
            
        returns:
            la entidad actualizada
            
        raises:
            sqlalchemyerror: si hay error al actualizar
        """
        try:
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def delete(self, id: UUID) -> bool:
        """
        elimina una entidad por su id.
        
        args:
            id: uuid de la entidad a eliminar
            
        returns:
            true si se elimino, false si no existia
            
        raises:
            sqlalchemyerror: si hay error al eliminar
        """
        try:
            obj = self.get_by_id(id)
            if obj:
                self.db.delete(obj)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def count(self) -> int:
        """
        cuenta el total de entidades.
        
        returns:
            numero total de registros
        """
        return self.db.query(self.model).count()
    
    def exists(self, id: UUID) -> bool:
        """
        verifica si existe una entidad con el id dado.
        
        args:
            id: uuid a verificar
            
        returns:
            true si existe, false en caso contrario
        """
        return self.db.query(self.model).filter(self.model.id == id).count() > 0
