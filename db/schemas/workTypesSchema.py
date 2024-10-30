def workTypeSchema(workType) -> dict:
    return{
        "id": str(workType["_id"]),
        "description": workType["description"],
        "time": workType["time"]
    }
    
def workTypeListSchema(workTypes) -> list:
    return [workTypeSchema(workTypes) for workTypes in workTypes]