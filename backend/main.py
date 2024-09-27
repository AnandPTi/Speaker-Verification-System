import os
import numpy as np
import librosa
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras import layers, models
from tensorflow.keras.models import load_model
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment

app = FastAPI()
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
# Configure CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to extract spectrogram features from an audio file
def extract_features(file_path, n_mels=128, n_fft=2048, hop_length=512):
    signal, sr = librosa.load(file_path, sr=None)
    mel_spec = librosa.feature.melspectrogram(
        y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels
    )
    log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
    return log_mel_spec

# Load dataset
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

class SpeakerIdentificationModel:
    def __init__(self, data_path="samples"):
        self.data_path = data_path
        self.model = self._build_model()

    def _build_model(self):
        X, y = load_data(self.data_path)
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)

        # Data split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42
        )
        X_train = np.expand_dims(X_train, axis=-1)
        X_test = np.expand_dims(X_test, axis=-1)

        # Build CNN model
        model = models.Sequential([
            layers.Conv2D(32, (3, 3), activation="relu", input_shape=X_train[0].shape),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation="relu"),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(128, (3, 3), activation="relu"),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dense(len(label_encoder.classes_), activation="softmax")
        ])

        model.compile(
            optimizer="adam", 
            loss="sparse_categorical_crossentropy", 
            metrics=["accuracy"]
        )
        return model

    def train(self, epochs=10, batch_size=32):
        X, y = load_data(self.data_path)
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42
        )
        X_train = np.expand_dims(X_train, axis=-1)
        X_test = np.expand_dims(X_test, axis=-1)

        self.model.fit(
            X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, y_test)
        )

    def evaluate(self):
        X, y = load_data(self.data_path)
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)

        _, X_test, _, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42
        )
        X_test = np.expand_dims(X_test, axis=-1)

        test_loss, test_acc = self.model.evaluate(X_test, y_test)
        print(f"Test accuracy: {test_acc}")

    def save_model(self, file_path="speaker_identification_model.h5"):
        self.model.save(file_path)


# Function to split and save audio files
def split_audio(input_file, person_name, output_folder="samples", segment_duration=2000):
    output_folder = f"{output_folder}/{person_name}"
    os.makedirs(output_folder, exist_ok=True)

    audio = AudioSegment.from_wav(input_file)
    total_duration = len(audio)
    num_segments = total_duration // segment_duration

    for i in range(num_segments):
        start_time = i * segment_duration
        end_time = (i + 1) * segment_duration
        segment = audio[start_time:end_time]
        output_file = os.path.join(output_folder, f"{i}.wav")
        segment.export(output_file, format="wav")
    
    return num_segments


def predict_person():
    model = load_model("speaker_identification_model.h5")
    sample_file_path = "test/0.wav"
    sample_features = extract_features(sample_file_path)
    sample_features = np.expand_dims(sample_features, axis=-1)
    sample_features = np.expand_dims(sample_features, axis=0)

    predictions = model.predict(sample_features)
    predicted_speaker_index = np.argmax(predictions)

    X, y = load_data("samples")
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    predicted_speaker = label_encoder.inverse_transform([predicted_speaker_index])[0]
    return predicted_speaker


@app.post("/record_audio_train")
async def record_audio_train(file: UploadFile, person_name: str = Form(...)):
    file_path = f"training_set/sample.wav"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    split_audio(file_path, person_name, output_folder="samples")
    return {"message": "File saved and split successfully"}


@app.post("/record_audio_test")
async def record_audio_test(file: UploadFile, person_name: str = Form(...)):
    file_path = f"testing_set/sample.wav"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    split_audio(file_path, person_name, output_folder="test")
    return {"message": "File saved and split successfully"}


@app.post("/train_model")
async def train_model_():
    model = SpeakerIdentificationModel()
    model.train()
    model.evaluate()
    model.save_model()
    return {"message": "Model trained successfully"}


@app.post("/test_model")
async def test_model():
    predicted_person = predict_person()
    return {"speaker": predicted_person}

# import os
# import numpy as np
# import librosa
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder
# from tensorflow.keras import layers, models
# from tensorflow.keras.models import load_model
# from fastapi import FastAPI
# from scipy.io.wavfile import read
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi import FastAPI, UploadFile
# from fastapi import Form
# from fastapi import UploadFile, Form
# from fastapi import FastAPI, UploadFile
# from fastapi.middleware.cors import CORSMiddleware
# from pydub import AudioSegment
# import os
# import librosa



# app = FastAPI()


# origins = [
#     "*",
# ]

