import styles from "./Nav.module.css";
import React from "react";
import "boxicons/css/boxicons.min.css";
import { NavLink } from "react-router-dom";
import { useTheme } from "../components/useTheme";

const Nav = () => {
    const { theme, toggleTheme } = useTheme();
    return(
        <>
            <nav className= {styles.sidebar}>
                <header>
                    <div className={styles.imageText}>
                        <span className ={styles.image}>
                            <img src="" alt ="logo"></img>
                        </span>
                        <div className={styles.headerText}>
                            <span className={styles.name}>Dashboard</span>
                        </div>
                    </div>
                    <i className={`bx bx-chevron-right ${styles.toggle}`}></i>
                </header>
                <div className={styles.menuBar}>
                    <div className={styles.menu}>
                         <aside className={styles.links}>
                            <NavLink className={styles.navLink} to="/dashboard">
                                <i className ={`bx  bx-home ${styles.icons}`}  ></i>
                                <span className={styles.text}>Dashboard</span>
                            </NavLink>
                            <NavLink className={styles.navLink} to="/analytics">
                                 <i className ={`bx bx-line-chart  ${styles.icons}`}  ></i>
                                 <span className={styles.text}>Analytics</span>
                            </NavLink>
                            <NavLink className={styles.navLink} to="/reports">
                                <i className ={`bx bx-download ${styles.icons}`} > </i>
                                <span className={styles.text}>Reports</span>
                            </NavLink>
                            <NavLink className={styles.navLink} to="/uploads">
                                <i className ={`bx bx-upload ${styles.icons}`}> </i>
                                <span className={styles.text}>Upload</span>
                            </NavLink>
                            <NavLink className={styles.navLink} to="/settings">
                                <i className ={`bx  bx-cog ${styles.icons}`}> </i>
                                <span className={styles.text}>Settings</span>
                            </NavLink>
                        </aside>
                    </div>
                </div>
                <div className={styles.bottomContent}>
                    <NavLink className={styles.navLink} to="">
                                <i className ={`bx bx-log-out ${styles.icons}`}> </i>
                                <span className={styles.text}>Logout</span>
                    </NavLink>
                    <NavLink className= {` ${styles.navLink} ${styles.mode} `}to="">
                        <div className={styles.moonSun}>
                            <i className ={`bx bx-moon ${styles.icons} ${styles.moon}`}> </i>
                            <i className ={`bx bx-sun ${styles.icons} ${styles.sun}`}> </i>
                        </div>
                        <span className={styles.text}>
                            {theme === "light" ? "Light Mode" : "Dark Mode"}
                        </span>
                        <div className={styles.toggleSwitch} onClick={(e) => { e.preventDefault(); toggleTheme(); }}>
                            <span className={styles.switch}></span>
                        </div>
                    </NavLink>
                </div>
            </nav>
        
        
        
        
        
        </>
    );



};
export default Nav;
