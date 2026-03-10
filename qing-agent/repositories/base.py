"""
Repository 基类
所有 Repository 的父类，提供通用 CRUD 操作
"""

from typing import TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import inspect

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Repository 基类"""
    
    def __init__(self, model: type[T], db: Session):
        """
        初始化 Repository
        
        Args:
            model: SQLAlchemy 模型类
            db: 数据库会话
        """
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[T]:
        """
        根据 ID 获取单个记录
        
        Args:
            id: 记录 ID
            
        Returns:
            记录对象，不存在返回 None
        """
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        获取所有记录（分页）
        
        Args:
            skip: 跳过数量
            limit: 返回数量上限
            
        Returns:
            记录列表
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, data: Dict[str, Any]) -> T:
        """
        创建新记录
        
        Args:
            data: 数据字典
            
        Returns:
            创建的记录对象
        """
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[T]:
        """
        更新记录
        
        Args:
            id: 记录 ID
            data: 更新数据
            
        Returns:
            更新后的记录对象，不存在返回 None
        """
        obj = self.get(id)
        if not obj:
            return None
        
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, id: int) -> bool:
        """
        删除记录
        
        Args:
            id: 记录 ID
            
        Returns:
            是否删除成功
        """
        obj = self.get(id)
        if not obj:
            return False
        
        self.db.delete(obj)
        self.db.commit()
        return True
    
    def filter(self, **kwargs) -> List[T]:
        """
        根据条件过滤记录
        
        Args:
            **kwargs: 过滤条件
            
        Returns:
            符合条件的记录列表
        """
        query = self.db.query(self.model)
        for key, value in kwargs.items():
            if value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.all()
    
    def first(self, **kwargs) -> Optional[T]:
        """
        根据条件获取第一条记录
        
        Args:
            **kwargs: 过滤条件
            
        Returns:
            符合条件的第一条记录，不存在返回 None
        """
        query = self.db.query(self.model)
        for key, value in kwargs.items():
            if value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.first()
