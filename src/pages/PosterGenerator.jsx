import { useState, useRef } from 'react'
import './PosterGenerator.css'

function PosterGenerator() {
  const [posterData, setPosterData] = useState({
    title: 'Justice for Palestine',
    subtitle: 'Stand Together for Human Rights',
    description: 'Join us in solidarity for justice and peace.',
    selectedImage: 'hunger'
  })

  const [aiDesign, setAiDesign] = useState(null)
  const [isGeneratingAi, setIsGeneratingAi] = useState(false)
  const [aiError, setAiError] = useState('')

  const posterImages = [
    { id: 'hunger', path: '/Hunger.png' },
    { id: 'solidarity', path: '/Solidarity.png' },
    { id: 'voice', path: '/Voice.png' }

  ]

  const handleInputChange = (field, value) => {
    setPosterData(prev => ({
      ...prev,
      [field]: value
    }))
  }


  const generatePoster = async () => {
    setIsGeneratingAi(true)
    setAiError('')
    setAiDesign(null)

    // Rotate through images: hunger -> solidarity -> voice -> hunger...
    const imageIds = ['hunger', 'solidarity', 'voice']
    const currentIndex = imageIds.indexOf(posterData.selectedImage)
    const nextIndex = (currentIndex + 1) % imageIds.length
    const nextImage = imageIds[nextIndex]

    
    // Update the selected image for next generation
    setPosterData(prev => ({
      ...prev,
      selectedImage: nextImage
    }))

    try {
      const response = await fetch('http://localhost:8000/api/generate-poster', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          theme: 'protest',
          title: posterData.title,
          subtitle: posterData.subtitle,
          description: posterData.description,
          imageType: nextImage
        })
      })

      if (!response.ok) {
        throw new Error('Failed to generate poster')
      }

      const data = await response.json()
      setAiDesign(data)
      
    } catch (err) {
      setAiError(err.message || 'An error occurred while generating poster')
    } finally {
      setIsGeneratingAi(false)
    }
  }

  const generateAiPoster = async () => {
    setIsGeneratingAi(true)
    setAiError('')
    setAiDesign(null)

    try {
      const response = await fetch('http://localhost:8000/api/generate-poster', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          theme: 'protest',
          title: posterData.title,
          subtitle: posterData.subtitle,
          description: posterData.description,
          style: 'modern'
        })
      })

      if (!response.ok) {
        throw new Error('Failed to generate AI poster design')
      }

      const data = await response.json()
      setAiDesign(data)
    } catch (err) {
      setAiError(err.message || 'An error occurred while generating AI design')
    } finally {
      setIsGeneratingAi(false)
    }
  }

  const resetPoster = () => {
    setPosterData({
      title: 'Justice for Palestine',
      subtitle: 'Stand Together for Human Rights',
      description: 'Join us in solidarity for justice and peace.',
      selectedImage: 'hunger'
    })

    setAiDesign(null)
    setAiError('')

  }
  const generateAIPoster = async () => {
    setIsGenerating(true)
    try {
      // Create a dynamic prompt based on user input
      let prompt = "Create a clean, bold solidarity poster. Use the Palestinian flag colors (red, green, black, white) prominently. Include one strong symbol such as a raised fist or hands joined in solidarity. "
      
      if (posterData.title) {
        prompt += `Add large, clear, bold text saying "${posterData.title}" in capital letters. `
      }
      
      if (posterData.subtitle) {
        prompt += `Include subtitle text: "${posterData.subtitle}". `
      }
      
      if (posterData.date || posterData.time) {
        let dateTimeText = ''
        if (posterData.date) dateTimeText += posterData.date
        if (posterData.date && posterData.time) dateTimeText += ' at '
        if (posterData.time) dateTimeText += posterData.time
        prompt += `Include date/time: "${dateTimeText}". `
      }
      
      if (posterData.location) {
        prompt += `Include location: "${posterData.location}". `
      }
      
      if (posterData.description) {
        prompt += `Include description: "${posterData.description}". `
      }
      
      if (posterData.customText) {
        prompt += `Include custom text: "${posterData.customText}". `
      }
      
      prompt += "Make it a professional, impactful poster design suitable for social media sharing."

      const response = await fetch(
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
        {
          method: "POST",
          headers: {
            Authorization: import.meta.env.VITE_HUGGING_FACE_API,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            inputs: prompt,
            parameters: {
              width: 1024,
              height: 1024,
              num_inference_steps: 30,
              guidance_scale: 8,
            },
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const blob = await response.blob();
      const posterImage = URL.createObjectURL(blob);
      setGeneratedPoster(posterImage);
    } catch (error) {
      console.error("Failed to create AI poster:", error);
    } finally {
      setIsGenerating(false);
    }
  };


  return (
    <div className="poster-generator">
      <div className="page-header">
        <h1>AI Poster Generator</h1>
        <p>Create professional Palestine solidarity posters with AI-powered design</p>
      </div>

      <div className="generator-container">
        <div className="editor-section">
          <h2>Design Your AI Poster</h2>
          
          <div className="image-info-section">
            <h3>🎨 AI Poster Generation</h3>
            <div className="info-box">
              <p>Images rotate automatically with each generation:</p>
              <ul>
                <li>1st generation: <strong>Hunger</strong> theme</li>
                <li>2nd generation: <strong>Solidarity</strong> theme</li>
                <li>3rd generation: <strong>Voice</strong> theme</li>
                <li>Then cycles back to Hunger...</li>
              </ul>
            </div>
            {selectedTemplate === 'solidarity' && (
              <div className="ai-notice">
                <p>🤖 This template uses AI generation for unique, creative designs!</p>
              </div>
            )}
          </div>

          <div className="poster-form">
            <div className="form-group">
              <label htmlFor="title">Main Title</label>
              <input
                type="text"
                id="title"
                value={posterData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="Enter main title"
              />
            </div>

            <div className="form-group">
              <label htmlFor="subtitle">Subtitle</label>
              <input
                type="text"
                id="subtitle"
                value={posterData.subtitle}
                onChange={(e) => handleInputChange('subtitle', e.target.value)}
                placeholder="Enter subtitle"
              />
            </div>



            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                value={posterData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Enter event description"
                rows="3"
              />
            </div>

            <div className="form-actions">

              <button className="btn btn-primary" onClick={generatePoster}>
                Generate AI Poster

              </button>
              <button className="btn btn-secondary" onClick={resetPoster}>
                Reset
              </button>
            </div>
          </div>
        </div>

        {/* Poster Preview Section */}
        <div className="preview-section">
          <h2>Generated Poster</h2>
          
          {isGeneratingAi ? (
            <div className="generating-placeholder">
              <div className="loading-spinner">🎨</div>
              <p>Generating your AI poster...</p>
            </div>
          ) : aiDesign && aiDesign.generated_image ? (

            <div className="poster-preview">
              <img 
                src={`data:image/png;base64,${aiDesign.generated_image}`} 
                alt="AI Generated Poster" 
                className="generated-poster-image"
              />
              <div className="poster-actions">
                <button 
                  className="btn btn-primary" 
                  onClick={() => {
                    const link = document.createElement('a');
                    link.download = 'ai-generated-poster.png';
                    link.href = `data:image/png;base64,${aiDesign.generated_image}`;
                    link.click();
                  }}
                >
                  Download Poster
                </button>
              </div>
            </div>
          ) : (
            <div className="poster-placeholder">
              <div className="placeholder-content">
                <div className="placeholder-icon">🎨</div>
                <p>Your AI-generated poster will appear here</p>
                <p>Fill out the form and click "Generate AI Poster"</p>
              </div>
            </div>
          )}

          {aiError && (
            <div className="ai-error">
              {aiError}
            </div>
          )}
        </div>
      </div>

      <div className="tips-section">
        <h2>AI Poster Generation Tips</h2>
        <div className="tips-grid">
          <div className="tip-card">
            <h3>🤖 AI-Powered Design</h3>
            <p>Our AI generates professional posters with Palestinian solidarity themes</p>
          </div>
          <div className="tip-card">
            <h3>🎨 Choose Your Style</h3>
            <p>Select from modern, bold, elegant, minimalist, or vintage styles</p>
          </div>
          <div className="tip-card">
            <h3>📝 Customize Content</h3>
            <p>Add your own title, subtitle, and description for personalized posters</p>
          </div>
          <div className="tip-card">
            <h3>📱 Instant Download</h3>
            <p>Download high-quality PNG files ready for printing or sharing</p>
          </div>
        </div>
      </div>


    </div>
  )
}

export default PosterGenerator 