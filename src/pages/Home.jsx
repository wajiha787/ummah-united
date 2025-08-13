import './Home.css'

function Home() {
  return (
    <div className="home">
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Ummah United</h1>
          <p className="hero-subtitle">Standing Together in Solidarity</p>
          <div className="hero-description">
            <p>Welcome to Ummah United, a platform dedicated to fostering unity, 
            awareness, and support within our global Muslim community. Together, 
            we stand for justice, peace, and the well-being of all people.</p>
          </div>
        </div>
        <div className="hero-visual">
          <div className="palestine-flag">
            <div className="flag-stripe black"></div>
            <div className="flag-stripe white"></div>
            <div className="flag-stripe green"></div>
            <div className="flag-triangle"></div>
          </div>
        </div>
      </div>

      <div className="features-section">
        <h2>Our Mission</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🕌</div>
            <h3>Unity</h3>
            <p>Bringing together Muslims from around the world in solidarity and brotherhood.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🕊️</div>
            <h3>Peace</h3>
            <p>Promoting peace, justice, and human rights for all people.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🤝</div>
            <h3>Support</h3>
            <p>Providing support and resources to those in need within our community.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📚</div>
            <h3>Education</h3>
            <p>Sharing knowledge and raising awareness about important issues.</p>
          </div>
        </div>
      </div>

      <div className="call-to-action">
        <h2>Join Our Community</h2>
        <p>Together we can make a difference. Explore our resources and get involved.</p>
        <div className="cta-buttons">
          <button className="cta-button primary">Learn More</button>
          <button className="cta-button secondary">Get Involved</button>
        </div>
      </div>
    </div>
  )
}

export default Home 