import React, { useState } from "react";
import axios from "axios";

const TextToSpeechComponent = () => {
    const [text, setText] = useState("");
    const [audioSrc, setAudioSrc] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleTextToSpeech = async () => {
        setLoading(true);
        setError(null);
        setAudioSrc(null);

        try {
            const response = await axios.post(`${process.env.REACT_APP_API_URL}/tts`, {
                model_path: "dummy_model.onnx", // Ganti dengan path model yang sesuai
                text,
            });

            if (response.data.audio) {
                setAudioSrc(`data:audio/wav;base64,${response.data.audio}`);
            }
        } catch (err) {
            setError(err.response?.data?.error || "An error occurred");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-xl mx-auto mt-10 p-6 bg-white shadow-md rounded-md">
            <h2 className="text-2xl font-semibold text-gray-700 mb-4">
                Text-to-Speech
            </h2>
            <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Enter text to convert to speech"
                className="w-full h-32 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
            />
            <button
                onClick={handleTextToSpeech}
                disabled={loading || !text}
                className={`w-full py-2 px-4 text-white font-semibold rounded-md transition ${
                    loading || !text
                        ? "bg-gray-400 cursor-not-allowed"
                        : "bg-blue-500 hover:bg-blue-600"
                }`}
            >
                {loading ? "Processing..." : "Convert to Speech"}
            </button>
            {error && <p className="mt-4 text-red-500">{error}</p>}
            {audioSrc && (
                <div className="mt-6">
                    <h3 className="text-xl font-semibold text-gray-700 mb-2">
                        Generated Audio
                    </h3>
                    <audio controls src={audioSrc} className="w-full" />
                </div>
            )}
        </div>
    );
};

export default TextToSpeechComponent;
