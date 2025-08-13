import { Link, useLocation } from 'react-router-dom'
import './Navbar.css'

function Navbar() {
  const location = useLocation()

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <div className="logo-container">
            <img src="/ummah-united-logo-simple.svg" alt="Ummah United Logo" className="navbar-logo" />
            <h1>Ummah United</h1>
          </div>
        </Link>
        <ul className="navbar-nav">
          <li className="nav-item">
            <Link 
              to="/" 
              className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
            >
              Home
            </Link>
          </li>
          <li className="nav-item">
            <Link 
              to="/boycotted-products" 
              className={`nav-link ${location.pathname === '/boycotted-products' ? 'active' : ''}`}
            >
              Boycotted Products
            </Link>
          </li>
          <li className="nav-item">
            <Link 
              to="/funding" 
              className={`nav-link ${location.pathname === '/funding' ? 'active' : ''}`}
            >
              Funding
            </Link>
          </li>
          <li className="nav-item">
            <Link 
              to="/poster-generator" 
              className={`nav-link ${location.pathname === '/poster-generator' ? 'active' : ''}`}
            >
              Poster Generator
            </Link>
          </li>
          <li className="nav-item">
            <Link 
              to="/quranic-verse" 
              className={`nav-link ${location.pathname === '/quranic-verse' ? 'active' : ''}`}
            >
              Quranic Verse
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  )
}

export default Navbar 