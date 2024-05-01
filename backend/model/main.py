from tensorflow.keras.models import load_model
import librosa
import numpy as np
import os
import numpy as np
import librosa
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras import layers, models


# Function to extract spectrogram features from audio file
def extract_features(file_path, n_mels=128, n_fft=2048, hop_length=512):
    signal, sr = librosa.load(file_path, sr=None)
    mel_spec = librosa.feature.melspectrogram(
        y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels
    )
    log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
    return log_mel_spec

# Define a function to load data from the given path
def load_data(path):
    features = []
    labels = []
    for speaker_folder in os.listdir(path):
        speaker_path = os.path.join(path, speaker_folder)
        for audio_file in os.listdir(speaker_path):
            file_path = os.path.join(speaker_path, audio_file)
            features.append(extract_features(file_path))
            labels.append(speaker_folder)
    return np.array(features), np.array(labels)


# Load data
data_path = "test_samples"
X, y = load_data(data_path)

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

# Add channel dimension for CNN
X_train = np.expand_dims(X_train, axis=-1)
X_test = np.expand_dims(X_test, axis=-1)

# Build CNN model
model = models.Sequential(
    [
        layers.Conv2D(32, (3, 3), activation="relu", input_shape=X_train[0].shape),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation="relu"),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(128, (3, 3), activation="relu"),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(128, activation="relu"),
        layers.Dense(len(label_encoder.classes_), activation="softmax"),
    ]
)

# Compile model
model.compile(
    optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
)

for i in range(5):
    # Train model
    model.fit(
        X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test)
    )

    # Evaluate model
    test_loss, test_acc = model.evaluate(X_test, y_test)
    print(f"Test accuracy: {test_acc}")

# Evaluate and print final accuracy
final_test_loss, final_test_acc = model.evaluate(X_test, y_test)
print(f"Final test accuracy: {final_test_acc}")
# Save the model
model.save("speaker_identification_model.h5")



# Load the saved model
model = load_model('speaker_identification_model.h5')

# Function to extract spectrogram features from audio file
def extract_features(file_path, n_mels=128, n_fft=2048, hop_length=512):
    signal, sr = librosa.load(file_path, sr=None)
    mel_spec = librosa.feature.melspectrogram(y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels)
    log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
    return log_mel_spec

# Example audio file for prediction
sample_file_path = "test_samples/Jens_Stoltenberg/1.wav"
sample_features = extract_features(sample_file_path)
sample_features = np.expand_dims(sample_features, axis=-1)  # Add channel dimension for CNN
sample_features = np.expand_dims(sample_features, axis=0)   # Add batch dimension

# Make prediction
predictions = model.predict(sample_features)
predicted_speaker_index = np.argmax(predictions)
print(predictions)
predicted_speaker = label_encoder.inverse_transform([predicted_speaker_index])[0]
print("Predicted Speaker:", predicted_speaker)