import { useEffect, useState } from "react";

const THEME_KEY = "theme";
const getInitial = () =>
  (localStorage.getItem(THEME_KEY) as "light"|"dark") || "light";

export function useTheme(){
  const [theme, setTheme] = useState<"light"|"dark">(getInitial);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === "light" ? "dark" : "light");

  return { theme, toggleTheme };
}