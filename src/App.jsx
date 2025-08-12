import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import BoycottedProducts from './pages/BoycottedProducts'
import Funding from './pages/Funding'
import PosterGenerator from './pages/PosterGenerator'
import QuranicVerse from './pages/QuranicVerse'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/boycotted-products" element={<BoycottedProducts />} />
            <Route path="/funding" element={<Funding />} />
            <Route path="/poster-generator" element={<PosterGenerator />} />
            <Route path="/quranic-verse" element={<QuranicVerse />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
