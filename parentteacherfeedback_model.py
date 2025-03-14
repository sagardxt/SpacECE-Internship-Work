# Import necessary libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Load the data (replace with your actual data)
df = pd.read_csv(r"C:\Users\ASUS\Documents\Copy of Dyslexia_Detection_Datasets(1).csv")  # Replace with actual path to your data

# Step 1: Preprocess Data

# Remove 'User_ID' and 'Child_ID' as they are identifiers and not useful for prediction
df = df.drop(['User_ID', 'Child_ID'], axis=1)

# Encode 'Role' and 'Feedback_Type' as categorical variables using Label Encoding
label_encoder = LabelEncoder()
df['Role'] = label_encoder.fit_transform(df['Role'])
df['Feedback_Type'] = label_encoder.fit_transform(df['Feedback_Type'])

# For the 'Comments' column, we may need to process the text (e.g., using TF-IDF, but for simplicity, we'll drop it in this case)
# You can choose to extract features from 'Comments' by using techniques like TF-IDF if you want to include text data.

df = df.drop('Comments', axis=1)  # Drop Comments column for simplicity (optional)

# Step 2: Define Features and Target Variable
X = df.drop('Engagement_Level (1-10)', axis=1)  # Features
y = df['Engagement_Level (1-10)']  # Target (Engagement_Level)

# Step 3: Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Standardizing the features (optional but often helps with gradient-based models)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Step 5: Initialize Gradient Boosting Regressor
model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)

# Step 6: Train the model
model.fit(X_train, y_train)

# Step 7: Predict on the test set
y_pred = model.predict(X_test)

# Step 8: Evaluate the model
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
print(f"R-squared: {r2:.2f}")

# Step 9: Hyperparameter Tuning (Optional)
# This step is optional and can help improve the model's performance.

param_grid = {
    'n_estimators': [100, 150],
    'learning_rate': [0.1, 0.05],
    'max_depth': [3, 5],
}

# Perform GridSearchCV to find the best parameters
grid_search = GridSearchCV(GradientBoostingRegressor(), param_grid, cv=5)
grid_search.fit(X_train, y_train)

# Best parameters found by GridSearchCV
print("\nBest parameters found by GridSearchCV:")
print(grid_search.best_params_)

# Step 10: Retrain the model with the best parameters
best_model = grid_search.best_estimator_
best_model.fit(X_train, y_train)

# Step 11: Predict with the best model and evaluate
y_pred_best = best_model.predict(X_test)
mse_best = mean_squared_error(y_test, y_pred_best)
rmse_best = np.sqrt(mse_best)
r2_best = r2_score(y_test, y_pred_best)

print(f"\nRMSE with Best Model: {rmse_best:.2f}")
print(f"R-squared with Best Model: {r2_best:.2f}")
