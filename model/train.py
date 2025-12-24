# train.py
import os
import logging
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from xgboost import XGBClassifier
import matplotlib.pyplot as plt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------- Config --------
DATA_PATH = "data/dataset.csv"
MODEL_OUT = "risk_model.pkl"
RANDOM_STATE = 42
TEST_SIZE = 0.20
TARGET = "Dropout"   # 👈 your actual target column

# -------- Load Data --------
logger.info("🔄 Loading dataset...")
df = pd.read_csv(DATA_PATH)
logger.info(f"✅ Data loaded: {df.shape}")
logger.info(f"Columns: {df.columns.tolist()}")

# Rename columns to match backend expectations
feature_mapping = {
    'Gender': 'gender',
    'Attendance_Rate': 'attendance',
    'Current_CGPA': 'marks',
    'Number_of_Backlogs': 'backlog'
}
df = df.rename(columns=feature_mapping)

# Safety check: Ensure target column exists
if TARGET not in df.columns:
    raise ValueError(f"❌ Target column '{TARGET}' not found. Available columns: {df.columns.tolist()}")

X = df.drop(TARGET, axis=1)
y = df[TARGET]

# -------- Preprocessing --------
# Select only the features we want to use
X = X[['gender', 'attendance', 'marks', 'backlog']]

# Separate categorical and numeric columns
categorical_cols = ['gender']
numeric_cols = ['attendance', 'marks', 'backlog']

# Create gender binary column (Male = 1, Female = 0)
X['gender_binary'] = (X['gender'] == 'Male').astype(int)
X = X.drop('gender', axis=1)  # Remove original gender column
numeric_cols = ['attendance', 'marks', 'backlog', 'gender_binary']

categorical_cols = []

logger.info(f"Categorical columns: {categorical_cols}")
logger.info(f"Numeric columns: {numeric_cols}")

# Pipelines
numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

# We only use numeric features
# Use indices instead of column names for arrays
preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, list(range(len(numeric_cols))))
    ]
)

# We already defined preprocessor above

# -------- Model --------
model = XGBClassifier(
    eval_metric="mlogloss",
    use_label_encoder=False,
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=RANDOM_STATE
)

pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", model)
])

# -------- Train/Test Split --------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
)

# -------- Training --------
logger.info("🚀 Training model...")
pipeline.fit(X_train, y_train)

# -------- Evaluation --------
y_pred = pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

logger.info("\n✅ Model Evaluation")
logger.info(f"Accuracy: {round(accuracy, 3)}")
logger.info(f"Classification Report:\n{report}")

# -------- Save Model --------
joblib.dump(pipeline, MODEL_OUT)
logger.info(f"💾 Model saved at: {MODEL_OUT}")

# -------- Confusion Matrix --------
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(5,4))
plt.imshow(cm, cmap="Blues")
plt.title("Confusion Matrix")
plt.colorbar()
plt.ylabel("True")
plt.xlabel("Predicted")
plt.show()
