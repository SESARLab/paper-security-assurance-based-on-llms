import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np
import pandas as pd

# Load data
data = pd.read_csv("../../../data/complete.csv", header=None).values
X = data[:, :-1]  # First 10 columns are the intermediate tests
y = data[:, -1]   # Last column is the final success/failure result

# Convert data to tensors
X = torch.tensor(X, dtype=torch.float32)
y = torch.tensor(y, dtype=torch.float32)

# Define train and test split
train_size = int(0.8 * len(X))
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# Create DataLoader, wraps in TensorDataset allowing X and y to be accessed together
train_dataset = TensorDataset(X_train, y_train)
test_dataset = TensorDataset(X_test, y_test)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)
# Every batch will contain 16 samples
# Shuffling training to improve generalization
# No shuffling for testing for a consistent evaluation

# Define LSTM model, input size: each timestep in the sequence has 1 input value, hidden size is the size of the hidden state, num layers the number of LSTM layers, output size is 1, because the model outputs a single value
class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=32, num_layers=1, output_size=1):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x.unsqueeze(-1), (h0, c0))
        out = self.dropout(out[:, -1, :])  # Apply dropout to the last LSTM output
        out = self.fc(out)
        return torch.sigmoid(out).squeeze()  # Sigmoid for binary classification

# Initialize model, loss function, and optimizer
model = LSTMModel(input_size=1, hidden_size=32, num_layers=1).to("cpu")
criterion = nn.BCELoss()  # Binary Cross Entropy Loss for binary classification
optimizer = optim.AdamW(model.parameters(), lr=0.001)  # AdamW optimizer with a learning rate of 0.001

# Learning rate scheduler, reduces the learning rate by a facotr of 0.1 every 10 epochs, helping the model converge
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)

# Train the model
def train_model(model, train_loader, criterion, optimizer, scheduler, num_epochs=50):
    model.train() # Set the model to training mode
    for epoch in range(num_epochs): # Iterates over batches in train lodaer, computes predictions and updates model weight to minimze the loss
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        
        scheduler.step()  # Adjust learning rate
        print(f"Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}")

# Evaluate the model
def evaluate_model(model, test_loader):
    model.eval() # Set the model to evaluation mode
    y_true = []
    y_pred = []
    with torch.no_grad(): # Disables gradient computation
        for inputs, labels in test_loader:
            outputs = model(inputs)
            predicted = (outputs >= 0.5).float()  # Binary threshold at 0.5 to get binary predictions
            y_true.extend(labels.tolist())
            y_pred.extend(predicted.tolist())
    
    # Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")

    return accuracy, precision, recall, f1

# Run training and evaluation
train_model(model, train_loader, criterion, optimizer, scheduler, num_epochs=50)
evaluate_model(model, test_loader)
