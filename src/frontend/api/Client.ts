
//api client so we can read the token and set the token on eevery request
//on 401 clears the token and sends to /login
import axios from "axios";

const api =axios.create({baseURL: "http://127.0.0.1:8000"})

api.interceptors.request.use((cfg) =>{
    const token = localStorage.getItem("token");
    if (token) cfg.headers.Authorization = `Bearer ${token}`;
    return cfg;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;