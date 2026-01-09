import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import MainPage from "./MainPage.jsx";
import Table from "./Table.jsx";
import Header from "./components/Header.jsx";
import {useState} from "react";

function App() {
    const [session, setSession] = useState({
        image: null,
        points: [],
        result: null,
        done: false,
        loading: false,
    });

    return (
        <BrowserRouter>
            <Header />
            <div className="page-content">
            <Routes>
                <Route path="/" element={<MainPage session={session} setSession={setSession}/>}/>
                <Route path="/table" element={<Table />}/>
            </Routes>
            </div>
        </BrowserRouter>

    )
}

export default App;