import React, { useState, useEffect } from "react";
import "./index.css";
import axios from 'axios';

const App = () => {
  const [message, setMessage] = useState("");
  const [language, setLanguage] = useState("en");
  const [speaker, setSpeaker] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [speakers, setSpeakers] = useState({});
  const [languages, setLanguages] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [file, setFile] = useState(null);
  const [speakerName, setSpeakerName] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [files, setFiles] = useState([]);

  const API_URL = process.env.REACT_APP_API_URL;

  useEffect(() => {
    fetchSpeakers();
    fetchLanguages();
    fetchFiles();
  }, []);

  const fetchSpeakers = () => {
    fetch(`${API_URL}/speakers`)
      .then((response) => response.json())
      .then((data) => setSpeakers(data))
      .catch((error) => console.error("Error fetching speakers:", error));
  };

  const fetchLanguages = () => {
    fetch(`${API_URL}/languages`)
      .then((response) => response.json())
      .then((data) => setLanguages(data))
      .catch((error) => console.error("Error fetching languages:", error));
  };

  const fetchFiles = () => {
    fetch(`${API_URL}/list-files`)
      .then((response) => response.json())
      .then((data) => setFiles(Array.isArray(data) ? data : []))
      .catch((error) => console.error("Error fetching files:", error));
  };

  const handleSpeak = () => {
    const ws = new WebSocket(`${API_URL}/ws/tts`);

    ws.onopen = () => {
      ws.send(JSON.stringify({ text: message, language, speaker }));
      setIsLoading(true);
    };

    ws.onmessage = (event) => {
      const audioBlob = new Blob([event.data], { type: "audio/wav" });
      const audioUrl = URL.createObjectURL(audioBlob);
      setAudioUrl(audioUrl);
      setIsLoading(false);
    };

    ws.onerror = () => setIsLoading(false);

    ws.onclose = () => console.log("WebSocket connection closed");
  };

  const handleUpload = () => {
  if (!speakerName || !file) {
    alert("Speaker name and file are required!");
    return;
  }

  const formData = new FormData();
  formData.append("speaker_name", speakerName.trim().replace(/\s+/g, "_").toLowerCase());
  formData.append("file", file);

  setIsUploading(true);
  setUploadProgress(0);

  axios.post(`${API_URL}/upload-sample/`, formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total) {
        const percent = Math.round((progressEvent.loaded / progressEvent.total) * 100);
        setUploadProgress(percent);
      }
    }
  })
    .then(() => {
      setIsUploading(false);
      fetchSpeakers();
      fetchFiles();
      setIsModalOpen(false);
      setSpeakerName("");
      setFile(null);
    })
    .catch(() => setIsUploading(false));
};
  const handleDelete = (fileName) => {
    fetch(`${API_URL}/delete-file`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_name: fileName }),
    })
      .then(() => fetchFiles())
      .catch((error) => alert(`Error deleting file: ${error.message}`));
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-r from-blue-500 to-purple-500 text-white">
      <div className="bg-white text-gray-800 shadow-lg rounded-xl w-full max-w-3xl p-8 space-y-6">
        <h1 className="text-3xl font-bold text-center">Text-to-Speech App</h1>

        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Enter your text here..."
          className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {Object.entries(languages).map(([code, name]) => (
              <option key={code} value={code}>
                {name}
              </option>
            ))}
          </select>
          <select
            value={speaker}
            onChange={(e) => setSpeaker(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {Object.entries(speakers).map(([key, alias]) => (
              <option key={key} value={key}>
                {alias}
              </option>
            ))}
          </select>
        </div>

        <div className="flex justify-between space-x-4">
          <button
            onClick={handleSpeak}
            disabled={isLoading}
            className={`w-full py-2 px-4 rounded-lg text-white font-bold ${
              isLoading
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-blue-500 hover:bg-blue-600"
            }`}
          >
            {isLoading ? "Processing..." : "Speak"}
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="w-full py-2 px-4 rounded-lg bg-green-500 hover:bg-green-600 text-white font-bold"
          >
            Upload Sample
          </button>
        </div>

        {audioUrl && (
          <audio controls src={audioUrl} className="w-full mt-4 rounded-lg" />
        )}

        {isModalOpen && (
          <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md space-y-4">
              <h2 className="text-lg font-bold">Upload New Speaker</h2>
              <input
                type="text"
                placeholder="Speaker Name"
                value={speakerName}
                onChange={(e) => setSpeakerName(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="file"
                accept="audio/wav"
                onChange={(e) => setFile(e.target.files[0])}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />

              {isUploading && (
		  <div className="mt-4">
		    <div className="relative w-full h-4 bg-gray-200 rounded-lg">
		      <div
			className="absolute top-0 left-0 h-4 bg-blue-500 rounded-lg"
			style={{ width: `${uploadProgress}%` }}
		      />
		    </div>
		    <p className="text-center mt-2">{uploadProgress}%</p>
		  </div>
		)}

              <div className="flex justify-between space-x-4">
                <button
                  onClick={handleUpload}
                  className="w-full py-2 px-4 rounded-lg bg-blue-500 hover:bg-blue-600 text-white font-bold"
                >
                  Upload
                </button>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="w-full py-2 px-4 rounded-lg bg-red-500 hover:bg-red-600 text-white font-bold"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        <div>
          <h3 className="text-lg font-bold">Speaker Files</h3>
          <ul className="space-y-2">
            {files.map((file) => (
              <li
                key={file}
                className="flex justify-between items-center bg-gray-100 p-3 rounded-lg"
              >
                <span>{file}</span>
                <button
                  onClick={() => handleDelete(file)}
                  className="py-1 px-3 bg-red-500 hover:bg-red-600 text-white rounded-lg"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default App;
