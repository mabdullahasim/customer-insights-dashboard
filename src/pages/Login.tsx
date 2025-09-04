import { useState } from "react";
import { Link } from "react-router-dom"; // for navigation
import password_icon from "../assets/password.png";
import email_icon from "../assets/email.png";
import styles from "./Login.module.css";

const Login = () => {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log("Login submitted:", { email, password });
    // You can call your login API here
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.text}>Login</div>
        <div className={styles.underline}></div>
      </div>

      <form className={styles.inputs} onSubmit={handleSubmit}>
        <div className={styles.input}>
          <img src={email_icon} alt="email icon" />
          <input
            type="email"
            placeholder="Email"
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
