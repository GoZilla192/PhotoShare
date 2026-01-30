import enum

class UserRole(str, enum.Enum):
    user = "user"
    moderator = "moderator"
    admin = "admin"