# # Add middlewares to the origins
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # Function to extract spectrogram features from audio file
# def extract_features(file_path, n_mels=128, n_fft=2048, hop_length=512):

#     # Load the audio file using librosa
#     signal, sr = librosa.load(file_path, sr=None)

#     # Extract Mel spectrogram features
#     mel_spec = librosa.feature.melspectrogram(
#         y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels
#     )

#     # Convert to log scale
#     log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)

#     # Return the log Mel spectrogram features
#     return log_mel_spec

#     # Define a function to load data from the given path


# def load_data(path):

#     # Define a function to load data from the given path
#     features = []
#     labels = []

#     # Loop through each speaker folder
#     for speaker_folder in os.listdir(path):

#         # Path to the speaker folder
#         speaker_path = os.path.join(path, speaker_folder)

#         # Loop through each audio file in the speaker folder
#         for audio_file in os.listdir(speaker_path):

#             # Path to the audio file
#             file_path = os.path.join(speaker_path, audio_file)

#             # Extract features from the audio file
#             features.append(extract_features(file_path))

#             # Append the speaker label
#             labels.append(speaker_folder)

#     # Convert the lists to numpy arrays
#     return np.array(features), np.array(labels)


# class SpeakerIdentificationModel:
#     def __init__(self, data_path="samples"):
#         self.data_path = data_path
#         self.model = self._build_model()

#     def _build_model(self):
#         # Load data
#         X, y = load_data(self.data_path)

#         # Encode labels
#         label_encoder = LabelEncoder()
#         y_encoded = label_encoder.fit_transform(y)

#         # Split data into training and test sets
#         X_train, X_test, y_train, y_test = train_test_split(
#             X, y_encoded, test_size=0.2, random_state=42
#         )

#         # Add channel dimension for CNN
#         X_train = np.expand_dims(X_train, axis=-1)
#         X_test = np.expand_dims(X_test, axis=-1)

#         # Build CNN model
#         model = models.Sequential(
#             [
#                 layers.Conv2D(
#                     32, (3, 3), activation="relu", input_shape=X_train[0].shape
#                 ),
#                 layers.MaxPooling2D((2, 2)),
#                 layers.Conv2D(64, (3, 3), activation="relu"),
#                 layers.MaxPooling2D((2, 2)),
#                 layers.Conv2D(128, (3, 3), activation="relu"),
#                 layers.MaxPooling2D((2, 2)),
#                 layers.Flatten(),
#                 layers.Dense(128, activation="relu"),
#                 layers.Dense(len(label_encoder.classes_), activation="softmax"),
#             ]
#         )

#         # Compile model
#         model.compile(
#             optimizer="adam",
#             loss="sparse_categorical_crossentropy",
#             metrics=["accuracy"],
#         )

#         return model

#     def train(self, epochs=10, batch_size=32):
#         # Load data
#         X, y = load_data(self.data_path)

#         # Encode labels
#         label_encoder = LabelEncoder()
#         y_encoded = label_encoder.fit_transform(y)

#         # Split data into training and test sets
#         X_train, X_test, y_train, y_test = train_test_split(
#             X, y_encoded, test_size=0.2, random_state=42
#         )

#         # Add channel dimension for CNN
#         X_train = np.expand_dims(X_train, axis=-1)
#         X_test = np.expand_dims(X_test, axis=-1)

#         # Train model
#         self.model.fit(
#             X_train,
#             y_train,
#             epochs=epochs,
#             batch_size=batch_size,
#             validation_data=(X_test, y_test),
#         )

#     def evaluate(self):
#         # Load data
#         X, y = load_data(self.data_path)

#         # Encode labels
#         label_encoder = LabelEncoder()
#         y_encoded = label_encoder.fit_transform(y)

#         # Split data into training and test sets
#         X_train, X_test, y_train, y_test = train_test_split(
#             X, y_encoded, test_size=0.2, random_state=42
#         )

#         # Add channel dimension for CNN
#         X_train = np.expand_dims(X_train, axis=-1)
#         X_test = np.expand_dims(X_test, axis=-1)

#         # Evaluate model
#         test_loss, test_acc = self.model.evaluate(X_test, y_test)
#         print(f"Test accuracy: {test_acc}")

#     def save_model(self, file_path="speaker_identification_model.h5"):
#         self.model.save(file_path)


# def save_file(input_file, person_name):
#     # Input .wav file

#     # Output folder to save the segments
#     output_folder = f"samples/{person_name}"
#     os.makedirs(output_folder, exist_ok=True)

#     # Load the audio file
#     audio = AudioSegment.from_wav(input_file)

