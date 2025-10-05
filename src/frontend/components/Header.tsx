import styles from "./Header.module.css";
import notifications from "../assets/notifications.png";
import {useState} from "react";
import { Search } from "@mynaui/icons-react";

type HeaderProps = { //blueprint that defines the prop
    onSearch?: (query: string) => void; //onSearch is a functional prop, if passed, it takes a string (query) and return nothing
}

const Header = ({onSearch}: HeaderProps) => { //recieves props of type HeaderProps and extracts onSearch
    const [query, setQuery] = useState(""); //Local state for the search input value with in header page does not update to main component
    const [expanded, setExpanded] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => { //runs everytime user types in input
        setQuery(e.target.value) //update local query state with the input value
        if (onSearch) onSearch(e.target.value); //if parent (home) passed onSearch call it with the current input
    };
    return(
        <header className ={styles.header}>
            <p>Hi, Abdullah</p>
           <div className={`${styles.iconGroup} ${expanded ? styles.expanded : ""}`}>
                <Search
                    className={styles.searchIcon}
                    size={30}
                    color="#BCFFDB"
                    strokeWidth={1}
                    onClick={() => setExpanded(v => !v)}
                />

                <input
                    className={styles.searchInput}
                    type="text"
                    value={query}
                    onChange={handleChange}
                    placeholder="Search..."
                />

                <button className={styles.iconButton}>
                <img className={styles.notifications} src={notifications} alt="Notifications" />
                </button>
            </div>
        </header>
    );
};
export default Header;