import { useState } from "react";
import { Link } from "react-router-dom"; // for navigation
import password_icon from "../assets/password.png";
import user_icon from "../assets/person.png";
import styles from "./Login.module.css";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const params = new URLSearchParams();
    params.append("username", email);    // FastAPI expects `username`
    params.append("password", password);
    try{
      const res = await axios.post("http://localhost:8000/auth/token", params, {headers: { "Content-Type": "application/x-www-form-urlencoded" },});

      console.log("Login success:", res.data);
      localStorage.setItem("token", res.data.access_token); // save JWT
      navigate("/dashboard"); 
    }
     catch (err: any) {
      console.error("Login failed:", err.response?.data || err.message);
      alert("Invalid username or password");
    }
    
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.text}>Login</div>
        <div className={styles.underline}></div>
      </div>

      <form className={styles.inputs} onSubmit={handleSubmit}>
        <div className={styles.input}>
          <img src={user_icon} alt="email icon" />
          <input
            type="text"
            placeholder="Username"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className={styles.input}>
          <img src={password_icon} alt="password icon" />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <div className={styles["forgot-password"]}>Forgot Password</div>

        <div className={styles["submit-container"]}>
          <button type="submit" className={styles.submit}>
            Login
          </button>
        </div>

        <p className={styles.switch}>
          Don't have an account? <Link to="/signup">Sign Up</Link>
        </p>
      </form>
    </div>
  );
};

export default Login;
