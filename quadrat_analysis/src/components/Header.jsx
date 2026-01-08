import React from 'react';
import {Link} from 'react-router-dom';
import '../styles/Header.css'

const Header = () => {
    return (
        <header className="header">
            <div className="header-content">
                <div className="nav-actions">
                    <Link to="/table" className="btn">Table</Link>
                    <Link to="/" className="btn">Analyze Quadrat</Link>
                </div>
            </div>
        </header>
    );
};

export default Header;