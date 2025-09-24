import styles from "./Header.module.css";
import {useState} from "react";

type HeaderProps = { //blueprint that defines the prop
    onSearch?: (query: string) => void; //onSearch is a functional prop, if passed, it takes a string (query) and return nothing
}

const Header = ({onSearch}: HeaderProps) => { //recieves props of type HeaderProps and extracts onSearch
    const [query, setQuery] = useState(""); //Local state for the search input value with in header page does not update to main component

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => { //runs everytime user types in input
        setQuery(e.target.value) //update local query state with the input value
        if (onSearch) onSearch(e.target.value); //if parent (home) passed onSearch call it with the current input
    };

    return(
        <header className ={styles.header}>
            <p>Hi, Abdullah</p>
            <div className={styles.searchBarWrapper}>
                <input className= {styles.searchBar}
                    type ="text"
                    value ={query}
                    onChange={handleChange} //calls handleChang with every keystroke
                    placeholder="Search..."
                />
            </div>
            <button className={styles.iconButton} >
                <img  alt="User menu" />
            </button>
            




        </header>
    );
};
export default Header;