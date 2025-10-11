import styles from "./Nav.module.css";
import React from "react";
import "boxicons/css/boxicons.min.css";
import { NavLink } from "react-router-dom";


const Nav = () => {

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
                    <div className="menu">
                         <aside className={styles.links}>
                            <NavLink to="/dashboard">
                                <i className ={`bx  bx-home ${styles.home}`}  ></i>
                                <span>Dashboard</span>
                            </NavLink>
                            <NavLink to="/analytics">
                                 <i className ={`bx bx-bar-chart-alt-2    ${styles.analytics}`}  ></i>
      
                                 <span>Analytics</span>
                            </NavLink>
                            <NavLink to="/reports">
                                <i className ={`bx  bxs-folder-down-arrow ${styles.reports}`} > </i>
                                <span>Reports</span>
                            </NavLink>
                            <NavLink to="/uploads">
                                <i className ={`bx  bxs-file-plus ${styles.upload}`}> </i>
                                <span>Upload</span>
                            </NavLink>
                            <NavLink to="/settings">
                                <i className ={`bx  bx-cog ${styles.settings}`}> </i>
                                <span>Settings</span>
                            </NavLink>
                        </aside>
                    </div>
                </div>
            </nav>
        
        
        
        
        
        </>
    );



};
export default Nav;