#     # Duration of each segment in milliseconds (0.01 seconds)
#     segment_duration = 2000

#     # Total duration of the audio in milliseconds
#     total_duration = len(audio)

#     # Calculate the number of segments
#     num_segments = total_duration // segment_duration

#     # Split the audio into segments
#     for i in range(num_segments):
#         # Calculate the start and end time of the segment
#         start_time = i * segment_duration
#         end_time = (i + 1) * segment_duration

#         # Extract the segment
#         segment = audio[start_time:end_time]

#         # Save the segment to a new .wav file
#         output_file = os.path.join(output_folder, f"{i}.wav")
#         segment.export(output_file, format="wav")

#     print(f"Split {input_file} into {num_segments} segments in {output_folder}.")


# def save_file_test(input_file, person_name):
#     # Input .wav file

#     # Output folder to save the segments
#     output_folder = f"test/"
#     os.makedirs(output_folder, exist_ok=True)

#     # Load the audio file
#     audio = AudioSegment.from_wav(input_file)

#     # Duration of each segment in milliseconds (0.01 seconds)
#     segment_duration = 2000

#     # Total duration of the audio in milliseconds
#     total_duration = len(audio)

#     # Calculate the number of segments
#     num_segments = total_duration // segment_duration

#     # Split the audio into segments
#     for i in range(num_segments):
#         # Calculate the start and end time of the segment
#         start_time = i * segment_duration
#         end_time = (i + 1) * segment_duration

#         # Extract the segment
#         segment = audio[start_time:end_time]

#         if i == 0:

#             # Save the segment to a new .wav file
#             output_file = os.path.join(output_folder, f"{i}.wav")
#             segment.export(output_file, format="wav")

#         break


# def predict_person():

#     # Load the saved model
#     model = load_model("speaker_identification_model.h5")

#     # Function to extract spectrogram features from audio file
#     def extract_features(file_path, n_mels=128, n_fft=2048, hop_length=512):
#         signal, sr = librosa.load(file_path, sr=None)
#         mel_spec = librosa.feature.melspectrogram(
#             y=signal, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels
#         )
#         log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
#         return log_mel_spec

#     # Example audio file for prediction
#     sample_file_path = "test/0.wav"
#     sample_features = extract_features(sample_file_path)
#     sample_features = np.expand_dims(
#         sample_features, axis=-1
#     )  # Add channel dimension for CNN
#     sample_features = np.expand_dims(sample_features, axis=0)  # Add batch dimension

#     # Make prediction
#     predictions = model.predict(sample_features)
#     predicted_speaker_index = np.argmax(predictions)
#     print(predictions)
#     # Load data
#     data_path = "samples"
#     X, y = load_data(data_path)

#     # Encode labels
#     label_encoder = LabelEncoder()
#     y_encoded = label_encoder.fit_transform(y)
#     predicted_speaker = label_encoder.inverse_transform([predicted_speaker_index])[0]
#     print("Predicted Speaker:", predicted_speaker)
#     return predicted_speaker


# @app.post("/record_audio_train")
# async def record_audio_train(
#     file: UploadFile,
#     person_name: str = Form(...),
# ):
#     print(person_name)
#     try:
#         file_path = f"training_set/sample.wav"
#         with open(file_path, "wb") as f:
#             file_content = await file.read()
#             print(file_content)
#             f.write(file_content)
#             f.close()

#         save_file(file_path, person_name)

#         return {"message": "File saved successfully"}
#     except Exception as e:
#         return {"message": e.args}


# @app.post("/record_audio_test")
# async def record_audio_train(
#     file: UploadFile,
#     person_name: str = Form(...),
# ):
#     print(person_name)
#     try:

#         # Save the file as sample.wav file.
#         file_path = f"testing_set/sample.wav"

#         # Write the file content to the sample.wav file.
#         with open(file_path, "wb") as f:

#             # Read the file content.
#             file_content = await file.read()
#             print(file_content)
#             f.write(file_content)

#             # Close the file.
#             f.close()

#         # Save the file.
#         save_file_test(file_path, person_name)
#         return {"message": "File saved successfully"}
#     except Exception as e:
#         return {"message": e.args}


# @app.post("/train_model")
# async def train_model_():

#     # Usage
#     model = SpeakerIdentificationModel()
#     model.train()
#     model.evaluate()
#     model.save_model()
#     return {"message": "Model trained successfully"}


# @app.post("/test_model")
# async def predict_person_():

#     predicted_person = predict_person()

#     return {"speaker": predicted_person}
