# app/models/role_enum.py
import enum

class Role(str, enum.Enum):
    OWNER = "owner"
    COLLABORATOR = "collaborator"