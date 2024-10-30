def roleSchema(role) -> dict:
    return {
        "id": str(role["_id"]),
        "description": role["description"],
    }
    
def roleListSchema(roles) -> list:
    return [roleSchema(role) for role in roles]