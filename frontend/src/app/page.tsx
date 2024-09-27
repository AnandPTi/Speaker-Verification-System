"use client";

import React, { ChangeEvent, useState } from "react";
import axios from "axios";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [personName, setPersonName] = useState<string>("");
  const [result, setResult] = useState<string>("");
  const [status, setStatus] = useState<string>(""); // For displaying action statuses

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
      setStatus("File selected");
    }
  };

  const handlePersonNameChange = (event: ChangeEvent<HTMLInputElement>) => {
    setPersonName(event.target.value);
  };

  const handleSubmit = async () => {
    if (!file || !personName) {
      alert("Please select a file and enter a person name.");
      return;
    }

    try {
      setStatus("Uploading...");
      const formData = new FormData();
      formData.append("file", file);
      formData.append("person_name", personName);

      await axios.post("http://localhost:8000/record_audio_train", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setStatus("File uploaded and training started!");
    } catch (error) {
      console.error("Error saving file:", error);
      setStatus("Error during upload");
    }
  };

  const handleSubmitTest = async () => {
    if (!file) {
      return;
    }

    try {
      setStatus("Testing...");
      const formData = new FormData();
      formData.append("file", file);
      formData.append("person_name", "sample.wav");

      await axios.post("http://localhost:8000/record_audio_test", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setStatus("Test file uploaded successfully!");
    } catch (error) {
      console.error("Error uploading test file:", error);
      setStatus("Error during testing");
    }
  };

  const handleTrain = async () => {
    try {
      setStatus("Training model...");
      await axios.post("http://localhost:8000/train_model");
      setStatus("Model trained successfully!");
    } catch (error) {
      console.error("Error training model:", error);
      setStatus("Error during training");
    }
  };

  const handleShowOutput = async () => {
    try {
      setStatus("Fetching output...");
      const response = await axios.post("http://localhost:8000/test_model");
      if (response.status === 200) {
        console.log(response.data.speaker);
        setResult(response.data.speaker);
        setStatus("Output ready!");
      }
    } catch (error) {
      console.error("Error getting output:", error);
      setStatus("Error fetching output");
    }
  };

  return (
    <>
      <div className="flex flex-col items-center justify-center bg-gradient-to-br from-green-800 to-black h-screen w-screen p-5">
        <div className="text-4xl font-bold text-white mb-10">Speaker Identification System</div>

        {/* Status display */}
        <div className="text-lg font-medium text-yellow-300 mb-4">{status}</div>

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

        {/* File Upload Section */}
        <div className="flex flex-col items-center space-y-6 mb-10">
          <div className="text-lg font-medium text-white">Upload audio file for training/test</div>
          <input type="file" id="fileUpload" onChange={handleFileChange} className="hidden" />
          <label
            htmlFor="fileUpload"
            className="bg-green-400 text-black py-3 px-6 rounded-lg cursor-pointer hover:bg-green-300 transition duration-300 ease-in-out"
          >
            Upload File
          </label>
        </div>

        {/* Action buttons */}
        <div className="flex justify-center space-x-6 mb-10">
          <button
            onClick={handleSubmit}
            className="bg-white text-black py-3 px-8 rounded-lg hover:bg-gray-200 transition duration-300 ease-in-out"
          >
            Submit for Training
          </button>
          <button
            onClick={handleTrain}
            className="bg-white text-black py-3 px-8 rounded-lg hover:bg-gray-200 transition duration-300 ease-in-out"
          >
            Train Model
          </button>
        </div>

        {/* Test Section */}
        <div className="text-lg font-medium text-white mb-4">Test Model</div>
        <div className="flex flex-col items-center space-y-6 mb-10">
          <div className="text-lg font-medium text-white">Upload audio file for testing</div>
          <input type="file" id="testFileUpload" onChange={handleFileChange} className="hidden" />
          <label
            htmlFor="testFileUpload"
            className="bg-orange-400 text-black py-3 px-6 rounded-lg cursor-pointer hover:bg-orange-300 transition duration-300 ease-in-out"
          >
            Upload Test File
          </label>
        </div>

        <button
          onClick={handleSubmitTest}
          className="bg-white text-black py-3 px-8 rounded-lg hover:bg-gray-200 transition duration-300 ease-in-out mb-4"
        >
          Submit Test
        </button>

        {/* Show Output */}
        <button
          onClick={handleShowOutput}
          className="bg-blue-500 text-white py-3 px-8 rounded-lg hover:bg-blue-400 transition duration-300 ease-in-out"
        >
          Show Output
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

//***************best************************************************ */
// "use client";

// import React, { ChangeEvent, useState } from "react";
// import axios from "axios";

// export default function Home() {
//   const [trainFile, setTrainFile] = useState<File | null>(null);
//   const [testFile, setTestFile] = useState<File | null>(null);
//   const [personName, setPersonName] = useState<string>("");
//   const [result, setResult] = useState<string>("");
//   const [loading, setLoading] = useState<boolean>(false);

//   const handleTrainFileChange = (event: ChangeEvent<HTMLInputElement>) => {
//     if (event.target.files && event.target.files[0]) {
//       setTrainFile(event.target.files[0]);
//     }
//   };

//   const handleTestFileChange = (event: ChangeEvent<HTMLInputElement>) => {
//     if (event.target.files && event.target.files[0]) {
//       setTestFile(event.target.files[0]);
//     }
//   };

//   const handlePersonNameChange = (event: ChangeEvent<HTMLInputElement>) => {
//     setPersonName(event.target.value);
//   };

//   const handleSubmitTrain = async () => {
//     if (!trainFile || !personName) {
//       alert("Please select a training file and enter a person name.");
//       return;
//     }

//     try {
//       setLoading(true);
//       const formData = new FormData();
//       formData.append("file", trainFile);
//       formData.append("person_name", personName);

//       await axios.post("http://localhost:8000/record_audio_train", formData, {
//         headers: {
//           "Content-Type": "multipart/form-data",
//         },
//       });
//       alert("Training data submitted successfully.");
//     } catch (error) {
//       console.error("Error saving file:", error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleSubmitTest = async () => {
//     if (!testFile) {
//       alert("Please upload a test file.");
//       return;
//     }

//     try {
//       setLoading(true);
//       const formData = new FormData();
//       formData.append("file", testFile);
//       formData.append("person_name", "sample.wav");

//       await axios.post("http://localhost:8000/record_audio_test", formData, {
//         headers: {
//           "Content-Type": "multipart/form-data",
//         },
//       });
//       alert("Test data submitted successfully.");

//       // Call handleOutput to fetch the result after the test data is submitted
//       await handleOutput();
//     } catch (error) {
//       console.error("Error saving file:", error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleOutput = async () => {
//     try {
//       setLoading(true);
//       const response = await axios.post("http://localhost:8000/test_model");
//       if (response.status === 200) {
//         console.log(response.data.speaker);
//         setResult(response.data.speaker);
//       }
//     } catch (error) {
//       console.error("Error getting output:", error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleTrainModel = async () => {
//     try {
//       setLoading(true);
//       await axios.post("http://localhost:8000/train_model");
//       alert("Model trained successfully.");
//     } catch (error) {
//       console.error("Error training model:", error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <>
//       <div className="flex flex-col items-center justify-center bg-gradient-to-br from-blue-800 to-black h-screen w-screen p-5">
//         <div className="text-4xl font-bold text-white mb-10">Speaker Identification System</div>

//         {/* Input for person's name */}
//         <div className="w-full max-w-md mb-8">
//           <label htmlFor="personName" className="block text-lg font-medium text-white mb-2">
//             Enter the person's name
//           </label>
//           <input
//             type="text"
//             id="personName"
//             className="block w-full p-3 rounded-md border border-gray-300 shadow-sm focus:outline-none focus:border-indigo-500"
//             placeholder="Person's Name"
//             value={personName}
//             onChange={handlePersonNameChange}
//           />
//         </div>

//         {/* Upload for training file */}
//         <div className="flex flex-col items-center space-y-6 mb-10">
//           <div className="text-lg font-medium text-white">Upload audio file for training</div>
//           <input type="file" id="trainFileUpload" onChange={handleTrainFileChange} className="hidden" />
//           <label htmlFor="trainFileUpload" className="bg-white text-black py-3 px-6 rounded-lg cursor-pointer hover:bg-gray-200 transition duration-300 ease-in-out">
//             Upload Training File
//           </label>
//           {trainFile && <p className="text-white">Selected file: {trainFile.name}</p>}
//         </div>

//         {/* Buttons */}
//         <div className="flex justify-center space-x-6 mb-10">
//           <button onClick={handleSubmitTrain} className="bg-white text-black py-3 px-8 rounded-lg hover:bg-gray-200 transition duration-300 ease-in-out">
//             Submit Train Data
//           </button>
//           <button onClick={handleTrainModel} className="bg-white text-black py-3 px-8 rounded-lg hover:bg-gray-200 transition duration-300 ease-in-out">
//             Train Model
//           </button>
//         </div>

//         {/* Upload for test file */}
//         <div className="text-lg font-medium text-white mb-4">Test Model</div>
//         <div className="flex flex-col items-center space-y-6 mb-10">
//           <div className="text-lg font-medium text-white">Upload audio file for testing</div>
//           <input type="file" id="testFileUpload" onChange={handleTestFileChange} className="hidden" />
//           <label htmlFor="testFileUpload" className="bg-white text-black py-3 px-6 rounded-lg cursor-pointer hover:bg-gray-200 transition duration-300 ease-in-out">
//             Upload Test File
//           </label>
//           {testFile && <p className="text-white">Selected file: {testFile.name}</p>}
//         </div>

//         {/* Submit Test and Output */}
//         <button onClick={handleSubmitTest} className="bg-white text-black py-3 px-8 rounded-lg hover:bg-gray-200 transition duration-300 ease-in-out">
//           Submit Test
//         </button>

//         {loading && <p className="text-white mt-4">Processing...</p>}

//         {result && (
//           <div className="mt-8">
//             <div className="text-xl font-semibold text-white mb-2">Predicted Speaker:</div>
//             <div className="text-2xl font-bold text-white text-center">{result}</div>
//           </div>
//         )}
//       </div>
//     </>
//   );
// }

// "use client";

// import React, { ChangeEvent, useState } from "react";
// import axios from "axios";

// export default function Home() {
//   const [trainFile, setTrainFile] = useState<File | null>(null);
//   const [testFile, setTestFile] = useState<File | null>(null);
//   const [personName, setPersonName] = useState<string>("");
//   const [result, setResult] = useState<string>("");
//   const [loading, setLoading] = useState<boolean>(false);

//   const handleTrainFileChange = (event: ChangeEvent<HTMLInputElement>) => {
//     if (event.target.files && event.target.files[0]) {
//       setTrainFile(event.target.files[0]);
//     }
//   };

//   const handleTestFileChange = (event: ChangeEvent<HTMLInputElement>) => {
//     if (event.target.files && event.target.files[0]) {
//       setTestFile(event.target.files[0]);
//     }
//   };

//   const handlePersonNameChange = (event: ChangeEvent<HTMLInputElement>) => {
//     setPersonName(event.target.value);
//   };

//   const handleSubmitTrain = async () => {
//     if (!trainFile || !personName) {
//       alert("Please select a training file and enter a person name.");
//       return;
//     }

//     try {
//       setLoading(true);
//       const formData = new FormData();
//       formData.append("file", trainFile);
//       formData.append("person_name", personName);

//       await axios.post("http://localhost:8000/record_audio_train", formData, {
//         headers: {
//           "Content-Type": "multipart/form-data",
//         },
//       });
//       alert("Training data submitted successfully.");
//     } catch (error) {
//       console.error("Error saving file:", error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleSubmitTest = async () => {
//     if (!testFile) {
//       alert("Please upload a test file.");
//       return;
//     }

//     try {
//       setLoading(true);
//       const formData = new FormData();
//       formData.append("file", testFile);
//       formData.append("person_name", "sample.wav");

//       await axios.post("http://localhost:8000/record_audio_test", formData, {
//         headers: {
//           "Content-Type": "multipart/form-data",
//         },
//       });
//       alert("Test data submitted successfully.");
//     } catch (error) {
//       console.error("Error saving file:", error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleOutput = async () => {
//     try {
//       setLoading(true);
//       const response = await axios.post("http://localhost:8000/test_model");
//       if (response.status === 200) {
//         console.log(response.data.speaker);
//         setResult(response.data.speaker);
//       }
//     } catch (error) {
//       console.error("Error getting output:", error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleTrainModel = async () => {
//     try {
//       setLoading(true);
//       await axios.post("http://localhost:8000/train_model");
//       alert("Model trained successfully.");
//     } catch (error) {
//       console.error("Error training model:", error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <>
//       <div className="flex flex-col items-center justify-center bg-gradient-to-br from-blue-800 to-black h-screen w-screen p-5">
//         <div className="text-4xl font-bold text-white mb-10">Speaker Identification System</div>

//         {/* Input for person's name */}
//         <div className="w-full max-w-md mb-8">
//           <label htmlFor="personName" className="block text-lg font-medium text-white mb-2">
//             Enter the person's name
//           </label>
//           <input
//             type="text"
//             id="personName"
//             className="block w-full p-3 rounded-md border border-gray-300 shadow-sm focus:outline-none focus:border-indigo-500"
//             placeholder="Person's Name"
//             value={personName}
//             onChange={handlePersonNameChange}
//           />
//         </div>

//         {/* Upload for training file */}
//         <div className="flex flex-col items-center space-y-6 mb-10">
//           <div className="text-lg font-medium text-white">Upload audio file for training</div>
//           <input type="file" id="trainFileUpload" onChange={handleTrainFileChange} className="hidden" />
//           <label htmlFor="trainFileUpload" className="bg-white text-black py-3 px-6 rounded-lg cursor-pointer hover:bg-gray-200 transition duration-300 ease-in-out">
//             Upload Training File
//           </label>
//           {trainFile && <p className="text-white">Selected file: {trainFile.name}</p>}
//         </div>

//         {/* Buttons */}
//         <div className="flex justify-center space-x-6 mb-10">
//           <button onClick={handleSubmitTrain} className="bg-white text-black py-3 px-8 rounded-lg hover:bg-gray-200 transition duration-300 ease-in-out">
//             Submit Train Data
//           </button>
//           <button onClick={handleTrainModel} className="bg-white text-black py-3 px-8 rounded-lg hover:bg-gray-200 transition duration-300 ease-in-out">
//             Train Model
//           </button>
//         </div>

//         {/* Upload for test file */}
//         <div className="text-lg font-medium text-white mb-4">Test Model</div>
//         <div className="flex flex-col items-center space-y-6 mb-10">
//           <div className="text-lg font-medium text-white">Upload audio file for testing</div>
//           <input type="file" id="testFileUpload" onChange={handleTestFileChange} className="hidden" />
//           <label htmlFor="testFileUpload" className="bg-white text-black py-3 px-6 rounded-lg cursor-pointer hover:bg-gray-200 transition duration-300 ease-in-out">
//             Upload Test File
//           </label>
//           {testFile && <p className="text-white">Selected file: {testFile.name}</p>}
//         </div>

//         {/* Submit Test and Output */}
//         <button onClick={handleOutput} className="bg-white text-black py-3 px-8 rounded-lg hover:bg-gray-200 transition duration-300 ease-in-out">
//           Submit Test
//         </button>

//         {loading && <p className="text-white mt-4">Processing...</p>}

//         {result && (
//           <div className="mt-8">
//             <div className="text-xl font-semibold text-white mb-2">Predicted Speaker:</div>
//             <div className="text-2xl font-bold text-white text-center">{result}</div>
//           </div>
//         )}
//       </div>
//     </>
//   );
// }

// "use client";

// import React, { ChangeEvent, useState } from "react";
// import axios from "axios";

// export default function Home() {
//   const [file, setFile] = useState<File | null>(null);
//   const [personName, setPersonName] = useState<string>("");
//   const [personNameTest, setPersonNameTest] = useState<string>("");

//   const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
//     if (event.target.files && event.target.files[0]) {
//       setFile(event.target.files[0]);
//     }
//   };

//   const handlePersonNameChange = (event: ChangeEvent<HTMLInputElement>) => {
//     setPersonName(event.target.value);
//   };

//   const handlePersonNameChangeTest = (event: ChangeEvent<HTMLInputElement>) => {
//     setPersonNameTest(event.target.value);
//   };

//   const handleSubmit = async () => {
//     if (!file || !personName) {
//       alert("Please select a file and enter a person name.");
//       return;
//     }

//     try {
//       const formData = new FormData();
//       formData.append("file", file);
//       formData.append("person_name", personName);

//       await axios.post("http://localhost:8000/record_audio_train", formData, {
//         headers: {
//           "Content-Type": "multipart/form-data",
//         },
//       });
//     } catch (error) {
//       console.error("Error saving file:", error);
//     }
//   };

//   const handleSubmitTest = async () => {
//     if (!file) {
//       return;
//     }

//     try {
//       const formData = new FormData();
//       formData.append("file", file);
//       formData.append("person_name", "sample.wav");

//       await axios.post("http://localhost:8000/record_audio_test", formData, {
//         headers: {
//           "Content-Type": "multipart/form-data",
//         },
//       });
//     } catch (error) {
//       console.error("Error saving file:", error);
//     }
//   };

//   const [result, setResult] = useState<string>("");

//   const handleOutput = async () => {
//     try {
//       const response = await axios.post("http://localhost:8000/test_model");
//       if (response.status === 200) {
//         console.log(response.data.speaker);
//         setResult(response.data.speaker);
//       }
//     } catch (error) {
//       console.error("Error getting output:", error);
//     }
//   };

//   const handleTrain = async () => {
//     try {
//       await axios.post("http://localhost:8000/train_model");
//     } catch (error) {
//       console.error("Error training model:", error);
//     }
//   };

//   return (
//     <>
//       <div className="flex flex-col items-center justify-center bg-gradient-to-br from-blue-800 to-black h-screen w-screen p-5">
//         <div className="text-4xl font-bold text-white mb-10">Speaker Identification System</div>

//         <div className="w-full max-w-md mb-8">
//           <label htmlFor="personName" className="block text-lg font-medium text-white mb-2">
//             Enter the person's name
//           </label>
//           <input
//             type="text"
//             id="personName"
//             className="block w-full p-3 rounded-md border border-gray-300 shadow-sm focus:outline-none focus:border-indigo-500"
//             placeholder="Person's Name"
//             value={personName}
//             onChange={handlePersonNameChange}
//           />
//         </div>

//         <div className="flex flex-col items-center space-y-6 mb-10">
//           <div className="text-lg font-medium text-white">Upload audio file for training/test</div>
//           <input type="file" id="fileUpload" onChange={handleFileChange} className="hidden" />
//           <label htmlFor="fileUpload" className="bg-white text-black py-3 px-6 rounded-lg cursor-pointer hover:bg-gray-200 transition duration-300 ease-in-out">
//             Upload File
//           </label>
//         </div>

//         <div className="flex justify-center space-x-6 mb-10">
//           <button onClick={handleSubmit} className="bg-white text-black py-3 px-8 rounded-lg hover:bg-gray-200 transition duration-300 ease-in-out">
//             Submit
//           </button>
//           <button onClick={handleTrain} className="bg-white text-black py-3 px-8 rounded-lg hover:bg-gray-200 transition duration-300 ease-in-out">
//             Train Model
//           </button>
//         </div>

//         <div className="text-lg font-medium text-white mb-4">Test Model</div>
//         <div className="flex flex-col items-center space-y-6 mb-10">
//           <div className="text-lg font-medium text-white">Upload audio file for testing</div>
//           <input type="file" id="testFileUpload" onChange={handleFileChange} className="hidden" />
//           <label htmlFor="testFileUpload" className="bg-white text-black py-3 px-6 rounded-lg cursor-pointer hover:bg-gray-200 transition duration-300 ease-in-out">
//             Upload File
//           </label>
//         </div>

//         <button onClick={handleSubmitTest} className="bg-white text-black py-3 px-8 rounded-lg hover:bg-gray-200 transition duration-300 ease-in-out">
//           Submit Test
//         </button>

//         {result && (
//           <div className="mt-8">
//             <div className="text-xl font-semibold text-white mb-2">Predicted Speaker:</div>
//             <div className="text-2xl font-bold text-white text-center">{result}</div>
//           </div>
//         )}
//       </div>
//     </>
//   );
// }
