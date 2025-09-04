import { useState } from "react";
import user_icon from "../assets/person.png";
import password_icon from "../assets/password.png";
import email_icon from "../assets/email.png";
import styles from "./Login.module.css";

type Action = "Login" | "Sign Up";

const Login = () => {
  const [action, setAction] = useState<Action>("Login");
  const [username, setUsername] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  // Handles actual form submission
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); // stop page reload
    if (action === "Sign Up") {
      console.log("Sign Up submitted:", { username, email, password });
    } else {
      console.log("Login submitted:", { email, password });
    }
  };

  // Switches between Login and Sign Up forms
  const handleActionChange = (newAction: Action) => {
    setAction(newAction);
    setUsername("");
    setEmail("");
    setPassword("");
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.text}>{action}</div>
        <div className={styles.underline}></div>
      </div>

      {/* REAL FORM */}
      <form className={styles.inputs} onSubmit={handleSubmit}>
        {/* Username only for Sign Up */}
        {action === "Sign Up" && (
          <div className={styles.input}>
            <img src={user_icon} alt="user icon" />
            <input
              type="text"
              placeholder="Name"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
        )}

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

        {/* Forgot Password only on Login */}
        {action === "Login" && (
          <div className={styles["forgot-password"]}>Forgot Password</div>
        )}

        <div className={styles["submit-container"]}>
          {/* Switch to Sign Up */}
          <button
            type="button"
            className={action === "Sign Up" ? `${styles.submit} ${styles.active}` : styles.submit}
            onClick={() => handleActionChange("Sign Up")}
          >
            Sign Up
          </button>

          {/* Submit Login */}
          <button
            type="submit"
            className={action === "Login" ? `${styles.submit} ${styles.active}` : styles.submit}
            onClick={() => handleActionChange("Login")}
          >
            Login
          </button>
        </div>
      </form>
    </div>
  );
};

export default Login;
