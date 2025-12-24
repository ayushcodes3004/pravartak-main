import joblib
import os
import numpy as np

# Load model
model_path = os.getenv('RISK_MODEL_PATH', '../model/risk_model.pkl')
model = joblib.load(model_path)
print('Model loaded')

# Test features (same as what backend sends)
test_features = np.array([[85.0, 7.5, 0, 1]])
print('Test features shape:', test_features.shape)
print('Test features:', test_features)

try:
    result = model.predict(test_features)
    print('Prediction successful:', result)
except Exception as e:
    print('Prediction error:', str(e))
    import traceback
    traceback.print_exc()