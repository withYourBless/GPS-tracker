from enum import Enum


class Role(str, Enum):
    ADMIN = 'Administrator'
    USER = 'User'
