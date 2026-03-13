# ============================================
# EcoPackAI - ML Model Training
# ============================================

from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

print("\nLoading Training Data...\n")

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
ARTIFACTS_DIR = BASE_DIR / "artifacts"

# Load datasets
X_train = joblib.load(ARTIFACTS_DIR / "X_train.pkl")
X_test = joblib.load(ARTIFACTS_DIR / "X_test.pkl")

y_cost_train = joblib.load(ARTIFACTS_DIR / "y_cost_train.pkl")
y_cost_test = joblib.load(ARTIFACTS_DIR / "y_cost_test.pkl")

y_co2_train = joblib.load(ARTIFACTS_DIR / "y_co2_train.pkl")
y_co2_test = joblib.load(ARTIFACTS_DIR / "y_co2_test.pkl")

# --------------------------------------------
# COST PREDICTION MODEL
# --------------------------------------------

print("\nTraining Cost Prediction Model...\n")

cost_model = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

cost_model.fit(X_train, y_cost_train)

cost_pred = cost_model.predict(X_test)

# Evaluation
rmse_cost = np.sqrt(mean_squared_error(y_cost_test, cost_pred))
mae_cost = mean_absolute_error(y_cost_test, cost_pred)
r2_cost = r2_score(y_cost_test, cost_pred)

print("Cost Prediction Metrics:")
print("RMSE:", round(rmse_cost, 2))
print("MAE:", round(mae_cost, 2))
print("R2 Score:", round(r2_cost, 2))

# Save Cost Model
MODELS_DIR.mkdir(parents=True, exist_ok=True)
joblib.dump(cost_model, MODELS_DIR / "cost_model.pkl")

# --------------------------------------------
# CO2 PREDICTION MODEL
# --------------------------------------------

print("\nTraining CO2 Prediction Model...\n")

co2_model = RandomForestRegressor(
    n_estimators=80,
    max_depth=4,
    min_samples_leaf=8,
    max_features=0.7,
    random_state=42
)

co2_model.fit(X_train, y_co2_train)

co2_pred = co2_model.predict(X_test)

# Evaluation
rmse_co2 = np.sqrt(mean_squared_error(y_co2_test, co2_pred))
mae_co2 = mean_absolute_error(y_co2_test, co2_pred)
r2_co2 = r2_score(y_co2_test, co2_pred)

print("CO2 Prediction Metrics:")
print("RMSE:", round(rmse_co2, 2))
print("MAE:", round(mae_co2, 2))
print("R2 Score:", round(r2_co2, 2))

# Save CO2 Model
joblib.dump(co2_model, MODELS_DIR / "co2_model.pkl")

print("\nModels Trained & Saved Successfully!")
