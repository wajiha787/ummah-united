import { useState, useEffect } from 'react'
import './QuranicVerse.css'

function QuranicVerse() {
  const [currentVerse, setCurrentVerse] = useState(0)
  const [showTranslation, setShowTranslation] = useState(true)
  const [showTafsir, setShowTafsir] = useState(false)

  // Quran Chatbot states
  const [isChatbotOpen, setIsChatbotOpen] = useState(false)
  const [chatbotQuestion, setChatbotQuestion] = useState('')
  const [isChatbotLoading, setIsChatbotLoading] = useState(false)
  const [chatbotAnswer, setChatbotAnswer] = useState('')
  const [chatbotError, setChatbotError] = useState('')

  // Daily Hadith states
  const [showHadithPopup, setShowHadithPopup] = useState(false)
  const [currentHadithIndex, setCurrentHadithIndex] = useState(0)

  const hadiths = [
    {
      id: 1,
      title: "The Ummah as One Body",
      text: "The believers, in their mutual kindness, compassion, and sympathy, are just like one body. When one of the limbs suffers, the whole body responds to it with wakefulness and fever.",
      source: "Sahih al-Bukhari, Sahih Muslim"
    },
    {
      id: 2,
      title: "Helping the Oppressed",
      text: "Help your brother, whether he is an oppressor or is oppressed. They said, 'O Messenger of Allah, we help the oppressed, but how do we help the oppressor?' He said, 'By preventing him from oppressing others.'",
      source: "Sahih al-Bukhari"
    },
    {
      id: 3,
      title: "Relieving Distress",
      text: "Whoever relieves a believer's distress of the distressful aspects of this world, Allah will rescue him from a difficulty of the difficulties of the Hereafter.",
      source: "Sahih Muslim"
    },
    {
      id: 4,
      title: "Standing Against Injustice",
      text: "The best jihad is a word of truth before a tyrant ruler.",
      source: "Sunan an-Nasa'i, Sunan Abu Dawood"
    },
    {
      id: 5,
      title: "Loving for Others",
      text: "None of you truly believes until he loves for his brother what he loves for himself.",
      source: "Sahih al-Bukhari, Sahih Muslim"
    },
    {
      id: 6,
      title: "Reward for Charity",
      text: "The believer's shade on the Day of Resurrection will be his charity.",
      source: "Sahih al-Bukhari"
    },
    {
      id: 7,
      title: "Mutual Mercy",
      text: "The merciful are shown mercy by the Most Merciful. Be merciful to those on the earth and the One above the heavens will have mercy upon you.",
      source: "Sunan al-Tirmidhi"
    }
  ]

  const verses = [
    {
      id: 1,
      surah: 'Surah Ibrahim',
      ayah: 14,
      arabic: 'وَلَنُسْكِنَنَّكُمُ ٱلْأَرْضَ مِنۢ بَعْدِهِمْ ۚ ذَٰلِكَ لِمَنْ خَافَ مَقَامِى وَخَافَ وَعِيدِ',
      translation: 'And make you reside in the land after them. This is for whoever is in awe of standing before Me and fears My warning.',
      tafsir: 'This verse promises that the righteous will inherit and reside in the land after the oppressors are removed. It emphasizes that this promise is specifically for those who fear Allah and are conscious of standing before Him on the Day of Judgment. This provides hope for justice and divine intervention.',
      theme: 'Promise of Land Inheritance'
    },
    {
      id: 2,
      surah: 'Surah An-Nisa',
      ayah: 4,
      arabic: 'وَمَا لَكُمْ لَا تُقَـٰتِلُونَ فِى سَبِيلِ ٱللَّهِ وَٱلْمُسْتَضْعَفِينَ مِنَ ٱلرِّجَالِ وَٱلنِّسَآءِ وَٱلْوِلْدَٰنِ',
      translation: 'And what is [the matter] with you that you fight not in the cause of Allah and for the oppressed among men, women, and children?',
      tafsir: 'This verse emphasizes the duty to fight for justice and protect the oppressed, including vulnerable groups like women and children. It calls upon believers to stand up against oppression and defend the rights of the weak.',
      theme: 'Helping the Oppressed'
    },
    {
      id: 3,
      surah: 'Surah Al-Hajj',
      ayah: 22,
      arabic: 'إِنَّ ٱللَّهَ يُدَافِعُ عَنِ ٱلَّذِينَ ءَامَنُوٓا۟',
      translation: 'Indeed, Allah defends those who have believed.',
      tafsir: 'This verse assures believers that Allah Himself will defend and protect those who have faith. It provides comfort to the oppressed that they are not alone in their struggle.',
      theme: 'Allah is with the Oppressed'
    },
    {
      id: 4,
      surah: 'Surah Aal-e-Imran',
      ayah: 3,
      arabic: 'إِن يَنصُرْكُمُ ٱللَّهُ فَلَا غَالِبَ لَكُمْ',
      translation: 'If Allah helps you, none can overcome you.',
      tafsir: 'This verse provides ultimate hope and assurance that with Allah\'s help, no force can overcome the believers. It reinforces the power of divine assistance in the struggle for justice.',
      theme: 'Promise of Allah\'s Help'
    }
  ]

  // Get current day of the week (0-6) to determine which Hadith to show
  useEffect(() => {
    const today = new Date().getDay() // 0 = Sunday, 1 = Monday, etc.
    setCurrentHadithIndex(today)
    setShowHadithPopup(true)
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentVerse((prev) => (prev + 1) % verses.length)
    }, 10000) // Change verse every 10 seconds

    return () => clearInterval(interval)
  }, [verses.length])

  const nextVerse = () => {
    setCurrentVerse((prev) => (prev + 1) % verses.length)
  }

  const prevVerse = () => {
    setCurrentVerse((prev) => (prev - 1 + verses.length) % verses.length)
  }

  const handleChatbotSubmit = async (e) => {
    e.preventDefault()
    if (!chatbotQuestion.trim()) {
      setChatbotError('Please enter your question.')
      return
    }

    setIsChatbotLoading(true)
    setChatbotError('')
    setChatbotAnswer('')

    try {
      const response = await fetch('http://localhost:8000/api/quran', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_question: chatbotQuestion
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get answer. Please try again.')
      }

      const data = await response.json()
      setChatbotAnswer(data.answer)
    } catch (err) {
      setChatbotError(err.message || 'An error occurred while processing your question.')
    } finally {
      setIsChatbotLoading(false)
    }
  }

  const resetChatbot = () => {
    setChatbotQuestion('')
    setChatbotAnswer('')
    setChatbotError('')
  }

  const closeHadithPopup = () => {
    setShowHadithPopup(false)
  }

  const currentVerseData = verses[currentVerse]
  const currentHadith = hadiths[currentHadithIndex]

  return (
    <div className="quranic-verse">
      {/* Daily Hadith Popup */}
      {showHadithPopup && (
        <div className="hadith-popup-overlay" onClick={closeHadithPopup}>
          <div className="hadith-popup" onClick={(e) => e.stopPropagation()}>
            <div className="hadith-popup-header">
              <div className="hadith-popup-title">
                <span className="hadith-popup-icon">📖</span>
                <div>
                  <h2>Daily Hadith</h2>
                </div>
              </div>
              <button className="hadith-popup-close-button" onClick={closeHadithPopup}>×</button>
            </div>

            <div className="hadith-popup-content">
              <div className="hadith-content">
                <h3 className="hadith-title">{currentHadith.title}</h3>
                <div className="hadith-text">
                  <p>"{currentHadith.text}"</p>
                </div>
                <div className="hadith-source">
                  <span>Source: {currentHadith.source}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="page-header">
        <h1>Quranic Verses About Palestine</h1>
        <p>Reflect on the sacred status of the Holy Land and its divine significance</p>
      </div>

      {/* Quran/Hadith Chatbot Section */}
      <div className="quran-chatbot-section">
        <div className="quran-chatbot-section-header">
          <div className="quran-chatbot-section-icon">📖</div>
          <div className="quran-chatbot-section-content">
            <h2>Ask About Palestine in Quran & Hadith</h2>
            <p>Get answers about Islamic stories, verses, and history related to Palestine and the Holy Land</p>
          </div>
          <button 
            className="quran-chatbot-section-button"
            onClick={() => setIsChatbotOpen(true)}
          >
            Ask Question
          </button>
        </div>
      </div>

      <div className="verse-container">
        <div className="verse-navigation">
          <button onClick={prevVerse} className="nav-button">
            ← Previous
          </button>
          <span className="verse-counter">
            {currentVerse + 1} of {verses.length}
          </span>
          <button onClick={nextVerse} className="nav-button">
            Next →
          </button>
        </div>

        <div className="verse-card">
          <div className="verse-header">
            <h2 className="surah-name">{currentVerseData.surah}</h2>
            <span className="ayah-number">Ayah {currentVerseData.ayah}</span>
          </div>

          <div className="verse-content">
            <div className="arabic-text">
              {currentVerseData.arabic}
            </div>

            {showTranslation && (
              <div className="translation">
                <h3>Translation</h3>
                <p className="english-translation">{currentVerseData.translation}</p>
              </div>
            )}

            {showTafsir && (
              <div className="tafsir">
                <h3>Tafsir (Interpretation)</h3>
                <p>{currentVerseData.tafsir}</p>
              </div>
            )}

            <div className="verse-theme">
              <span className="theme-badge">{currentVerseData.theme}</span>
            </div>
          </div>

          <div className="verse-controls">
            <button
              onClick={() => setShowTranslation(!showTranslation)}
              className={`control-button ${showTranslation ? 'active' : ''}`}
            >
              {showTranslation ? 'Hide' : 'Show'} Translation
            </button>
            <button
              onClick={() => setShowTafsir(!showTafsir)}
              className={`control-button ${showTafsir ? 'active' : ''}`}
            >
              {showTafsir ? 'Hide' : 'Show'} Tafsir
            </button>
          </div>
        </div>

        <div className="verse-indicators">
          {verses.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentVerse(index)}
              className={`indicator ${index === currentVerse ? 'active' : ''}`}
            />
          ))}
        </div>
      </div>

      {/* Quran Chatbot Modal */}
      {isChatbotOpen && (
        <div className="quran-chatbot-modal-overlay" onClick={() => setIsChatbotOpen(false)}>
          <div className="quran-chatbot-modal" onClick={(e) => e.stopPropagation()}>
            <div className="quran-chatbot-modal-header">
              <div className="quran-chatbot-modal-title">
                <span className="quran-chatbot-modal-avatar">📖</span>
                <div>
                  <h2>Islamic Knowledge Assistant</h2>
                  <p>Ask about Palestine in Quran, Hadith, and Islamic history</p>
                </div>
              </div>
              <button className="quran-chatbot-close-button" onClick={() => setIsChatbotOpen(false)}>×</button>
            </div>

            <div className="quran-chatbot-modal-content">
              <form onSubmit={handleChatbotSubmit} className="quran-chatbot-form">
                <div className="form-group">
                  <label htmlFor="quran-question">Ask your question:</label>
                  <textarea
                    id="quran-question"
                    value={chatbotQuestion}
                    onChange={(e) => setChatbotQuestion(e.target.value)}
                    placeholder="Ask about Quranic verses, Hadith, or Islamic stories related to Palestine..."
                    rows="4"
                    className="quran-question-input"
                    disabled={isChatbotLoading}
                  />
                </div>

                <div className="quran-chatbot-actions">
                  <button 
                    type="submit" 
                    className="quran-chatbot-submit-button"
                    disabled={isChatbotLoading}
                  >
                    {isChatbotLoading ? 'Getting Answer...' : 'Ask Question'}
                  </button>
                  <button 
                    type="button" 
                    className="quran-chatbot-reset-button"
                    onClick={resetChatbot}
                    disabled={isChatbotLoading}
                  >
                    Reset
                  </button>
                </div>

                {chatbotError && (
                  <div className="quran-chatbot-error">
                    {chatbotError}
                  </div>
                )}
              </form>

              {isChatbotLoading && (
                <div className="quran-chatbot-loading">
                  <div className="loading-spinner"></div>
                  <p>Searching Islamic sources...</p>
                </div>
              )}

              {chatbotAnswer && (
                <div className="quran-chatbot-answer">
                  <div className="quran-chatbot-answer-header">
                    <span className="quran-chatbot-answer-avatar">📖</span>
                    <h3>Islamic Answer:</h3>
                  </div>
                  <div className="quran-answer-content">
                    {chatbotAnswer.split('\n').map((line, index) => (
                      <p key={index} className="quran-answer-line">
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

      <div className="prayer-section">
        <h2>Prayer for Palestine</h2>
        <div className="prayer-text">
          <p>
            "O Allah, protect the blessed land of Palestine and its people. Grant peace and justice to the Holy Land. 
            Help us to understand the sacred nature of this land and guide us to support those who are oppressed. 
            Grant victory to the truth and protect the innocent. Ameen."
          </p>
        </div>
      </div>
    </div>
  )
}

export default QuranicVerse 