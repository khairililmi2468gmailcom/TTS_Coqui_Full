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
<<<<<<< HEAD
  const [warning, setWarning] = useState(false);

  const [model, setModel] = useState("xtts"); // "xtts" or "bark"
  const [modelActive, setModelActive] = useState(false);
  const [isModelLoading, setIsModelLoading] = useState(false);
  const [xttsStatus, setXttsStatus] = useState(false);
  const [barkStatus, setBarkStatus] = useState(false);
  const [isXttsLoading, setIsXttsLoading] = useState(false);
  const [isBarkLoading, setIsBarkLoading] = useState(false);
  // Fetch status on load to check model status

  const API_URL_8000 = process.env.REACT_APP_API_URL_8000;
  const API_URL_8001 = process.env.REACT_APP_API_URL_8001;

  const fetchModelStatus = async () => {
    try {
      const xttsResponse = await axios.get(`${API_URL_8000}/status`);
      const barkResponse = await axios.get(`${API_URL_8001}/status`);
      setXttsStatus(xttsResponse.data.active);
      setBarkStatus(barkResponse.data.active);
    } catch (error) {
      console.error("Error fetching model status:", error);
    }
  };


  const toggleModel = async (model) => {
    const isActive = model === "xtts" ? xttsStatus : barkStatus;
    const setLoading = model === "xtts" ? setIsXttsLoading : setIsBarkLoading;
    const setStatus = model === "xtts" ? setXttsStatus : setBarkStatus;
    const url = model === "xtts" ? API_URL_8000 : API_URL_8001;

    setLoading(true);
    try {
      if (isActive) {
        await axios.post(`${url}/stop-model`);
        setStatus(false);
      } else {
        await axios.post(`${url}/start-model`);
        setStatus(true);
      }
      if (model === "xtts") {
        fetchSpeakers();
        fetchLanguages();
        fetchFiles();
      }
    } catch (error) {
      console.error(`Error toggling ${model}:`, error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModelStatus();
  }, []);



  useEffect(() => {
    if (model === "xtts") {
      fetchSpeakers();
      fetchLanguages();
      fetchFiles();
    }
  }, [model]);

  const fetchSpeakers = () => {
    fetch(`${API_URL_8000}/speakers`)
=======

  const API_URL = process.env.REACT_APP_API_URL;

  useEffect(() => {
    fetchSpeakers();
    fetchLanguages();
    fetchFiles();
  }, []);

  const fetchSpeakers = () => {
    fetch(`${API_URL}/speakers`)
>>>>>>> 2c3d9cf169fc27cd8c127ed2d6d5c28e0919d0c7
      .then((response) => response.json())
      .then((data) => setSpeakers(data))
      .catch((error) => console.error("Error fetching speakers:", error));
  };

  const fetchLanguages = () => {
<<<<<<< HEAD
    fetch(`${API_URL_8000}/languages`)
=======
    fetch(`${API_URL}/languages`)
>>>>>>> 2c3d9cf169fc27cd8c127ed2d6d5c28e0919d0c7
      .then((response) => response.json())
      .then((data) => setLanguages(data))
      .catch((error) => console.error("Error fetching languages:", error));
  };

  const fetchFiles = () => {
<<<<<<< HEAD
    fetch(`${API_URL_8000}/list-files`)
=======
    fetch(`${API_URL}/list-files`)
>>>>>>> 2c3d9cf169fc27cd8c127ed2d6d5c28e0919d0c7
      .then((response) => response.json())
      .then((data) => setFiles(Array.isArray(data) ? data : []))
      .catch((error) => console.error("Error fetching files:", error));
  };

  const handleSpeak = () => {
<<<<<<< HEAD
    if (model === "xtts" && !speaker) {
      setWarning(true);
      return;
    }
    setWarning(false);

    const websocketUrl =
      model === "bark"
        ? `${API_URL_8001}/ws/bark`
        : `${API_URL_8000}/ws/tts`;

    const ws = new WebSocket(websocketUrl);
    ws.onopen = () => {
      const payload = model === "bark"
        ? { text: message }
        : { text: message, language, speaker };
      ws.send(JSON.stringify(payload));
=======
    const ws = new WebSocket(`${API_URL}/ws/tts`);

    ws.onopen = () => {
      ws.send(JSON.stringify({ text: message, language, speaker }));
>>>>>>> 2c3d9cf169fc27cd8c127ed2d6d5c28e0919d0c7
      setIsLoading(true);
    };

    ws.onmessage = (event) => {
      const audioBlob = new Blob([event.data], { type: "audio/wav" });
      const audioUrl = URL.createObjectURL(audioBlob);
      setAudioUrl(audioUrl);
      setIsLoading(false);
    };

<<<<<<< HEAD
    ws.onerror = () => {
      console.error("WebSocket error");
      setIsLoading(false);
    };
=======
    ws.onerror = () => setIsLoading(false);
>>>>>>> 2c3d9cf169fc27cd8c127ed2d6d5c28e0919d0c7

    ws.onclose = () => console.log("WebSocket connection closed");
  };

<<<<<<< HEAD

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

    axios.post(`${API_URL_8000}/upload-sample/`, formData, {
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
    fetch(`${API_URL_8000}/delete-file`, {
=======
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
>>>>>>> 2c3d9cf169fc27cd8c127ed2d6d5c28e0919d0c7
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_name: fileName }),
    })
      .then(() => fetchFiles())
      .catch((error) => alert(`Error deleting file: ${error.message}`));
  };

  return (
<<<<<<< HEAD
    <>
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-r from-blue-500 to-purple-500 text-white">
        <div className="bg-white text-gray-800 shadow-lg rounded-xl w-full max-w-3xl p-8 space-y-6">
          <h1 className="text-3xl font-bold text-center">Text-to-Speech App</h1>
          <div className="flex justify-between items-center space-x-4">
            {/** XTTS Switch */}

            <div className="space-y-6">
              {/* XTTS Toggle Button */}
              <div className="flex items-center justify-between">
                <span className="text-lg font-medium">XTTS Model</span>
                <label className="inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={xttsStatus}
                    onChange={() => toggleModel("xtts")}
                    disabled={isXttsLoading}
                  />
                  <div className="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                  <span className="ms-3 text-sm font-medium text-gray-900 dark:text-gray-300">
                    {isXttsLoading ? "Loading..." : xttsStatus ? "Active" : "Inactive"}
                  </span>
                </label>
              </div>
              {isXttsLoading && (
                <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                  <div className="bg-blue-600 h-2.5 rounded-full animate-pulse" style={{ width: "100%" }}></div>
                </div>
              )}

              {/* Bark Toggle Button */}
              <div className="flex items-center justify-between">
                <span className="text-lg font-medium">Bark Model</span>
                <label className="inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={barkStatus}
                    onChange={() => toggleModel("bark")}
                    disabled={isBarkLoading}
                  />
                  <div className="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                  <span className="ms-3 text-sm font-medium text-gray-900 dark:text-gray-300">
                    {isBarkLoading ? "Loading..." : barkStatus ? "Active" : "Inactive"}
                  </span>
                </label>
              </div>
              {isBarkLoading && (
                <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                  <div className="bg-blue-600 h-2.5 rounded-full animate-pulse" style={{ width: "100%" }}></div>
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-center">
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="xtts">XTTS V2</option>
              <option value="bark">BARK</option>
            </select>
          </div>

          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Enter your text here..."
            className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          {model === "xtts" && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="" disabled hidden>
                  Select the language
                </option>
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
                <option value="" disabled hidden>
                  Select the speaker
                </option>
                {Object.entries(speakers).map(([key, alias]) => (
                  <option key={key} value={key}>
                    {alias}
                  </option>
                ))}
              </select>
            </div>
          )}

          {warning && model === "xtts" && (
            <p className="text-red-500 text-center">Please select a speaker before proceeding.</p>
          )}

          <div className="flex justify-between space-x-4">
            <button
              onClick={handleSpeak}
              disabled={isLoading || (model === "xtts" && !speaker)}
              className={`w-full py-2 px-4 rounded-lg text-white font-bold ${isLoading || (model === "xtts" && !speaker)
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-blue-500 hover:bg-blue-600"
                }`}
            >
              {isLoading ? "Processing..." : "Speak"}
            </button>

            {model === "xtts" && (
              <button
                onClick={() => setIsModalOpen(true)}
                className="w-full py-2 px-4 rounded-lg bg-green-500 hover:bg-green-600 text-white font-bold"
              >
                Upload Sample
              </button>
            )}
          </div>

          {audioUrl && (
            <audio controls src={audioUrl} className="w-full mt-4 rounded-lg" />
          )}

          {isModalOpen && model === "xtts" && (
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

          {model === "xtts" && (
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
          )}
        </div>
      </div>
    </>
=======
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
>>>>>>> 2c3d9cf169fc27cd8c127ed2d6d5c28e0919d0c7
  );
};

export default App;
