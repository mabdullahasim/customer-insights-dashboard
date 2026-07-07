import { useState, useEffect, useRef } from "react";
import styles from "./Header.module.css";
import {Search, X,Bell,AlertTriangle, Check,Download,} from "lucide-react";
import api from "../api/Client";

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

interface UserInfo {
  username: string;
  email: string;
}

const Header = ({ title = "Dashboard", subtitle = "" }: HeaderProps) => {
  const [searchOpen, setSearchOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [notifOpen, setNotifOpen] = useState(false);
  const [user, setUser] = useState<UserInfo | null>(null);
  const notifRef = useRef<HTMLDivElement>(null);

useEffect(() => {
    api
      .get("/users/me")
      .then((res) => setUser(res.data))
      .catch(() => {});
  }, []);

  /* Close notification dropdown on outside click */
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setNotifOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const userInitials = user
    ? user.username.slice(0, 2).toUpperCase()
    : "??";

  return (
    <header className={styles.header}>
      <div className={styles.titleArea}>
        <div className={styles.title}>{title}</div>
        {subtitle && <div className={styles.subtitle}>{subtitle}</div>}
      </div>

      <div className={styles.actions}>
        {/* Expandable search */}
        <div
          className={styles.searchWrap}
          style={{ width: searchOpen ? 320 : 88 }}
        >
          <Search size={18} className={styles.searchIcon} />
          <input
            className={styles.searchInput}
            placeholder="Search customers, reports..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            className={styles.searchBtn}
            onClick={() => {
              setSearchOpen((v) => !v);
              if (searchOpen) setQuery("");
            }}
          >
            {searchOpen ? (
              <X size={16} strokeWidth={2.4} />
            ) : (
              <Search size={16} strokeWidth={2.4} />
            )}
          </button>
        </div>

        {/* Notifications */}
        <div ref={notifRef} style={{ position: "relative" }}>
          <button
            className={styles.notifBtn}
            onClick={() => setNotifOpen((v) => !v)}
          >
            <Bell size={20} />
            <span className={styles.notifDot} />
          </button>

          {notifOpen && (
            <div className={styles.notifDrop}>
              <div className={styles.notifTitle}>Notifications</div>
              <div className={styles.notifItem}>
                <div className={`${styles.notifChip} ${styles.notifChipDanger}`}>
                  <AlertTriangle size={16} />
                </div>
                <div>
                  <div className={styles.notifText}>
                    14 customers flagged high churn risk
                  </div>
                  <div className={styles.notifTime}>2 hours ago</div>
                </div>
              </div>
              <div className={styles.notifItem}>
                <div className={`${styles.notifChip} ${styles.notifChipPositive}`}>
                  <Check size={16} />
                </div>
                <div>
                  <div className={styles.notifText}>
                    Sentiment analysis completed
                  </div>
                  <div className={styles.notifTime}>Yesterday</div>
                </div>
              </div>
              <div className={styles.notifItem}>
                <div className={`${styles.notifChip} ${styles.notifChipAccent}`}>
                  <Download size={16} />
                </div>
                <div>
                  <div className={styles.notifText}>
                    New customer data uploaded
                  </div>
                  <div className={styles.notifTime}>2 days ago</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* User chip */}
        <div className={styles.userChip}>
          <div className={styles.userAvatar}>{userInitials}</div>
          <div className={styles.userInfo}>
            <div className={styles.userName}>
              {user ? user.username : "..."}
            </div>
            <div className={styles.userRole}>Analyst</div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;