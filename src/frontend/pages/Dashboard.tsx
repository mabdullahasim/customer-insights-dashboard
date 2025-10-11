import { useState } from "react";
import { Link } from "react-router-dom"; // for navigation
import styles from "./Dashboard.module.css";
import Header from "../components/Header";
import Nav from "../components/nav";

const Dashboard = () => {
    return (
        <>
            <div className={styles.container}>
                <Header/>
                <Nav/>
                
            
            
            </div>
        
        
        </>


    )




}
export default Dashboard;