from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pandas as pd
from tensorflow import keras
import joblib

model = keras.models.load_model('model.keras')
label_encoder = joblib.load('label_encoder.pkl')

app = FastAPI()

class InputData(BaseModel):
    features: list

@app.post('/predict')
def predict(input_data: InputData):
    input_df = pd.DataFrame(input_data.features)

    predictions = model.predict(input_df)

    top_n = 3
    predicted_probabilities = predictions[0]
    top_n_indices = np.argsort(predicted_probabilities)[-top_n:][::-1]
    top_n_probabilities = predicted_probabilities[top_n_indices]
    top_n_classes = label_encoder.inverse_transform(top_n_indices)

    results = []
    for i in range(top_n):
        percentage = top_n_probabilities[i] * 100
        results.append({
            'label': top_n_classes[i],
            'probability': f'{percentage:.2f}%'
        })

    return results

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)