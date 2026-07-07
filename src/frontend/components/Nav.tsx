import { NavLink, useNavigate, useLocation } from "react-router-dom";
import { useTheme } from "../components/useTheme";
import styles from "./Nav.module.css";
import {
  LayoutDashboard,
  BarChart3,
  FileText,
  Upload,
  Settings,
  Sun,
  Moon,
  LogOut,
  TrendingUp,
} from "lucide-react";

const navItems = [
  { to: "/dashboard", label: "Dashboard", Icon: LayoutDashboard },
  { to: "/analytics", label: "Analytics", Icon: BarChart3 },
  { to: "/reports", label: "Reports", Icon: FileText },
  { to: "/uploads", label: "Upload", Icon: Upload },
  { to: "/settings", label: "Settings", Icon: Settings },
];

const Nav = () => {
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  function handleLogout(e: React.MouseEvent) {
    e.preventDefault();
    localStorage.removeItem("token");
    navigate("/login", { replace: true });
  }

  return (
    <aside className={styles.sidebar}>
      {/* Brand */}
      <NavLink to="/dashboard" className={styles.brand}>
        <div className={styles.brandIcon}>
          <TrendingUp size={22} color="#fff" strokeWidth={2.2} />
        </div>
        <div>
          <div className={styles.brandName}>Insightly</div>
          <div className={styles.brandSub}>CUSTOMER INSIGHTS</div>
        </div>
      </NavLink>

      {/* Menu label */}
      <div className={styles.menuLabel}>MENU</div>

      {/* Nav links */}
      <nav className={styles.nav}>
        {navItems.map(({ to, label, Icon }) => {
          const active = location.pathname === to;
          return (
            <NavLink
              key={to}
              to={to}
              className={`${styles.navLink} ${active ? styles.navLinkActive : ""}`}
            >
              <Icon size={19} />
              <span>{label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className={styles.footer}>
        <button className={styles.themeBtn} onClick={toggleTheme}>
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          <span>{theme === "dark" ? "Light mode" : "Dark mode"}</span>
        </button>
        <a href="#" className={styles.logoutLink} onClick={handleLogout}>
          <LogOut size={18} />
          <span>Log out</span>
        </a>
      </div>
    </aside>
  );
};

export default Nav;