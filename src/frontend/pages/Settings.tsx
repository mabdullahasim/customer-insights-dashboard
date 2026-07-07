import { useState, useEffect } from "react";
import styles from "./Settings.module.css";
import Header from "../components/Header";
import Nav from "../components/Nav";
import { useTheme } from "../components/useTheme";
import api from "../api/Client";
import { User, Mail, Lock, Eye, Check } from "lucide-react";

interface UserInfo {
  username: string;
  email: string;
}

const Settings = () => {
  const { theme, toggleTheme } = useTheme();
  const [user, setUser] = useState<UserInfo | null>(null);
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [toast, setToast] = useState("");

  useEffect(() => {
    api.get("/users/me").then((res) => {
      setUser(res.data);
      setEmail(res.data.email);
    }).catch(() => {});
  }, []);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(""), 3500);
  };

  const savePw = async () => {
    if (!pw) { showToast("Please enter a new password."); return; }
    try {
      await api.post("/users/forgotPassword", { email, password: pw });
      showToast("Password updated successfully.");
      setPw("");
    } catch (err: any) {
      showToast(err.response?.data?.detail || "Password update failed.");
    }
  };

  const setTheme = (t: "light" | "dark") => {
    if (theme !== t) toggleTheme();
  };

  const userInitials = user ? user.username.slice(0, 2).toUpperCase() : "??";

  return (
    <div className={styles.container}>
      <Nav />
      <Header title="Settings" subtitle="Manage your account and preferences." />
      <main className={styles.main}>

        {toast && (
          <div className={styles.toast}><Check size={18} strokeWidth={2.4} />{toast}</div>
        )}

        {/* Account info */}
        <div className={styles.card}>
          <div className={styles.cardTitle}>Account information</div>
          <div className={styles.accountHeader}>
            <div className={styles.bigAvatar}>{userInitials}</div>
            <div>
              <div className={styles.accountName}>{user?.username ?? "..."}</div>
              <div className={styles.accountRole}>Customer Insights Analyst</div>
            </div>
          </div>
          <div className={styles.fieldGrid}>
            <div>
              <label className={styles.fieldLabel}>USERNAME</label>
              <div className={styles.readonlyField}>
                <User size={17} color="var(--muted)" />
                <span>{user?.username ?? "..."}</span>
              </div>
            </div>
            <div>
              <label className={styles.fieldLabel}>EMAIL</label>
              <div className={styles.readonlyField}>
                <Mail size={17} color="var(--muted)" />
                <span>{user?.email ?? "..."}</span>
              </div>
            </div>
          </div>
        </div>

        <div className={styles.twoCol}>
          {/* Appearance */}
          <div className={styles.card}>
            <div className={styles.cardTitle}>Appearance</div>
            <div className={styles.cardSub}>Choose how the dashboard looks.</div>
            <div className={styles.themeRow}>
              <button className={`${styles.themeCard} ${theme === "light" ? styles.themeCardActive : ""}`} onClick={() => setTheme("light")}>
                <div className={styles.themePreviewLight}>
                  <div className={styles.previewSidebar} style={{ background: "#fff", borderRight: "1px solid #d5daf0" }} />
                  <div className={styles.previewContent}>
                    <div className={styles.previewBar} style={{ background: "#695CFE" }} />
                    <div className={styles.previewLine} style={{ background: "#c9cde8" }} />
                  </div>
                </div>
                <span className={styles.themeLabel}>Light</span>
              </button>
              <button className={`${styles.themeCard} ${theme === "dark" ? styles.themeCardActive : ""}`} onClick={() => setTheme("dark")}>
                <div className={styles.themePreviewDark}>
                  <div className={styles.previewSidebar} style={{ background: "#1a1d29", borderRight: "1px solid #33353f" }} />
                  <div className={styles.previewContent}>
                    <div className={styles.previewBar} style={{ background: "#4f46e5" }} />
                    <div className={styles.previewLine} style={{ background: "#3a3d4a" }} />
                  </div>
                </div>
                <span className={styles.themeLabel}>Dark</span>
              </button>
            </div>
          </div>

          {/* Password */}
          <div className={styles.card}>
            <div className={styles.cardTitle}>Change password</div>
            <div className={styles.cardSub}>Update the credentials for your account.</div>
            <div className={styles.formStack}>
              <div>
                <label className={styles.fieldLabel}>EMAIL</label>
                <div className={styles.pillInput}>
                  <Mail size={17} color="var(--muted)" />
                  <input value={email} onChange={(e) => setEmail(e.target.value)} className={styles.input} />
                </div>
              </div>
              <div>
                <label className={styles.fieldLabel}>NEW PASSWORD</label>
                <div className={styles.pillInput}>
                  <Lock size={17} color="var(--muted)" />
                  <input type={showPw ? "text" : "password"} value={pw} onChange={(e) => setPw(e.target.value)} placeholder="Enter new password" className={styles.input} />
                  <button className={styles.eyeBtn} onClick={() => setShowPw((v) => !v)}><Eye size={17} /></button>
                </div>
              </div>
              <button className={styles.saveBtn} onClick={savePw}>Update password</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Settings;