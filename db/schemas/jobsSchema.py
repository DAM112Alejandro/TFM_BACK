def jobSchema(job) -> dict:
    return{
        "id": str(job["_id"]),
        "registration_date": str(job["registration_date"]),
        "appointment_date": str(job["appointment_date"]),
        "start_date": str(job["start_date"]),
        "finish_date": str(job["finish_date"]),
        "license_plate": job["license_plate"],
        "client_phone": job["client_phone"],
        "user_id": str(job["user_id"]),
        "status_id": str(job["status_id"]),
        "workType_id": str(job["workType_id"])
    }
    
def jobListSchema(jobs) -> list:
    return [jobSchema(job) for job in jobs]