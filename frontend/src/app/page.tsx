"use client";

import React, { ChangeEvent, useState } from "react";
import axios from "axios";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [personName, setPersonName] = useState<string>("");
  const [personNameTest, setPersonNameTest] = useState<string>("");

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
    }
  };

  const handlePersonNameChange = (event: ChangeEvent<HTMLInputElement>) => {
    setPersonName(event.target.value);
  };

  const handlePersonNameChangeTest = (event: ChangeEvent<HTMLInputElement>) => {
    setPersonNameTest(event.target.value);
  };

  const handleSubmit = async () => {
    if (!file || !personName) {
      alert("Please select a file and enter a person name.");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("person_name", personName);

      await axios.post("http://localhost:8000/record_audio_train", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
    } catch (error) {
      console.error("Error saving file:", error);
    }
  };

  const handleSubmitTest = async () => {
    if (!file) {
      return;
    }

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("person_name", "sample.wav");

      await axios.post("http://localhost:8000/record_audio_test", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
    } catch (error) {
      console.error("Error saving file:", error);
    }
  };

  const [result, setResult] = useState<string>("");

  const handleOutput = async () => {
    try {
      const response = await axios.post("http://localhost:8000/test_model");
      if (response.status === 200) {
        console.log(response.data.speaker);
        setResult(response.data.speaker);
      }
    } catch (error) {
      console.error("Error getting output:", error);
    }
  };

  const handleTrain = async () => {
    try {
      await axios.post("http://localhost:8000/train_model");
    } catch (error) {
      console.error("Error training model:", error);
    }
  };

  return (
    <>
      <div className="flex flex-col items-center justify-center bg-gradient-to-br from-blue-800 to-black h-screen w-screen p-5">
        <div className="text-4xl font-bold text-white mb-10">Speaker Identification System</div>

        <div className="w-full max-w-md mb-8">
          <label htmlFor="personName" className="block text-lg font-medium text-white mb-2">
            Enter the person's name
          </label>
          <input
            type="text"
            id="personName"
            className="block w-full p-3 rounded-md border border-gray-300 shadow-sm focus:outline-none focus:border-indigo-500"
            placeholder="Person's Name"
            value={personName}
            onChange={handlePersonNameChange}
          />
        </div>

        <div className="flex flex-col items-center space-y-6 mb-10">
          <div className="text-lg font-medium text-white">Upload audio file for training/test</div>
          <input type="file" id="fileUpload" onChange={handleFileChange} className="hidden" />
          <label htmlFor="fileUpload" className="bg-white text-black py-3 px-6 rounded-lg cursor-pointer hover:bg-gray-200 transition duration-300 ease-in-out">
            Upload File
          </label>
        </div>

        <div className="flex justify-center space-x-6 mb-10">
          <button onClick={handleSubmit} className="bg-white text-black py-3 px-8 rounded-lg hover:bg-gray-200 transition duration-300 ease-in-out">
            Submit
          </button>
          <button onClick={handleTrain} className="bg-white text-black py-3 px-8 rounded-lg hover:bg-gray-200 transition duration-300 ease-in-out">
            Train Model
          </button>
        </div>

        <div className="text-lg font-medium text-white mb-4">Test Model</div>
        <div className="flex flex-col items-center space-y-6 mb-10">
          <div className="text-lg font-medium text-white">Upload audio file for testing</div>
          <input type="file" id="testFileUpload" onChange={handleFileChange} className="hidden" />
          <label htmlFor="testFileUpload" className="bg-white text-black py-3 px-6 rounded-lg cursor-pointer hover:bg-gray-200 transition duration-300 ease-in-out">
            Upload File
          </label>
        </div>

        <button onClick={handleSubmitTest} className="bg-white text-black py-3 px-8 rounded-lg hover:bg-gray-200 transition duration-300 ease-in-out">
          Submit Test
        </button>

        {result && (
          <div className="mt-8">
            <div className="text-xl font-semibold text-white mb-2">Predicted Speaker:</div>
            <div className="text-2xl font-bold text-white text-center">{result}</div>
          </div>
        )}
      </div>
    </>
  );
}
