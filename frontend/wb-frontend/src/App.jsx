// src/App.jsx
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import ChatPage from "./pages/ChatPage";
import DocumentPage from "./pages/DocumentPage";

function App() {
  return (
    <BrowserRouter>
      <div className="app-header">
        <h1>WB Research Helper</h1>
        <nav>
          <Link to="/">Dashboard</Link> | <Link to="/chatpage">Chatbot</Link>
        </nav>
      </div>

      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/chatpage" element={<ChatPage />} />
        <Route path="/documents/:id" element={<DocumentPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;