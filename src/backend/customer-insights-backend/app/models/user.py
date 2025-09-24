from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

# class UserInDb(User):

class User(Base):
    __tablename_="users"

    id = Column(Integer, primary_key=true, index = true)
    full_name = Column(String, nullable = False)
    email = Column(String, unique= True, nullable = False)
    role = Column(String, nullable = False)
    hashed_password = Column(String, nullable = False)
    is_active = Column(Boolean, default = True)

