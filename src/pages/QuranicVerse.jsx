import { useState, useEffect } from 'react'
import './QuranicVerse.css'

function QuranicVerse() {
  const [currentVerse, setCurrentVerse] = useState(0)
  const [showTranslation, setShowTranslation] = useState(true)
  const [showTafsir, setShowTafsir] = useState(false)

  const verses = [
    {
      id: 1,
      surah: 'Al-Baqarah',
      ayah: 256,
      arabic: 'لَا إِكْرَاهَ فِي الدِّينِ ۖ قَد تَّبَيَّنَ الرُّشْدُ مِنَ الْغَيِّ ۚ فَمَن يَكْفُرْ بِالطَّاغُوتِ وَيُؤْمِن بِاللَّهِ فَقَدِ اسْتَمْسَكَ بِالْعُرْوَةِ الْوُثْقَىٰ لَا انفِصَامَ لَهَا ۗ وَاللَّهُ سَمِيعٌ عَلِيمٌ',
      translation: 'There is no compulsion in religion. The right direction is henceforth distinct from error. And he who rejecteth false deities and believeth in Allah hath grasped a firm handhold which will never break. Allah is Hearer, Knower.',
      tafsir: 'This verse emphasizes the principle of religious freedom in Islam. It states that no one should be forced to accept any religion, as the truth has been made clear from falsehood. The verse teaches that faith must come from conviction, not coercion.',
      theme: 'Religious Freedom'
    },
    {
      id: 2,
      surah: 'Al-Hujurat',
      ayah: 13,
      arabic: 'يَا أَيُّهَا النَّاسُ إِنَّا خَلَقْنَاكُم مِّن ذَكَرٍ وَأُنثَىٰ وَجَعَلْنَاكُمْ شُعُوبًا وَقَبَائِلَ لِتَعَارَفُوا ۚ إِنَّ أَكْرَمَكُمْ عِندَ اللَّهِ أَتْقَاكُمْ ۚ إِنَّ اللَّهَ عَلِيمٌ خَبِيرٌ',
      translation: 'O mankind! We have created you from a male and a female, and made you into nations and tribes, that you may know one another. Verily, the most honorable of you with Allah is that (believer) who has At-Taqwa (piety and righteousness). Verily, Allah is All-Knowing, All-Aware.',
      tafsir: 'This verse teaches that all human beings are equal in the sight of Allah, regardless of their race, ethnicity, or social status. The only criterion for superiority is piety and righteousness. It promotes unity and understanding among different nations and tribes.',
      theme: 'Human Equality'
    },
    {
      id: 3,
      surah: 'Al-Ma\'idah',
      ayah: 32,
      arabic: 'مِنْ أَجْلِ ذَٰلِكَ كَتَبْنَا عَلَىٰ بَنِي إِسْرَائِيلَ أَنَّهُ مَن قَتَلَ نَفْسًا بِغَيْرِ نَفْسٍ أَوْ فَسَادٍ فِي الْأَرْضِ فَكَأَنَّمَا قَتَلَ النَّاسَ جَمِيعًا وَمَنْ أَحْيَاهَا فَكَأَنَّمَا أَحْيَا النَّاسَ جَمِيعًا',
      translation: 'Because of that, We decreed upon the Children of Israel that whoever kills a soul unless for a soul or for corruption [done] in the land - it is as if he had slain mankind entirely. And whoever saves one - it is as if he had saved mankind entirely.',
      tafsir: 'This verse establishes the sanctity of human life and the principle that killing one innocent person is equivalent to killing all of humanity. It also teaches that saving one life is equivalent to saving all of humanity, emphasizing the value of every human life.',
      theme: 'Sanctity of Life'
    },
    {
      id: 4,
      surah: 'Al-Imran',
      ayah: 103,
      arabic: 'وَاعْتَصِمُوا بِحَبْلِ اللَّهِ جَمِيعًا وَلَا تَفَرَّقُوا ۚ وَاذْكُرُوا نِعْمَتَ اللَّهِ عَلَيْكُمْ إِذْ كُنتُمْ أَعْدَاءً فَأَلَّفَ بَيْنَ قُلُوبِكُمْ فَأَصْبَحْتُم بِنِعْمَتِهِ إِخْوَانًا',
      translation: 'And hold firmly to the rope of Allah all together and do not become divided. And remember the favor of Allah upon you - when you were enemies and He brought your hearts together and you became, by His favor, brothers.',
      tafsir: 'This verse calls for unity among Muslims and warns against division. It reminds believers to hold fast to Allah\'s guidance collectively and not to split into factions. It also reminds them of Allah\'s blessing in uniting their hearts after they were enemies.',
      theme: 'Unity'
    },
    {
      id: 5,
      surah: 'Al-Furqan',
      ayah: 63,
      arabic: 'وَعِبَادُ الرَّحْمَٰنِ الَّذِينَ يَمْشُونَ عَلَى الْأَرْضِ هَوْنًا وَإِذَا خَاطَبَهُمُ الْجَاهِلُونَ قَالُوا سَلَامًا',
      translation: 'And the servants of the Most Merciful are those who walk upon the earth easily, and when the ignorant address them [harshly], they say [words of] peace.',
      tafsir: 'This verse describes the characteristics of the true servants of Allah. They walk humbly on earth and respond to ignorance with peace and wisdom, showing patience and forgiveness even when faced with harsh words.',
      theme: 'Humility and Peace'
    }
  ]

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

  const currentVerseData = verses[currentVerse]

  return (
    <div className="quranic-verse">
      <div className="page-header">
        <h1>Daily Quranic Verses</h1>
        <p>Reflect on the wisdom and guidance from the Holy Quran</p>
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
                <p>{currentVerseData.translation}</p>
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

      <div className="reflection-section">
        <h2>Daily Reflection</h2>
        <div className="reflection-content">
          <p>
            Take a moment to reflect on the meaning of this verse and how it applies to your daily life. 
            Consider how you can implement its teachings in your interactions with others and in your 
            personal growth.
          </p>
          
          <div className="reflection-prompts">
            <h3>Reflection Questions:</h3>
            <ul>
              <li>How does this verse relate to current events?</li>
              <li>What actions can I take to embody these teachings?</li>
              <li>How can I share this wisdom with others?</li>
              <li>What does this verse teach me about my relationship with Allah?</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="prayer-section">
        <h2>Prayer for Today</h2>
        <div className="prayer-text">
          <p>
            "O Allah, help us to understand and implement the teachings of Your Book in our daily lives. 
            Grant us the wisdom to apply these verses in our interactions with others. Strengthen our 
            faith and guide us on the straight path. Ameen."
          </p>
        </div>
      </div>
    </div>
  )
}

export default QuranicVerse 