import { useState } from 'react'
import './Funding.css'

function Funding() {
  const [isFAQOpen, setIsFAQOpen] = useState(false)
  const [userQuestion, setUserQuestion] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [faqAnswer, setFaqAnswer] = useState('')
  const [error, setError] = useState('')

  const campaigns = [
    {
      id: 1,
      title: 'Hot Meals for Starved Palestinian Kids',
      description: 'Providing daily hot meals to children in north Gaza who are facing severe food insecurity',
      goal: 50000,
      raised: 35000,
      image: '🍲',
      category: 'food',
      link: 'https://www.gofundme.com/f/Hot-meals-in-gaza-daily?utm_source=chatgpt.com'
    },
    {
      id: 2,
      title: 'Safe Home & Education for Children',
      description: 'Helping families secure safe housing and education for their children during this crisis',
      goal: 25000,
      raised: 18000,
      image: '🏠',
      category: 'education',
      link: 'https://www.gofundme.com/f/help-us-secure-a-safe-home-and-education-for-our-children?utm_source=chatgpt.com'
    },
    {
      id: 3,
      title: 'Family Survival & Evacuation Fund',
      description: 'Supporting families trying to flee the conflict and survive in Gaza',
      goal: 15000,
      raised: 12000,
      image: '🚨',
      category: 'emergency',
      link: 'https://www.gofundme.com/f/help-fleeing-the-conflict-in-gaza?utm_source=chatgpt.com'
    },
    {
      id: 4,
      title: 'Heal Palestine Inc. Support',
      description: 'Supporting Heal Palestine Inc. in their humanitarian efforts for Gaza',
      goal: 30000,
      raised: 22000,
      image: '❤️',
      category: 'medical',
      link: 'https://www.gofundme.com/charity/heal-palestine-inc?utm_source=chatgpt.com'
    }
  ]

  const handleDirectDonation = (campaignLink) => {
    window.open(campaignLink, '_blank')
  }

  const handleFAQSubmit = async (e) => {
    e.preventDefault()
    if (!userQuestion.trim()) {
      setError('Please enter your question.')
      return
    }

    setIsLoading(true)
    setError('')
    setFaqAnswer('')

    try {
      const response = await fetch('/api/faq', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_question: userQuestion
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get answer. Please try again.')
      }

      const data = await response.json()
      setFaqAnswer(data.answer)
    } catch (err) {
      setError(err.message || 'An error occurred while processing your question.')
    } finally {
      setIsLoading(false)
    }
  }

  const resetFAQ = () => {
    setUserQuestion('')
    setFaqAnswer('')
    setError('')
  }

  const closeFAQ = () => {
    setIsFAQOpen(false)
    resetFAQ()
  }

  return (
    <div className="funding">
      {/* Sophia Avatar Button with Hover Message */}
      <div className="sophia-avatar-container">
        <div className="sophia-tooltip">
          <div className="sophia-tooltip-content">
            <div className="sophia-tooltip-avatar">
              <img src="/sophia-avatar.png" alt="Sophia" className="sophia-avatar-img" />
            </div>
            <div className="sophia-tooltip-text">
              <p className="sophia-greeting">Hi! I'm Sophia</p>
              <p className="sophia-description">Your AI assistant here to help with questions about Gaza relief and donations</p>
            </div>
          </div>
        </div>
        <button 
          className="sophia-avatar-button"
          onClick={() => setIsFAQOpen(true)}
          title="Ask Sophia about Gaza relief and donations"
        >
          <img src="/sophia-avatar.png" alt="Sophia" className="sophia-avatar-img" />
        </button>
      </div>

      {/* FAQ Modal */}
      {isFAQOpen && (
        <div className="faq-modal-overlay" onClick={closeFAQ}>
          <div className="faq-modal" onClick={(e) => e.stopPropagation()}>
            <div className="faq-modal-header">
              <div className="faq-modal-title">
                <div className="faq-modal-avatar">
                  <img src="/sophia-avatar.png" alt="Sophia" className="sophia-avatar-img" />
                </div>
                <div>
                  <h2>Sophia - Your AI Assistant</h2>
                  <p>Ask me anything about Gaza relief, donations, or humanitarian aid</p>
                </div>
              </div>
              <button className="faq-close-button" onClick={closeFAQ}>×</button>
            </div>

            <div className="faq-modal-content">
              <form onSubmit={handleFAQSubmit} className="faq-form">
                <div className="form-group">
                  <label htmlFor="question">Ask your question:</label>
                  <textarea
                    id="question"
                    value={userQuestion}
                    onChange={(e) => setUserQuestion(e.target.value)}
                    placeholder="Ask about Gaza relief, donations, humanitarian aid, or any other questions..."
                    rows="4"
                    className="question-input"
                    disabled={isLoading}
                  />
                </div>

                <div className="faq-actions">
                  <button 
                    type="submit" 
                    className="faq-submit-button"
                    disabled={isLoading}
                  >
                    {isLoading ? 'Getting Answer...' : 'Ask Sophia'}
                  </button>
                  <button 
                    type="button" 
                    className="faq-reset-button"
                    onClick={resetFAQ}
                    disabled={isLoading}
                  >
                    Reset
                  </button>
                </div>

                {error && (
                  <div className="faq-error">
                    {error}
                  </div>
                )}
              </form>

              {isLoading && (
                <div className="faq-loading">
                  <div className="loading-spinner"></div>
                  <p>Sophia is thinking...</p>
                </div>
              )}

              {faqAnswer && (
                <div className="faq-answer">
                  <div className="faq-answer-header">
                    <div className="faq-answer-avatar">
                      <img src="/sophia-avatar.png" alt="Sophia" className="sophia-avatar-img" />
                    </div>
                    <h3>Sophia's Answer:</h3>
                  </div>
                  <div className="answer-content">
                    {faqAnswer.split('\n').map((line, index) => (
                      <p key={index} className="answer-line">
                        {line}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="page-header">
        <h1>Support Gaza Emergency Relief</h1>
        <p>Your generous donations help provide immediate aid to families in Gaza facing humanitarian crisis.</p>
      </div>

      <div className="campaigns-section">
        <h2>Emergency Relief Campaigns</h2>
        <div className="campaigns-grid">
          {campaigns.map(campaign => (
            <div key={campaign.id} className="campaign-card">
              <div className="campaign-header">
                <div className="campaign-icon">{campaign.image}</div>
                <div className="campaign-info">
                  <h3>{campaign.title}</h3>
                  <p>{campaign.description}</p>
                </div>
              </div>

              <button 
                className="donate-button"
                onClick={() => handleDirectDonation(campaign.link)}
              >
                Donate Now
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Alkhidmat Foundation Section */}
      <div className="alkhidmat-section">
        <div className="alkhidmat-header">
          <h2>Partner Organization: Alkhidmat Foundation Pakistan</h2>
          <p>A respected Pakistani NGO actively providing humanitarian services, including aid for Gaza.</p>
        </div>

        <div className="alkhidmat-options">
          <div className="alkhidmat-card">
            <h3>🚨 Emergency Palestine Appeal</h3>
            <p>Direct support for Gaza emergency relief efforts</p>
            <a 
              href="https://alkhidmat.org/appeal/emergency-appeal-palestine-save-lives-in-gaza-today?utm_source=chatgpt.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="alkhidmat-button emergency"
            >
              Emergency Appeal
            </a>
          </div>

          <div className="alkhidmat-card">
            <h3>🏦 Bank Transfer</h3>
            <div className="bank-details">
              <p><strong>Bank:</strong> Meezan Bank</p>
              <p><strong>Account:</strong> Al Khidmat Foundation Pakistan</p>
              <p><strong>IBAN:</strong> PK35MEZN0002140100861151</p>
              <p><strong>SWIFT:</strong> MEZNPKKA</p>
            </div>
            <a 
              href="https://alkhidmat.org/donate?utm_source=chatgpt.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="alkhidmat-button secondary"
            >
              More Details
            </a>
          </div>
        </div>

        <div className="alkhidmat-note">
          <p><strong>Note:</strong> Alkhidmat Foundation Pakistan is a trusted partner organization. Your donations through them directly support humanitarian efforts including Gaza emergency relief.</p>
        </div>
      </div>
    </div>
  )
}

export default Funding 