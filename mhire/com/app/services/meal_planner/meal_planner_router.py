config = Config()
router = APIRouter()

feature1_service = Feature1(config)

@router.get("/endpont1-name")
async def get_endpoint_response():
    return {"message": "Hello from Feature1' Endpoint1!"}

@router.post("/endpont2-name")
async def get_endpoint_response():
    return {"message": "Hello from Feature1's Endpoint2!"}