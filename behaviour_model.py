# Import necessary libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import cross_val_score

# Load your data 
data = pd.read_csv(r"C:\Users\ASUS\Documents\Copy of Dyslexia_Detection_Datasets(1).csv")


df = pd.DataFrame(data)

# Step 1: Preprocess Data

# Remove 'Child_ID' if it's not needed as a feature
df = df.drop('Child_ID', axis=1)

# Encode categorical features (Emotion, Speech_Tone, and Facial_Expression)
label_encoder = LabelEncoder()
df['Emotion'] = label_encoder.fit_transform(df['Emotion'])
df['Speech_Tone'] = label_encoder.fit_transform(df['Speech_Tone'])
df['Facial_Expression'] = label_encoder.fit_transform(df['Facial_Expression'])

# Separate features (X) and target (y)
X = df.drop('Stress_Level (1-10)', axis=1)  # Features
y = df['Stress_Level (1-10)']  # Target variable

# Step 2: Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 3: Initialize Gradient Boosting Classifier
model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3)

# Step 4: Train the model
model.fit(X_train, y_train)

# Step 5: Predict on the test set
y_pred = model.predict(X_test)

# Step 6: Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.2f}%")

# Step 7: Classification Report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Step 8: Hyperparameter Tuning (Optional)
# This step is optional if you want to improve the model's performance.
param_grid = {
    'n_estimators': [100, 150],
    'learning_rate': [0.1, 0.05],
    'max_depth': [3, 5],
}

# Perform GridSearchCV to find the best parameters
grid_search = GridSearchCV(GradientBoostingClassifier(), param_grid, cv=5)
grid_search.fit(X_train, y_train)

# Best parameters found by GridSearchCV
print("\nBest parameters found by GridSearchCV:")
print(grid_search.best_params_)

# Step 9: Retrain the model with the best parameters
best_model = grid_search.best_estimator_
best_model.fit(X_train, y_train)

# Step 10: Predict with the best model and evaluate
y_pred_best = best_model.predict(X_test)
accuracy_best = accuracy_score(y_test, y_pred_best)
print(f"Accuracy with Best Model: {accuracy_best * 100:.2f}%")

