import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Load the dataset
data_path = '../../../data/complete.csv'
column_names = [f"Test_{i+1}" for i in range(10)] + ["Outcome"]
df = pd.read_csv(data_path, header=None, names=column_names)

# Separate features and target
X = df.drop(columns=["Outcome"])  # Features
y = df["Outcome"]  # Target

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Initialize the Naive Bayes classifier
classifier = GaussianNB()

# Train the model
classifier.fit(X_train, y_train)

# Make predictions
y_pred = classifier.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")

# Generate the classification report and extract precision, recall, and F1 score
report = classification_report(y_test, y_pred, output_dict=True)

# Print only accuracy, precision, recall, and F1-score
print(f"Precision: {report['1']['precision']:.2f}")
print(f"Recall: {report['1']['recall']:.2f}")
print(f"F1 Score: {report['1']['f1-score']:.2f}")