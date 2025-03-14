# Import necessary libraries
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Load the data 
df = pd.read_csv(r"C:\Users\ASUS\Documents\Copy of Dyslexia_Detection_Datasets(1).csv")  # Make sure your CSV file path is correct

# Step 1: Preprocess Data

# Remove 'Child_ID' as it is not useful for the prediction task
df = df.drop('Child_ID', axis=1)

# Encode 'Game_Completed' and 'Suggested_Next_Level' as categorical variables
label_encoder = LabelEncoder()

# Encode 'Game_Completed' - Transform game names into numeric labels
df['Game_Completed'] = label_encoder.fit_transform(df['Game_Completed'])

# Encode 'Suggested_Next_Level' - Convert 'Yes'/'No' to numeric values (1/0)
df['Suggested_Next_Level'] = label_encoder.fit_transform(df['Suggested_Next_Level'])

# Step 2: Define Features and Target Variable
X = df.drop('Suggested_Next_Level', axis=1)  # Features
y = df['Suggested_Next_Level']  # Target (Suggested_Next_Level)

# Step 3: Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Initialize Gradient Boosting Classifier
model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3)

# Step 5: Train the model
model.fit(X_train, y_train)

# Step 6: Predict on the test set
y_pred = model.predict(X_test)

# Step 7: Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.2f}%")

# Step 8: Classification Report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Step 9: Hyperparameter Tuning (Optional)
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

# Step 10: Retrain the model with the best parameters
best_model = grid_search.best_estimator_
best_model.fit(X_train, y_train)

# Step 11: Predict with the best model and evaluate
y_pred_best = best_model.predict(X_test)
accuracy_best = accuracy_score(y_test, y_pred_best)
print(f"Accuracy with Best Model: {accuracy_best * 100:.2f}%")

