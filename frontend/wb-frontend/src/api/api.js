import axios from "axios";

const api = axios.create({
  baseURL: "/api", // Vite proxy to backend
  timeout: 5000,
});

export default api;