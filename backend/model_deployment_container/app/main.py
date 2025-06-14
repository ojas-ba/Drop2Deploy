from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from google.cloud import storage
import os
from tensorflow.keras.models import load_model
import numpy as np
from pydantic import BaseModel, validator


model = None

def download_model(gcs_url:str):
    """
    Download a model file from Google Cloud Storage and save it locally.

    Args:
        gcs_url (str): GCS path to the model file (e.g., gs://bucket/model.pkl)
    
    Returns:
        Model file path if download is successful.

    Raises:
        ValueError: If the file extension is unsupported.
        RuntimeError: If download fails for any reason.
    """
    try:
        client = storage.Client()
        bucket_name,blob_name = gcs_url.replace("gs://", "").split("/", 1)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        if gcs_url.endswith(".h5"):
            blob.download_to_filename("model.h5")
            return "model.h5"
        elif gcs_url.endswith(".keras"):
            blob.download_to_filename("model.keras")
            return "model.keras"
        else:
            raise ValueError("Unsupported model file format. Supported formats are: .h5, .keras")
    except Exception as e:
        raise RuntimeError(f"Failed to download model from GCS: {e}")
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    GCS_MODEL_URL = os.getenv("GCS_MODEL_URL")
    if not GCS_MODEL_URL:
        raise RuntimeError("GCS_MODEL_URL environment variable not set")
    
    model_path = download_model(GCS_MODEL_URL)
    model = load_model(model_path)
    print("Model loaded successfully")
    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)


class InputData(BaseModel):
    data: list
    
    @validator("data")
    def validate_data(cls, v):
        if not isinstance(v, list) or not all(isinstance(i, (int, float)) for i in v):
            raise ValueError("Input data must be a list of numbers.")
        return v
    

@app.post("/predict")
async def predict(request: InputData):
    """
    Endpoint to handle prediction requests.
    This endpoint downloads the model from GCS, loads it, and returns a prediction.
    Returns:
        dict: Prediction result.
        
    """

    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    if not request.data:
        raise HTTPException(status_code=400, detail="Input data is required")
    
    try:
        input_data = np.array(request.data)
        
        try:
            if len(input_data.shape) == len(model.input_shape) - 1:
                input_data = np.expand_dims(input_data, axis=0)
        except AttributeError:
            if input_data.ndim == 1:
                input_data = input_data.reshape(1, -1)
        
        prediction = model.predict(input_data)
        prediction = prediction.tolist()
        return {"prediction": prediction,"success": True}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))