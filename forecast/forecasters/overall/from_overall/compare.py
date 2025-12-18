import numpy as np
import torch
import torch.nn as nn
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.ensemble import RandomForestClassifier
from statsmodels.tsa.stattools import acf
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
from pathlib import Path

class TimeSeriesDataset(Dataset):
    """Custom Dataset for binary time series"""
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)
        
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class LSTMPredictor(nn.Module):
    """LSTM model for binary sequence prediction"""
    def __init__(self, input_size=1, hidden_size=32, num_layers=1):
        super(LSTMPredictor, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc1 = nn.Linear(hidden_size, 16)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(16, 1)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        lstm_out, _ = self.lstm(x, (h0, c0))
        lstm_out = lstm_out[:, -1, :]
        
        out = self.fc1(lstm_out)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        out = self.sigmoid(out)
        
        return out

class BinaryTimeSeriesPredictor:
    def __init__(self, sequence_length=10, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.sequence_length = sequence_length
        self.device = device
        print(f"Using device: {self.device}")
        
    def load_data(self, file_path):
        """Load and preprocess the binary time series data"""
        try:
            df = pd.read_csv(file_path)
            # Assuming the data is just a single column of 0s and 1s
            data = df.iloc[:, 0].values
            print(f"Loaded {len(data)} samples")
            print(f"Distribution of classes: \n{pd.Series(data).value_counts(normalize=True)}")
            return data
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def prepare_sequences(self, data):
        """Convert time series into sequences for prediction"""
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:(i + self.sequence_length)])
            y.append(data[i + self.sequence_length])
        return np.array(X), np.array(y)
    
    def markov_chain(self, data):
        """Simple first-order Markov Chain"""
        transition_matrix = np.zeros((2, 2))
        for i in range(len(data)-1):
            transition_matrix[data[i], data[i+1]] += 1
            
        row_sums = transition_matrix.sum(axis=1)
        transition_matrix = transition_matrix / row_sums[:, np.newaxis]
        return transition_matrix
    
    def train_lstm(self, model, train_loader, criterion, optimizer, num_epochs):
        """Train the LSTM model"""
        model.train()
        train_losses = []
        
        for epoch in range(num_epochs):
            total_loss = 0
            for batch_X, batch_y in train_loader:
                batch_X = batch_X.to(self.device)
                batch_y = batch_y.to(self.device)
                
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y.unsqueeze(1))
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(train_loader)
            train_losses.append(avg_loss)
            
            if (epoch + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}')
        
        return train_losses
    
    def predict_lstm(self, model, test_loader):
        """Make predictions using the LSTM model"""
        model.eval()
        predictions = []
        with torch.no_grad():
            for batch_X, _ in test_loader:
                batch_X = batch_X.to(self.device)
                outputs = model(batch_X)
                predicted = (outputs.cpu().numpy() > 0.5).astype(int)
                predictions.extend(predicted)
        return np.array(predictions)

    def evaluate_model(self, y_true, y_pred, model_name):
        """Evaluate model performance"""
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
        
        print(f"\n{model_name} Results:")
        print(f"Accuracy: {accuracy:.3f}")
        print(f"Precision: {precision:.3f}")
        print(f"Recall: {recall:.3f}")
        print(f"F1 Score: {f1:.3f}")
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    def plot_training_history(self, losses, save_path=None):
        """Plot training loss history"""
        plt.figure(figsize=(10, 6))
        plt.plot(losses)
        plt.title('Training Loss Over Time')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path)
        plt.close()

def main():
    # Set random seeds for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    
    # Initialize predictor
    sequence_length = 100  # Adjust this based on your needs
    predictor = BinaryTimeSeriesPredictor(sequence_length=sequence_length)
    
    # Load data
    data_path = Path('../../../data/overall.csv')
    data = predictor.load_data(data_path)
    
    # Prepare sequences
    X, y = predictor.prepare_sequences(data)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    print(f"\nData shapes:")
    print(f"Training data: {X_train.shape}")
    print(f"Testing data: {X_test.shape}")
    
    # 1. Markov Chain
    print("\nTraining Markov Chain...")
    transition_matrix = predictor.markov_chain(data)
    markov_predictions = []
    current_state = data[-1]
    for _ in range(len(y_test)):
        prob = transition_matrix[current_state]
        prediction = 1 if prob[1] > 0.5 else 0
        markov_predictions.append(prediction)
        current_state = prediction
    
    # 2. Random Forest
    print("\nTraining Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_predictions = rf_model.predict(X_test)
    
    # 3. LSTM
    print("\nTraining LSTM...")
    # Prepare data loaders
    train_dataset = TimeSeriesDataset(
        X_train.reshape(-1, sequence_length, 1),
        y_train
    )
    test_dataset = TimeSeriesDataset(
        X_test.reshape(-1, sequence_length, 1),
        y_test
    )
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # Initialize model, criterion, and optimizer
    model = LSTMPredictor().to(predictor.device)
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    # Train the model and get training history
    train_losses = predictor.train_lstm(model, train_loader, criterion, optimizer, num_epochs=50)
    
    # Plot and save training history
    predictor.plot_training_history(train_losses, save_path='training_history.png')
    
    # Make predictions
    lstm_predictions = predictor.predict_lstm(model, test_loader)
    
    # Evaluate all models
    results = {}
    results['markov'] = predictor.evaluate_model(y_test, markov_predictions, "Markov Chain")
    results['random_forest'] = predictor.evaluate_model(y_test, rf_predictions, "Random Forest")
    results['lstm'] = predictor.evaluate_model(y_test, lstm_predictions.flatten(), "LSTM")
    
    # Save model results
    results_df = pd.DataFrame(results).round(3)
    results_df.to_csv('model_results.csv')
    print("\nResults saved to 'model_results.csv'")
    
    # Save the best model
    best_model = max(results.items(), key=lambda x: x[1]['f1'])[0]
    print(f"\nBest performing model: {best_model}")
    if best_model == 'lstm':
        torch.save(model.state_dict(), 'best_model.pth')
        print("Best model saved to 'best_model.pth'")

if __name__ == "__main__":
    main()