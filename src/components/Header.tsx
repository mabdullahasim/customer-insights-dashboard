import styles from "./Header.module.css";
import {useState} from "react";

type HeaderProps = { //blueprint that defines the prop
    onSearch?: (query: string) => void; //onSearch is a functional prop that if passed should take a string (query) and return nothing
}

const Header = ({onSearch}: HeaderProps) => {   //recives the direct value of onSearch of type HeaderProps
    const [query, setQuery] = useState("");

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => { //function will run every time user tpyes into search bar
        setQuery(e.target.value) //set query to value from event object passed from input
        if (onSearch) onSearch(e.target.value); //if onSearch isnt undefined call onSearch
    };

    return(
        <header className ={styles.header}>
            <h1>Customer Insights</h1>
            <div className={styles.searchBar}>
                <input
                    type ="text"
                    value ={query}
                    onChange={handleChange}
                    placeholder="Search..."
                />
            </div>





        </header>
    );
};
export default Header;