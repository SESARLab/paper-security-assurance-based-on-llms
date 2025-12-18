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
y = data[:, :]    # Use all columns including the final result

# Parameters
sequence_length = 100  # Window length
input_size = X.shape[1]  # Number of features (all columns in X)
batch_size = 16

# Prepare sequences and labels for the sliding window
def create_sequences(X, seq_length):
    sequences = []
    labels = []
    for i in range(len(X) - seq_length):
        # Extract a sequence of `seq_length` rows as input and the (i+seq_length)th row as target
        sequences.append(X[i:i + seq_length])
        labels.append(X[i + seq_length])  # Predict the entire next row
    return torch.tensor(sequences, dtype=torch.float32), torch.tensor(labels, dtype=torch.float32)

X_seq, y_seq = create_sequences(X, sequence_length)

# Define train and test split
train_size = int(0.8 * len(X_seq))
X_train, X_test = X_seq[:train_size], X_seq[train_size:]
y_train, y_test = y_seq[:train_size], y_seq[train_size:]

# Create DataLoader
train_dataset = TensorDataset(X_train, y_train)
test_dataset = TensorDataset(X_test, y_test)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

# Define LSTM model with input size of all features
class LSTMModel(nn.Module):
    def __init__(self, input_size=10, hidden_size=32, num_layers=1):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, input_size)  # Output size is now the number of features
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.dropout(out[:, -1, :])  # Apply dropout to the last LSTM output
        out = self.fc(out)
        return torch.sigmoid(out)  # Sigmoid for binary classification across all features

# Initialize model, loss function, and optimizer
model = LSTMModel(input_size=input_size, hidden_size=32, num_layers=1).to("cpu")
criterion = nn.BCELoss()  # Binary Cross Entropy Loss
optimizer = optim.AdamW(model.parameters(), lr=0.001)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)

def train_model_with_checkpointing(model, train_loader, test_loader, criterion, optimizer, scheduler, num_epochs=50):
    model.train()
    best_loss = float('inf')
    best_model = None
    
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        
        scheduler.step()

        # Validation phase
        val_loss = 0
        model.eval()
        with torch.no_grad():
            for inputs, labels in test_loader:
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * inputs.size(0)  # Accumulate loss for averaging

        val_loss /= len(test_loader.dataset)
        print(f"Epoch [{epoch + 1}/{num_epochs}], Train Loss: {loss.item():.4f}, Val Loss: {val_loss:.4f}")

        # Checkpointing
        if val_loss < best_loss:
            best_loss = val_loss
            best_model = model.state_dict()  # Save the best model weights

    # Load the best model weights
    model.load_state_dict(best_model)
    print(f"Best Validation Loss: {best_loss:.4f}")

# Evaluate the model
def evaluate_model(model, test_loader):
    model.eval()
    y_true = []
    y_pred = []
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            predicted = (outputs >= 0.5).float()
            y_true.extend(labels.tolist())
            y_pred.extend(predicted.tolist())
    
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='macro')  # Adjust average method as necessary
    recall = recall_score(y_true, y_pred, average='macro')
    f1 = f1_score(y_true, y_pred, average='macro')
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")

    return accuracy, precision, recall, f1

# Run training with checkpointing and evaluate
train_model_with_checkpointing(model, train_loader, test_loader, criterion, optimizer, scheduler, num_epochs=50)
evaluate_model(model, test_loader)
