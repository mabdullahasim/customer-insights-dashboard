
# class UserInDb(User):
#     __tablename__="users"
#     id = Column(Integer, primary_key=true, index = true)
#     full_name = Column(String, nullable = False)
#     email = Column(String, unique= True, nullable = False)
#     role = Column(String, nullable = False)
#     hashed_pwd = Column(String, nullable = False)
#     is_active = Column(Boolean, default = True)

class User(BaseModeL):
    username: str
    email: str or None = None
    full_name: str or None = None
    disabled: bool or None = None

# class UserCreate(BaseModeL):
#     name: str
#     email: str
#     role: str
#     password: str

# class UserResponse(BaseModeL):
#     id: int
#     name: str
#     email: str
#     role: str

class UserInDB(User):
    hashed_password: str