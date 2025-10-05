import styles from "./Nav.module.css";
import "boxicons/css/boxicons.min.css";




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
            </nav>
        
        
        
        
        
        </>
    );



};
export default Nav;