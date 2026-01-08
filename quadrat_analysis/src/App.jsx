import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import MainPage from "./MainPage.jsx";
import Table from "./Table.jsx";
import Header from "./components/Header.jsx";

function App() {
    return (
        <BrowserRouter>
            <Header />
            <div className="page-content">
            <Routes>
                <Route path="/" element={<MainPage/>}/>
                <Route path="/table" element={<Table />}/>
            </Routes>
            </div>
        </BrowserRouter>

    )
}

export default App;