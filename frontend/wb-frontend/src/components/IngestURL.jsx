import { useState } from "react";
import api from "../api/api";

export default function IngestURL() {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState("");

  const handleIngest = async () => {
    if (!url.trim()) {
      setStatus("Please enter a URL.");
      return;
    }

    try {
      setStatus("Ingesting...");
      const res = await api.post("/ingest", { url });

      const { status: ingestionStatus, document_id, chunks } = res.data;

      setStatus(
        `Ingestion ${ingestionStatus}! Document ID: ${document_id}, Chunks: ${chunks}`
      );
      setUrl("");
    } catch (err) {
      console.error(err);
      const msg =
        err.response?.data?.detail ||
        err.message ||
        "Failed to ingest URL";
      setStatus(msg);
    }
  };

  return (
    <div className="ingest-container">
      <input
        type="text"
        value={url}
        placeholder="Enter URL"
        onChange={(e) => setUrl(e.target.value)}
        className="ingest-input"
      />
      <button onClick={handleIngest} className="ingest-button">
        Upload
      </button>
      <p className={`ingest-status ${status.includes("Failed") ? "error" : "success"}`}>
        {status}
      </p>
    </div>
  );
}