def userSchema(user) -> dict:
    return{
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "rol_id": str(user["rol_id"])
    }
    
def userListSchema(users) -> list:
    return [userSchema(user) for user in users]