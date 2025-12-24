import joblib
import os
import numpy as np

# Simulate the exact data that would be received from frontend
test_data = {
    'attendance': 85.0,
    'marks': 7.5,
    'backlog': 0,
    'gender': 'Male'
}

print("Test data:", test_data)

# Create features exactly as done in backend
features = np.array([[
    test_data['attendance'],
    test_data['marks'],
    test_data['backlog'],
    1 if test_data['gender'].lower() == 'male' else 0
]])

print("Features array:", features)
print("Features shape:", features.shape)

# Load model
model_path = os.getenv('RISK_MODEL_PATH', '../model/risk_model.pkl')
model = joblib.load(model_path)
print('Model loaded')

# Check model expectations
ct = model.named_steps['preprocessor']
print('Model expects', ct.n_features_in_, 'features')

try:
    result = model.predict(features)
    print('Prediction successful:', result)
except Exception as e:
    print('Prediction error:', str(e))
    import traceback
    traceback.print_exc()