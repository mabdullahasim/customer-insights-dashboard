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

  const handleActionChange = (newAction: Action) => {
    setAction(newAction);
    if(newAction == "Sign Up"){

    }
    // Clear inputs on action change if needed
    setUsername("");
    setEmail("");
    setPassword("");
  };

  const handleSubmit = () => {
    if (action === "Sign Up") {
      console.log("Sign Up Clicked", { username, email, password });
    } else {
      console.log("Login Clicked", { email, password });
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.text}>{action}</div>
        <div className={styles.underline}></div>
      </div>

      <div className={styles.inputs}>
        {action === "Sign Up" && (
          <div className={styles.input}>
            <img src={user_icon} alt="user icon" />
            <input
              type="text"
              placeholder="Name"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
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
          />
        </div>

        <div className={styles.input}>
          <img src={password_icon} alt="password icon" />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
      </div>

      <div className={styles["forgot-password"] }style={{ display: action === "Login" ? "block" : "none" }}>Forgot Password</div>

      <div className={styles["submit-container"]}>
        <div
          className={action === "Sign Up" ? `${styles.submit} ${styles.active}` : styles.submit}
          onClick={() => {
            handleActionChange("Sign Up");
            handleSubmit();
          }}
        >
          Sign Up
        </div>

        <div
          className={action === "Login" ? `${styles.submit} ${styles.active}` : styles.submit}
          onClick={() => {
            handleActionChange("Login");
            handleSubmit();
          }}
        >
          Login
        </div>
      </div>
    </div>
  );
};

export default Login;