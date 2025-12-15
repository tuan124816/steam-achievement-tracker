from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Simple health check endpoint.
    Used to verify that the backend is running.
    """
    return {
        "status": "ok",
        "service": "steam-tracker-backend"
    }
