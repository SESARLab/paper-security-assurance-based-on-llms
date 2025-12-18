import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings
warnings.filterwarnings("ignore")

def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

def create_sequence_datasets(data, seq_length=1000, forecast_horizon=10):
    # Total number of rows in dataset
    total_rows = len(data)
    
    # Need at least seq_length + forecast_horizon rows
    if total_rows < seq_length + forecast_horizon:
        raise ValueError(f"Need at least {seq_length + forecast_horizon} rows.")
    
    # Calculate number of complete sequences we can create
    num_sequences = total_rows - seq_length - forecast_horizon + 1
    
    print(f"Creating {num_sequences} sequences of length {seq_length} with {forecast_horizon} forecast horizon")
    
    X_sequences = []
    y_sequences = []
    
    for i in range(num_sequences):
        # Input sequence
        X_seq = data.iloc[i:i+seq_length, :-1].values  # All columns except last, as numpy array
        # Target sequence (rows to forecast)
        y_seq = data.iloc[i+seq_length:i+seq_length+forecast_horizon, :-1].values
        
        X_sequences.append(X_seq)
        y_sequences.append(y_seq)
    
    return X_sequences, y_sequences, data.columns[:-1]

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

def train_forecasting_model(X_train, y_train, n_estimators=100, random_state=42):
    # Reshape input data for training
    # Each row will be a flattened 1000-row sequence
    X_train_flat = np.array([seq.flatten() for seq in X_train])
    
    # Prepare target data (first row of each target sequence)
    # We'll train separate models for each step in the forecast horizon
    num_features = y_train[0].shape[1]
    forecast_horizon = y_train[0].shape[0]
    
    models = []
    for step in range(forecast_horizon):
        step_models = []
        for feature in range(num_features):
            # Extract target values for this step and feature
            y_train_step_feature = np.array([seq[step, feature] for seq in y_train])
            
            # Train model
            model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
            model.fit(X_train_flat, y_train_step_feature)
            step_models.append(model)
        models.append(step_models)
    
    print(f"Trained {forecast_horizon} steps × {num_features} features = {forecast_horizon * num_features} models")
    return models

def generate_forecasts(models, X_test):
    num_test_sequences = len(X_test)
    forecast_horizon = len(models)
    num_features = len(models[0])
    
    # Prepare flattened input
    X_test_flat = np.array([seq.flatten() for seq in X_test])
    
    # Generate forecasts
    forecasts = []
    for i in range(num_test_sequences):
        forecast = np.zeros((forecast_horizon, num_features))
        for step in range(forecast_horizon):
            for feature in range(num_features):
                forecast[step, feature] = models[step][feature].predict([X_test_flat[i]])[0]
        forecasts.append(forecast)
    
    return forecasts

def evaluate_forecasts(forecasts, y_test):
    all_actual = []
    all_predicted = []
    
    for i in range(len(forecasts)):
        forecast = forecasts[i]
        actual = y_test[i]
        
        # Flatten for metrics calculation
        all_predicted.extend(forecast.flatten())
        all_actual.extend(actual.flatten())
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(all_actual, all_predicted),
        'precision': precision_score(all_actual, all_predicted, zero_division=0),
        'recall': recall_score(all_actual, all_predicted, zero_division=0),
        'f1': f1_score(all_actual, all_predicted, zero_division=0)
    }
    
    return metrics

def visualize_forecast_comparison(forecasts, y_test, feature_names, num_to_show=3):
    num_to_show = min(num_to_show, len(forecasts))
    
    for i in range(num_to_show):
        forecast = forecasts[i]
        actual = y_test[i]
        
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))
        
        # Create heatmaps
        axes[0].imshow(forecast, cmap='Blues', aspect='auto')
        axes[0].set_title(f'Forecasted Sequence {i+1}')
        axes[0].set_yticks(range(forecast.shape[0]))
        axes[0].set_yticklabels([f'Step {j+1}' for j in range(forecast.shape[0])])
        axes[0].set_xticks(range(len(feature_names)))
        axes[0].set_xticklabels(feature_names, rotation=90)
        
        axes[1].imshow(actual, cmap='Blues', aspect='auto')
        axes[1].set_title(f'Actual Sequence {i+1}')
        axes[1].set_yticks(range(actual.shape[0]))
        axes[1].set_yticklabels([f'Step {j+1}' for j in range(actual.shape[0])])
        axes[1].set_xticks(range(len(feature_names)))
        axes[1].set_xticklabels(feature_names, rotation=90)
        
        plt.tight_layout()
        plt.savefig(f'sequence_comparison_{i+1}.png')
        plt.close()

def main():
    # Load data
    file_path = '../../../data/complete.csv'
    data = load_data(file_path)
    
    # Parameters
    sequence_length = 500  # Use 1000 rows as input
    forecast_horizon = 1   # Forecast next 10 rows
    
    try:
        # Create sequence datasets
        X_sequences, y_sequences, feature_names = create_sequence_datasets(
            data, seq_length=sequence_length, forecast_horizon=forecast_horizon
        )
        
        # Split into training and testing sets
        X_train, y_train, X_test, y_test = train_test_split_sequences(X_sequences, y_sequences)
        print(f"Training on {len(X_train)} sequences, testing on {len(X_test)} sequences")
        
        # Train models
        models = train_forecasting_model(X_train, y_train)
        
        # Generate forecasts
        forecasts = generate_forecasts(models, X_test)
        
        # Evaluate forecasting performance
        metrics = evaluate_forecasts(forecasts, y_test)
        
        print("\nForecasting Performance Metrics:")
        for metric_name, metric_value in metrics.items():
            print(f"{metric_name.capitalize()}: {metric_value:.4f}")
        
        # Visualize some forecasts vs actual
        visualize_forecast_comparison(forecasts, y_test, feature_names)
        
        # Output example forecast
        if forecasts:
            print("\nExample forecast (first 3 rows of first test sequence):")
            print(forecasts[0][:3])
            
            print("\nCorresponding actual values:")
            print(y_test[0][:3])
            
    except ValueError as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        if "Not enough data" in str(e):
            print("\nToo small dataset")

if __name__ == "__main__":
    main()