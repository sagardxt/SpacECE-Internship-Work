import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Load the dataset from CSV file
df = pd.read_csv(r"C:\Users\ASUS\Documents\Dyslexia_Detection_Datasets.csv")

# Preview the dataset
print(df.head())

# Convert categorical columns (e.g., Gender) into numerical values (0 for Male, 1 for Female)
df['Gender'] = df['Gender'].apply(lambda x: 0 if x == 'M' else 1)

# Convert the 'Word_Spoken' column into numerical values (you can use label encoding or one-hot encoding)
# Here, we’ll use label encoding for simplicity (you can further improve it)
df['Word_Spoken'] = df['Word_Spoken'].astype('category').cat.codes

# Select features (independent variables) and target (dependent variable)
# Features: 'Age', 'Gender', 'Word_Spoken', 'Pronunciation_Error', 'Phoneme_Error'
# Target: 'Fluency_Score'

X = df[['Age', 'Gender', 'Word_Spoken']]  # Features
y = df['Fluency_Score (1-10)']  # Target variable

# Split the data into training and testing sets (80% training, 20% testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the Linear Regression model
model = GradientBoostingRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model's performance
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'Mean Squared Error: {mse}')
print(f'R-squared: {r2}')
