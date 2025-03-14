# Import necessary libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder

# Load the data
data = pd.read_csv(r"C:\Users\ASUS\Documents\Copy of Dyslexia_Detection_Datasets(1).csv")

# Preprocess the data (assuming data is in a format like: Age, Handwriting_Sample, etc.)
# Convert categorical features like Handwriting_Sample, Letter_Confusion, Spacing_Issues if necessary.
label_encoder = LabelEncoder()

# Example: Encoding categorical features (if they are categorical in nature)
data['Handwriting_Sample'] = label_encoder.fit_transform(data['Handwriting_Sample'])
data['Letter_Confusion'] = label_encoder.fit_transform(data['Letter_Confusion'])
data['Spacing_Issues'] = label_encoder.fit_transform(data['Spacing_Issues'])

# Define feature variables and target
X = data[['Age', 'Handwriting_Sample', 'Letter_Confusion', 'Spacing_Issues']]  # Features
y = data['Writing_Speed (words/min)']  # Target variable

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize Gradient Boosting Regressor model
model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)

# Train the model
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

# Evaluate the model using Mean Squared Error (for regression problems)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

# Optionally, you can check the feature importance from the model:
importances = model.feature_importances_
print(f"Feature Importances: {importances}")
