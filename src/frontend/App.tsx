import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import SignUp from "./pages/SignUp";
import Dashboard from "./pages/Dashboard";
import RequireAuth from "./api/Auth/RequireAuth";
function App() {
  return (
    <Router>
      <Routes>
        {/* <Route element = {<RequireAuth/>}> for protected routes requiring auth */}
          <Route path= "/dashboard" element = {<Dashboard/>} />
        {/* </Route> */}

        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/" element={<Login />} />
      </Routes>
    </Router>
  );
}

export default App;