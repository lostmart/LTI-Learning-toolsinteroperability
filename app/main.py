from fastapi import FastAPI

app = FastAPI(
    title="LTI Lab Platform",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "LTI Lab Platform API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}