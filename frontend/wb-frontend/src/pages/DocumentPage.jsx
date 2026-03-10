import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import api from "../api/api";

export default function DocumentPage() {
  const { id } = useParams();
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDocument = async () => {
      try {
        const res = await api.get(`/documents/${id}`);
        setDocument(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDocument();
  }, [id]);

  if (loading) return <p>Loading...</p>;
  if (!document) return <p>Document not found</p>;

  return (
    <div>
      <h2>{document.title}</h2>
      <a href={document.url} target="_blank" rel="noreferrer">
        Original URL
      </a>
      <div style={{ marginTop: "1rem" }}>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {document.markdown_content}
        </ReactMarkdown>
      </div>
      <hr />
      <Link to="/">Back to Dashboard</Link>
    </div>
  );
}