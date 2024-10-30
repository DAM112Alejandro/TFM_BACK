def statusSchema(status) -> dict:
    return {
        "id": str(status["_id"]),
        "description": status["description"]
    }
    
def statusListSchema(statuses) -> list:
    return [statusSchema(status) for status in statuses]