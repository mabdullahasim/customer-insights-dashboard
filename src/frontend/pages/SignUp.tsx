import { useState } from "react";
import user_icon from "../assets/person.png";
import email_icon from "../assets/email.png";
import password_icon from "../assets/password.png";
import styles from "./SignUp.module.css";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function SignUp() {
  // State for inputs
  const [username, setUsername] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const navigate = useNavigate();
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://localhost:8000/auth/signUp", {
        username,
        email,
        password,
      });

      navigate("/login");
    }
    catch (err: any) {
      console.error("Signup failed:", err.response?.data || err.message);
      alert(err.response?.data?.detail || "Signup failed. Please try again.");
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.text}>Sign Up</div>
        <div className={styles.underline}></div>
      </div>

      <form className={styles.inputs} onSubmit={handleSubmit}>
        <div className={styles.input}>
          <img src={user_icon} alt="user" />
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        <div className={styles.input}>
          <img src={email_icon} alt="email" />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className={styles.input}>
          <img src={password_icon} alt="password" />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <div className={styles["submit-container"]}>
          <button type="submit" className={styles.submit}>
            Sign Up
          </button>
        </div>

        <p className={styles.switch}>
          Already have an account? <a href="/login">Login</a>
        </p>
      </form>
    </div>
  );
}

export default SignUp;