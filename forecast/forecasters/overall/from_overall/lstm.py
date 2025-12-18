import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import sys
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Check for forecast length argument
forecast_length = int(sys.argv[1]) if len(sys.argv) > 1 else 3  # Default to 5 if no argument is given
if forecast_length < 1:
    raise ValueError("Forecast length must be at least 1.")

# Load the dataset
file_path = '../../../data/overall.csv'
data = pd.read_csv(file_path, header=None)
y = data.iloc[:, 0].values  # Assuming data is a single-column CSV

# Normalize the data
y_min, y_max = y.min(), y.max()
y_normalized = (y - y_min) / (y_max - y_min)

# Set parameters
window_size = 50  # Number of past values used to predict future values
batch_size = 32
epochs = 50  # Adjust based on dataset and performance needs
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Prepare the data for LSTM
X, y_lstm = [], []
for i in range(len(y_normalized) - window_size - forecast_length + 1):
    X.append(y_normalized[i:i + window_size])
    y_lstm.append(y_normalized[i + window_size:i + window_size + forecast_length])

X = np.array(X)
y_lstm = np.array(y_lstm)

# Convert data to PyTorch tensors
X = torch.tensor(X, dtype=torch.float32).unsqueeze(-1).to(device)  # Shape [samples, time steps, features]
y_lstm = torch.tensor(y_lstm, dtype=torch.float32).to(device)       # Shape [samples, forecast_length]

# Define the LSTM model
class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=50, num_layers=2, output_size=forecast_length):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])  # Use the last time step's output for forecasting
        return out

# Instantiate and move the model to the device (GPU or CPU)
model = LSTMModel().to(device)

# Define loss function and optimizer
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training the model
model.train()
for epoch in range(epochs):
    optimizer.zero_grad()
    output = model(X)
    loss = criterion(output, y_lstm)
    loss.backward()
    optimizer.step()
    if (epoch + 1) % 10 == 0:  # Print loss every 10 epochs
        print(f'Epoch [{epoch + 1}/{epochs}], Loss: {loss.item():.4f}')

# Forecasting the next `forecast_length` values
model.eval()
with torch.no_grad():
    last_sequence = torch.tensor(y_normalized[-window_size:], dtype=torch.float32).unsqueeze(0).unsqueeze(-1).to(device)
    forecast = model(last_sequence).squeeze().cpu().numpy()

# Denormalize the forecasted values
forecast_denormalized = forecast * (y_max - y_min) + y_min

# Apply threshold to create binary predictions
binary_predictions = (forecast_denormalized >= 0.5).astype(int)

# Actual values for the forecast period
actual_values = y[-forecast_length:]

# Calculate metrics
accuracy = accuracy_score(actual_values, binary_predictions)
precision = precision_score(actual_values, binary_predictions, zero_division=0)
recall = recall_score(actual_values, binary_predictions, zero_division=0)
f1 = f1_score(actual_values, binary_predictions, zero_division=0)

# Display results
print(f'Forecasted Next {forecast_length} Values:', forecast_denormalized)
print(f'Accuracy: {accuracy * 100:.2f}%')
print(f'Precision: {precision * 100:.2f}%')
print(f'Recall: {recall * 100:.2f}%')
print(f'F1 Score: {f1 * 100:.2f}%')