import { useState } from 'react'
import './Funding.css'

function Funding() {
  const [selectedCampaign, setSelectedCampaign] = useState('')
  const [donationAmount, setDonationAmount] = useState('')

  const campaigns = [
    {
      id: 1,
      title: 'Emergency Relief Fund',
      description: 'Providing immediate humanitarian aid to affected families',
      goal: 50000,
      raised: 35000,
      image: '🆘',
      category: 'emergency'
    },
    {
      id: 2,
      title: 'Medical Supplies',
      description: 'Sending essential medical equipment and supplies',
      goal: 25000,
      raised: 18000,
      image: '🏥',
      category: 'medical'
    },
    {
      id: 3,
      title: 'Education Support',
      description: 'Supporting children\'s education and school supplies',
      goal: 15000,
      raised: 12000,
      image: '📚',
      category: 'education'
    },
    {
      id: 4,
      title: 'Food Security',
      description: 'Providing food packages and clean water',
      goal: 30000,
      raised: 22000,
      image: '🍞',
      category: 'food'
    }
  ]

  const quickAmounts = [10, 25, 50, 100, 250, 500]

  const calculateProgress = (raised, goal) => {
    return Math.min((raised / goal) * 100, 100)
  }

  const handleDonation = (e) => {
    e.preventDefault()
    if (selectedCampaign && donationAmount) {
      alert(`Thank you for your donation of $${donationAmount} to ${selectedCampaign}. This is a demo - in a real application, this would redirect to a secure payment processor.`)
      setDonationAmount('')
      setSelectedCampaign('')
    } else {
      alert('Please select a campaign and enter a donation amount.')
    }
  }

  return (
    <div className="funding">
      <div className="page-header">
        <h1>Support Our Cause</h1>
        <p>Your generous donations help us provide essential aid and support to those in need.</p>
      </div>

      <div className="campaigns-section">
        <h2>Active Campaigns</h2>
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
              
              <div className="campaign-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${calculateProgress(campaign.raised, campaign.goal)}%` }}
                  ></div>
                </div>
                <div className="progress-stats">
                  <span className="raised">${campaign.raised.toLocaleString()}</span>
                  <span className="goal">of ${campaign.goal.toLocaleString()}</span>
                  <span className="percentage">{Math.round(calculateProgress(campaign.raised, campaign.goal))}%</span>
                </div>
              </div>

              <button 
                className="donate-button"
                onClick={() => setSelectedCampaign(campaign.title)}
              >
                Donate Now
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="donation-section">
        <div className="donation-form-container">
          <h2>Make a Donation</h2>
          <form onSubmit={handleDonation} className="donation-form">
            <div className="form-group">
              <label htmlFor="campaign-select">Select Campaign:</label>
              <select
                id="campaign-select"
                value={selectedCampaign}
                onChange={(e) => setSelectedCampaign(e.target.value)}
                required
              >
                <option value="">Choose a campaign...</option>
                {campaigns.map(campaign => (
                  <option key={campaign.id} value={campaign.title}>
                    {campaign.title}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Donation Amount:</label>
              <div className="amount-buttons">
                {quickAmounts.map(amount => (
                  <button
                    key={amount}
                    type="button"
                    className={`amount-button ${donationAmount === amount.toString() ? 'selected' : ''}`}
                    onClick={() => setDonationAmount(amount.toString())}
                  >
                    ${amount}
                  </button>
                ))}
              </div>
              <input
                type="number"
                placeholder="Or enter custom amount"
                value={donationAmount}
                onChange={(e) => setDonationAmount(e.target.value)}
                min="1"
                step="1"
                className="custom-amount"
              />
            </div>

            <button type="submit" className="submit-donation">
              Donate Securely
            </button>
          </form>
        </div>

        <div className="donation-info">
          <h3>Why Donate?</h3>
          <ul>
            <li>100% of your donation goes directly to those in need</li>
            <li>Transparent reporting on how funds are used</li>
            <li>Emergency response within 24-48 hours</li>
            <li>Regular updates on project progress</li>
          </ul>
          
          <h3>Other Ways to Help</h3>
          <div className="help-options">
            <div className="help-option">
              <h4>Volunteer</h4>
              <p>Join our volunteer network and help on the ground</p>
            </div>
            <div className="help-option">
              <h4>Fundraise</h4>
              <p>Start your own fundraising campaign</p>
            </div>
            <div className="help-option">
              <h4>Spread Awareness</h4>
              <p>Share our campaigns on social media</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Funding 