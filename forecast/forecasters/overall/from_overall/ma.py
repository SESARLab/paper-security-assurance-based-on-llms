import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import sys

# Load arguments for forecast length
forecast_length = int(sys.argv[1]) if len(sys.argv) > 1 else 1
if forecast_length < 1:
    raise ValueError("Forecast length must be at least 1.")

# Load the dataset
file_path = '../../../data/overall.csv'
data = pd.read_csv(file_path, header=None)

# Convert the first (and only) column to a NumPy array for easier processing
y = data.iloc[:, 0].values

# Define the window size for the moving average
window_size = 5

# Calculate the moving average for the original data
moving_avg = np.convolve(y, np.ones(window_size) / window_size, mode='valid')

# To align the moving average with the original data length, add NaNs at the start
moving_avg = np.concatenate((np.full(window_size - 1, np.nan), moving_avg))

# Forecast the next `forecast_length` values
# Start by calculating the moving average up to the end of `y`
forecast_values = []
for i in range(forecast_length):
    if i == 0:
        # Use the last `window_size` values in `y` for the initial moving average forecast
        forecast_input = y[-window_size:]
    else:
        # Update forecast_input with previously forecasted values
        forecast_input = np.append(forecast_input[1:], forecast_values[-1])

    # Calculate the mean of the last `window_size` values to get the next forecasted value
    next_forecast = np.mean(forecast_input)
    forecast_values.append(next_forecast)

# Apply threshold and make binary predictions
threshold = 0.5  # You can adjust this value
binary_predictions = (np.concatenate((moving_avg, forecast_values)) > threshold).astype(int)

# Replace NaN values in binary predictions
binary_predictions[np.isnan(binary_predictions)] = 0

# Calculate metrics only for the original length of `y`
accuracy = accuracy_score(y, binary_predictions[:len(y)])
precision = precision_score(y, binary_predictions[:len(y)], zero_division=0)
recall = recall_score(y, binary_predictions[:len(y)], zero_division=0)
f1 = f1_score(y, binary_predictions[:len(y)], zero_division=0)

# Display results
print(f'Accuracy: {accuracy * 100:.2f}%')
print(f'Precision: {precision * 100:.2f}%')
print(f'Recall: {recall * 100:.2f}%')
print(f'F1 Score: {f1 * 100:.2f}%')
print('Moving Average Predictions:', binary_predictions[:len(y)])
print('Actual Values:', y)
print(f'Forecasted Next {forecast_length} Values (moving average):', forecast_values)
