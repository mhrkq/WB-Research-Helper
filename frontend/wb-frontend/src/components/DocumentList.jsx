import "../App.css";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/api";

export default function DocumentList() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const res = await api.get("/documents");
      setDocuments(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const filteredDocuments = documents.filter((doc) => {
    const title = doc.title || ""; // fallback to empty string
    const url = doc.url || "";
    return (
      title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      url.toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  return (
    <div>
      {/* Search + Refresh */}
      <div className="document-controls">
        <input
          type="text"
          placeholder="Search documents..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="document-search"
        />
        <button onClick={loadDocuments} className="refresh-button">
          Refresh
        </button>
      </div>

      {/* Documents list */}
      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul className="document-list">
          {filteredDocuments.map((doc) => (
            <li key={doc.id}>
              {doc.title || "(No Title)"} — <Link to={`/documents/${doc.id}`}>View</Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}