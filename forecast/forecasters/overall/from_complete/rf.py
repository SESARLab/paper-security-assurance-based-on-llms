import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings
warnings.filterwarnings("ignore")

def load_data(file_path):
    # Load the CSV file
    data = pd.read_csv(file_path)
    return data

def create_sequence_datasets(data, seq_length=1000, forecast_horizon=10):
    """Create datasets of sequences for training and testing."""
    # Total number of rows in dataset
    total_rows = len(data)
    
    # Need at least seq_length + forecast_horizon rows
    if total_rows < seq_length + forecast_horizon:
        raise ValueError(f"Not enough data. Need at least {seq_length + forecast_horizon} rows.")
    
    # Calculate number of complete sequences we can create
    num_sequences = total_rows - seq_length - forecast_horizon + 1
    
    print(f"Creating {num_sequences} sequences of length {seq_length} with {forecast_horizon} forecast horizon")
    
    X_sequences = []
    y_sequences = []
    
    for i in range(num_sequences):
        # Input sequence - all columns (including the target column for previous steps)
        X_seq = data.iloc[i:i+seq_length].values
        
        # Target sequence - only the last column (overall scores) for future steps
        y_seq = data.iloc[i+seq_length:i+seq_length+forecast_horizon, -1].values
        
        X_sequences.append(X_seq)
        y_sequences.append(y_seq)
    
    return X_sequences, y_sequences

def train_test_split_sequences(X_sequences, y_sequences, test_size=0.2):
    # Determine split point
    num_sequences = len(X_sequences)
    split_idx = int(num_sequences * (1 - test_size))
    
    # Split into train and test sets
    X_train = X_sequences[:split_idx]
    y_train = y_sequences[:split_idx]
    X_test = X_sequences[split_idx:]
    y_test = y_sequences[split_idx:]
    
    return X_train, y_train, X_test, y_test

def train_forecasting_model(X_train, y_train, forecast_horizon, n_estimators=100, random_state=42):
    # Reshape input data for training
    X_train_flat = np.array([seq.flatten() for seq in X_train])
    
    # Train separate models for each step in the forecast horizon
    models = []
    for step in range(forecast_horizon):
        # Extract target values for this step
        y_train_step = np.array([seq[step] for seq in y_train])
        
        # Train model
        model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
        model.fit(X_train_flat, y_train_step)
        models.append(model)
    
    print(f"Trained {forecast_horizon} models for forecasting overall scores")
    return models

def generate_forecasts(models, X_test):
    num_test_sequences = len(X_test)
    forecast_horizon = len(models)
    
    # Prepare flattened input
    X_test_flat = np.array([seq.flatten() for seq in X_test])
    
    # Generate forecasts
    forecasts = []
    for i in range(num_test_sequences):
        forecast = np.zeros(forecast_horizon)
        for step in range(forecast_horizon):
            forecast[step] = models[step].predict([X_test_flat[i]])[0]
        forecasts.append(forecast)
    
    return forecasts

def evaluate_forecasts(forecasts, y_test):
    """Evaluate forecasting performance."""
    all_actual = []
    all_predicted = []
    
    for i in range(len(forecasts)):
        forecast = forecasts[i]
        actual = y_test[i]
        
        all_predicted.extend(forecast)
        all_actual.extend(actual)
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(all_actual, all_predicted),
        'precision': precision_score(all_actual, all_predicted, zero_division=0),
        'recall': recall_score(all_actual, all_predicted, zero_division=0),
        'f1': f1_score(all_actual, all_predicted, zero_division=0)
    }
    
    return metrics

def visualize_forecast_comparison(forecasts, y_test, num_to_show=5):
    num_to_show = min(num_to_show, len(forecasts))
    
    for i in range(num_to_show):
        forecast = forecasts[i]
        actual = y_test[i]
        
        forecast_horizon = len(forecast)
        steps = range(1, forecast_horizon + 1)
        
        plt.figure(figsize=(10, 6))
        plt.plot(steps, actual, 'bo-', label='Actual')
        plt.plot(steps, forecast, 'ro-', label='Forecast')
        plt.title(f'Overall Score Forecast vs Actual (Sequence {i+1})')
        plt.xlabel('Forecast Step')
        plt.ylabel('Overall Score (Binary)')
        plt.yticks([0, 1])
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'overall_score_comparison_{i+1}.png')
        plt.close()
        
def visualize_all_forecasts(forecasts, y_test):
    forecast_horizon = len(forecasts[0])
    steps = range(1, forecast_horizon + 1)
    
    # Calculate accuracy at each step
    accuracy_by_step = []
    for step in range(forecast_horizon):
        step_actual = [y_test[i][step] for i in range(len(y_test))]
        step_pred = [forecasts[i][step] for i in range(len(forecasts))]
        accuracy = accuracy_score(step_actual, step_pred)
        accuracy_by_step.append(accuracy)
    
    plt.figure(figsize=(10, 6))
    plt.plot(steps, accuracy_by_step, 'go-')
    plt.title('Forecast Accuracy by Time Step')
    plt.xlabel('Forecast Step')
    plt.ylabel('Accuracy')
    plt.ylim(0, 1)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('forecast_accuracy_by_step.png')
    plt.close()

def main():
    # Load data
    file_path = '../../../data/complete.csv'
    data = load_data(file_path)
    
    # Get the name of the last column (overall score)
    score_column = data.columns[-1]
    print(f"Forecasting target column: {score_column}")
    
    # Parameters
    sequence_length = 500  # Use 500 rows as input
    forecast_horizon = 10   # Forecast next 10 overall scores
    
    try:
        # Create sequence datasets
        X_sequences, y_sequences = create_sequence_datasets(
            data, seq_length=sequence_length, forecast_horizon=forecast_horizon
        )
        
        # Split into training and testing sets
        X_train, y_train, X_test, y_test = train_test_split_sequences(X_sequences, y_sequences)
        print(f"Training on {len(X_train)} sequences, testing on {len(X_test)} sequences")
        
        # Train models
        models = train_forecasting_model(X_train, y_train, forecast_horizon)
        
        # Generate forecasts
        forecasts = generate_forecasts(models, X_test)
        
        # Evaluate forecasting performance
        metrics = evaluate_forecasts(forecasts, y_test)
        
        print("\nForecasting Performance Metrics:")
        for metric_name, metric_value in metrics.items():
            print(f"{metric_name.capitalize()}: {metric_value:.4f}")
        
        # Visualize some forecasts vs actual
        visualize_forecast_comparison(forecasts, y_test)
        
        # Visualize accuracy by forecast step
        visualize_all_forecasts(forecasts, y_test)
        
        # Output example forecast
        if forecasts:
            print("\nExample forecast (overall scores for first test sequence):")
            print(forecasts[0])
            
            print("\nCorresponding actual values:")
            print(y_test[0])
            
    except ValueError as e:
        # For debugging
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Reduce sequence length if dataset is too small
        if "Not enough data" in str(e):
            print("\nToo small dataset")

if __name__ == "__main__":
    main()