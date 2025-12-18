import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import accuracy_score

# Load the dataset
file_path = '../../../data/overall.csv'
data = pd.read_csv(file_path)

# Assuming your data does not have a header, we'll read it without headers
data = pd.read_csv(file_path, header=None)

# Convert the first (and only) column to a NumPy array for easier processing
y = data.iloc[:, 0].values

# Fit the ARIMA model
# Using a simple (1,0,1) ARIMA model, but you might experiment with different (p,d,q) parameters
model = ARIMA(y, order=(1,0,1))
fitted_model = model.fit()

# Make predictions
# We'll predict the same length as the original data
predictions = fitted_model.predict(start=0, end=len(y)-1)

# Convert predictions to binary using a threshold
# You can choose a threshold, here 0.5 is used as an example
binary_predictions = (predictions > 0.5).astype(int)

# Calculate accuracy
accuracy = accuracy_score(y, binary_predictions)
print(f'Accuracy: {accuracy * 100:.2f}%')

# Display results
print('Predictions:', binary_predictions)
