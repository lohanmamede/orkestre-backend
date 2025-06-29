# app/models/user_establishment_link.py
from sqlalchemy import Column, ForeignKey, Table, Enum as SAEnum
from app.db.base_class import Base
from .role_enum import Role

user_establishment_link = Table(
    'user_establishment_link',
    Base.metadata,
    Column('user_id', ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('establishment_id', ForeignKey('establishments.id', ondelete="CASCADE"), primary_key=True),
    Column('role', SAEnum(Role), nullable=False, default=Role.COLLABORATOR)
)