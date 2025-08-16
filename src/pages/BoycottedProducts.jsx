import { useState, useRef, useEffect } from 'react'
import './BoycottedProducts.css'

const BoycottedProducts = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showScanner, setShowScanner] = useState(false)
  const [scannedBarcode, setScannedBarcode] = useState(null)
  const [showFileUpload, setShowFileUpload] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [scanMode, setScanMode] = useState('') // 'camera' or 'file'
  const [brandSuggestions, setBrandSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  
  const fileInputRef = useRef(null)
  const videoRef = useRef(null)

  // Load brand suggestions on component mount
  useEffect(() => {
    loadBrandSuggestions()
  }, [])

  const loadBrandSuggestions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/brands')
      if (response.ok) {
        const data = await response.json()
        setBrandSuggestions(data.brands)
      }
    } catch (err) {
      console.error('Error loading brand suggestions:', err)
    }
  }

  const getFilteredSuggestions = () => {
    if (!searchQuery.trim()) return []
    return brandSuggestions.filter(brand => 
      brand.toLowerCase().includes(searchQuery.toLowerCase())
    ).slice(0, 5) // Show max 5 suggestions
  }

  const handleSuggestionClick = (suggestion) => {
    setSearchQuery(suggestion)
    setShowSuggestions(false)
    performSearch(suggestion)
  }

  const performSearch = async (query) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('http://localhost:8000/api/search-product', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      })
      
      if (!response.ok) {
        throw new Error('Failed to search product')
      }
      
      const data = await response.json()
      setSearchResults(data)
    } catch (err) {
      setError('Error searching for product. Please try again.')
      console.error('Search error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    setShowSuggestions(false)
    if (searchQuery.trim()) {
      performSearch(searchQuery.trim())
    }
  }

  const clearSearch = () => {
    setSearchQuery('')
    setSearchResults(null)
    setError(null)
    setScannedBarcode(null)
    setShowSuggestions(false)
  }

  // Add click outside handler
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.search-input-container')) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleBarcodeScan = async (barcode) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('http://localhost:8000/api/scan-barcode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ barcode }),
      })
      
      if (!response.ok) {
        throw new Error('Failed to scan barcode')
      }
      
      const data = await response.json()
      setScannedBarcode(data)
      setSearchResults(null)
    } catch (err) {
      setError('Error scanning barcode. Please try again.')
      console.error('Barcode scan error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const startCameraScan = () => {
    setScanMode('camera')
    setShowScanner(true)
    setShowFileUpload(false)
    setError(null)
    
    // Check if we're on HTTPS or localhost (required for camera access)
    const isSecure = window.location.protocol === 'https:' || window.location.hostname === 'localhost'
    
    if (!isSecure) {
      setError('Camera access requires HTTPS. Please use file upload or manual entry instead.')
      return
    }
    
    // Request camera access
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } 
      })
        .then((stream) => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream
            videoRef.current.onloadedmetadata = () => {
              videoRef.current.play()
            }
          }
        })
        .catch((err) => {
          console.error('Camera access error:', err)
          if (err.name === 'NotAllowedError') {
            setError('Camera access denied. Please allow camera permissions and try again.')
          } else if (err.name === 'NotFoundError') {
            setError('No camera found on this device. Please use file upload or manual entry.')
          } else {
            setError('Unable to access camera. Please try file upload or manual entry instead.')
          }
        })
    } else {
      setError('Camera not supported on this device. Please use file upload or manual entry.')
    }
  }

  const stopCameraScan = () => {
    setShowScanner(false)
    setScanMode('')
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks()
      tracks.forEach(track => track.stop())
    }
  }

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFile(file)
      setShowFileUpload(true)
      setShowScanner(false)
      setScanMode('file')
    }
  }

  const processFileUpload = async () => {
    if (!selectedFile) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      // Create FormData to send the image file
      const formData = new FormData()
      formData.append('file', selectedFile)
      
      const response = await fetch('http://localhost:8000/api/upload-image', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error('Failed to process image')
      }
      
      const data = await response.json()
      
      // Create a barcode scan result object from the image processing response
      const barcodeResult = {
        barcode: data.barcode,
        is_israeli: data.is_israeli,
        country: data.country,
        message: data.analysis.message,
        alternatives: data.analysis.alternatives
      }
      
      setScannedBarcode(barcodeResult)
      setSearchResults(null)
      
      // Close the file upload interface
      setShowFileUpload(false)
      setSelectedFile(null)
      setScanMode('')
      
    } catch (err) {
      setError('Error processing image. Please try again or use manual entry.')
      console.error('File upload error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleManualBarcode = () => {
    const barcode = prompt('Enter barcode number:')
    if (barcode && barcode.trim()) {
      handleBarcodeScan(barcode.trim())
    }
  }

  return (
    <div className="boycotted-products">
      <div className="page-header">
        <h1>Boycotted Products Scanner</h1>
        <p>Search for products or scan barcodes to check if they are boycotted and find Palestinian alternatives</p>
      </div>

      <div className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-group">
            <div className="search-input-container">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value)
                  setShowSuggestions(true)
                }}
                onFocus={() => setShowSuggestions(true)}
                placeholder="Enter product name or brand..."
                className="search-input"
                disabled={isLoading}
              />
              {showSuggestions && getFilteredSuggestions().length > 0 && (
                <div className="suggestions-dropdown">
                  {getFilteredSuggestions().map((suggestion, index) => (
                    <div
                      key={index}
                      className="suggestion-item"
                      onClick={() => handleSuggestionClick(suggestion)}
                    >
                      {suggestion}
                    </div>
                  ))}
                </div>
              )}
            </div>
            <button type="submit" className="search-button" disabled={isLoading || !searchQuery.trim()}>
              {isLoading ? 'Searching...' : 'Search'}
            </button>
          </div>
          
          <div className="scan-options">
            <button 
              type="button" 
              className="scan-button camera"
              onClick={startCameraScan}
              disabled={isLoading}
            >
              📷 Camera Scan
            </button>
            <button 
              type="button" 
              className="scan-button file"
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading}
            >
              📁 Upload Image
            </button>
            <button 
              type="button" 
              className="scan-button manual"
              onClick={handleManualBarcode}
              disabled={isLoading}
            >
              ⌨️ Manual Entry
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </div>
        </form>

        {error && <div className="error-message">{error}</div>}
        {isLoading && <div className="loading-message">Processing...</div>}
      </div>

      {/* Camera Scanner */}
      {showScanner && (
        <div className="scanner-overlay">
          <div className="scanner-container">
            <h3>📷 Camera Scanner</h3>
            <p>Point your camera at a barcode to scan</p>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="scanner-video"
            />
            <div className="scanner-controls">
              <button 
                className="scan-button manual"
                onClick={handleManualBarcode}
              >
                ⌨️ Enter Manually
              </button>
              <button 
                className="scan-button process"
                onClick={() => {
                  // For now, simulate barcode detection for demo
                  // In a real implementation, you would use a barcode scanning library
                  // like QuaggaJS or ZXing to detect barcodes from the video stream
                  const simulatedBarcode = '8419876543210' // Another Israeli barcode
                  handleBarcodeScan(simulatedBarcode)
                  stopCameraScan()
                }}
              >
                🔍 Scan Barcode
              </button>
              <button 
                className="scan-button cancel"
                onClick={stopCameraScan}
              >
                ❌ Close Scanner
              </button>
            </div>
          </div>
        </div>
      )}

      {/* File Upload */}
      {showFileUpload && selectedFile && (
        <div className="file-upload-section">
          <h3>📁 Image Upload</h3>
          <p>Selected file: {selectedFile.name}</p>
          <div className="file-controls">
            <button 
              className="scan-button process"
              onClick={processFileUpload}
              disabled={isLoading}
            >
              🔍 Process Image
            </button>
            <button 
              className="scan-button cancel"
              onClick={() => {
                setShowFileUpload(false)
                setSelectedFile(null)
                setScanMode('')
              }}
            >
              ❌ Cancel
            </button>
          </div>
        </div>
      )}

      {/* Search Results */}
      {searchResults && (
        <div className="result-section">
          <div className={`result-card ${searchResults.is_boycotted ? 'boycotted' : 'safe'}`}>
            <div className="result-header">
              <h2>{searchResults.brand_name}</h2>
              <span className={`status-badge ${searchResults.is_boycotted ? 'boycotted' : 'safe'}`}>
                {searchResults.is_boycotted ? 'BOYCOTTED' : 'SAFE'}
              </span>
            </div>
            <div className="result-content">
              <p className="result-message">{searchResults.message}</p>
              {searchResults.product_description && (
                <div className="product-description">
                  <h3>About this product:</h3>
                  <p>{searchResults.product_description}</p>
                </div>
              )}
              <div className="category-info">
                Category: {searchResults.category}
              </div>
              {searchResults.is_boycotted && (
                <div className="boycott-info">
                  <h3>Why is this boycotted?</h3>
                  <p>{searchResults.boycott_reason}</p>
                </div>
              )}
              {searchResults.alternatives && searchResults.alternatives.length > 0 ? (
                <div className="alternatives-section">
                  <h3>Alternatives:</h3>
                  <div className="alternatives-list">
                    {searchResults.alternatives.map((alternative, index) => (
                      <div key={index} className="alternative-item">
                        <span className="alternative-bullet">•</span>
                        <span className="alternative-text">{alternative}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="no-alternatives">
                  <p>No alternatives available for this product.</p>
                </div>
              )}
              <button className="new-search-button" onClick={clearSearch}>
                Search Another Product
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Barcode Scan Results */}
      {scannedBarcode && (
        <div className="result-section">
          <div className={`result-card ${scannedBarcode.is_israeli ? 'boycotted' : 'safe'}`}>
            <div className="result-header">
              <h2>Barcode: {scannedBarcode.barcode}</h2>
              <span className={`status-badge ${scannedBarcode.is_israeli ? 'boycotted' : 'safe'}`}>
                {scannedBarcode.is_israeli ? 'ISRAELI' : 'SAFE'}
              </span>
            </div>
            <div className="result-content">
              <p className="result-message">{scannedBarcode.message}</p>
              <div className="category-info">
                Country: {scannedBarcode.country}
              </div>
              {scannedBarcode.is_israeli && scannedBarcode.alternatives.length > 0 && (
                <div className="alternatives-section">
                  <h3>Alternatives:</h3>
                  <div className="alternatives-list">
                    {scannedBarcode.alternatives.map((alternative, index) => (
                      <div key={index} className="alternative-item">
                        <span className="alternative-bullet">•</span>
                        <span className="alternative-text">{alternative}</span>
          </div>
        ))}
      </div>
                </div>
              )}
              <button className="new-search-button" onClick={clearSearch}>
                Scan Another Barcode
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="info-section">
        <h2>How to Use the Scanner</h2>
        <p>This tool helps you identify boycotted products and find Palestinian alternatives:</p>
        
        <h3>Search by Name</h3>
        <p>Enter the product or brand name in the search bar to check if it's boycotted.</p>
        
        <h3>Barcode Scanning</h3>
        <p>Scan product barcodes to automatically detect Israeli products:</p>
        <ul>
          <li><strong>Israeli Barcodes:</strong> Products with barcodes starting with 729, 841, or 871 are Israeli</li>
          <li><strong>Camera Scan:</strong> Use your device camera to scan barcodes in real-time</li>
          <li><strong>Image Upload:</strong> Upload photos of product barcodes for analysis</li>
          <li><strong>Manual Entry:</strong> Type barcode numbers manually</li>
        </ul>
        
        <h3>Why Boycott Israeli Products?</h3>
        <p>Boycotting Israeli products is a peaceful way to support Palestinian rights and oppose occupation. By choosing alternatives, you can:</p>
        <ul>
          <li>Support Palestinian businesses and economy</li>
          <li>Reduce funding for occupation and settlements</li>
          <li>Promote ethical consumerism</li>
          <li>Stand in solidarity with Palestinian people</li>
        </ul>
        
        <div className="search-tips">
          <h3>💡 Search Tips</h3>
          <ul>
            <li>Try different variations of brand names (e.g., "Nike", "Nike shoes", "Nike sports")</li>
            <li>Use the camera scanner for quick barcode detection</li>
            <li>Upload clear, well-lit images of barcodes for better results</li>
            <li>Check the alternatives section for local and ethical options</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default BoycottedProducts 