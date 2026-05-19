import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import router as gpu_router

app = FastAPI(title="featurize API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(gpu_router)

@app.get("/")
def read_test():
    return {"msg": "Welcome"}

# if __name__=="__main__":
#     print("Server running: http://127.0.0.1:8000")
#     uvicorn.run(app, host="127.0.0.1", port=8000)