import { useState } from 'react'
import './BoycottedProducts.css'

function BoycottedProducts() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')

  const boycottedItems = [
    {
      id: 1,
      name: 'McDonald\'s',
      category: 'food',
      description: 'Fast food restaurant chain',
      reason: 'Supporting occupation through business operations',
      alternatives: ['Local halal restaurants', 'Home-cooked meals', 'Other halal chains']
    },
    {
      id: 2,
      name: 'Starbucks',
      category: 'beverages',
      description: 'Coffee chain',
      reason: 'Supporting occupation through business operations',
      alternatives: ['Local coffee shops', 'Home-brewed coffee', 'Halal coffee brands']
    },
    {
      id: 3,
      name: 'Nike',
      category: 'clothing',
      description: 'Sportswear and footwear',
      reason: 'Supporting occupation through business operations',
      alternatives: ['Local sportswear brands', 'Halal clothing stores', 'Ethical sportswear']
    },
    {
      id: 4,
      name: 'Coca-Cola',
      category: 'beverages',
      description: 'Soft drink company',
      reason: 'Supporting occupation through business operations',
      alternatives: ['Local soft drink brands', 'Natural juices', 'Halal beverage companies']
    },
    {
      id: 5,
      name: 'Pepsi',
      category: 'beverages',
      description: 'Soft drink company',
      reason: 'Supporting occupation through business operations',
      alternatives: ['Local soft drink brands', 'Natural juices', 'Halal beverage companies']
    },
    {
      id: 6,
      name: 'KFC',
      category: 'food',
      description: 'Fast food restaurant chain',
      reason: 'Supporting occupation through business operations',
      alternatives: ['Local halal restaurants', 'Home-cooked meals', 'Other halal chains']
    },
    {
      id: 7,
      name: 'Pizza Hut',
      category: 'food',
      description: 'Pizza restaurant chain',
      reason: 'Supporting occupation through business operations',
      alternatives: ['Local halal pizza places', 'Home-made pizza', 'Halal pizza chains']
    },
    {
      id: 8,
      name: 'Adidas',
      category: 'clothing',
      description: 'Sportswear and footwear',
      reason: 'Supporting occupation through business operations',
      alternatives: ['Local sportswear brands', 'Halal clothing stores', 'Ethical sportswear']
    }
  ]

  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'food', label: 'Food & Restaurants' },
    { value: 'beverages', label: 'Beverages' },
    { value: 'clothing', label: 'Clothing & Fashion' }
  ]

  const filteredItems = boycottedItems.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className="boycotted-products">
      <div className="page-header">
        <h1>Boycotted Products</h1>
        <p>Support justice by avoiding these companies and products. Choose ethical alternatives.</p>
      </div>

      <div className="search-filters">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search products or companies..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="category-filter">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="category-select"
          >
            {categories.map(category => (
              <option key={category.value} value={category.value}>
                {category.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="products-grid">
        {filteredItems.map(item => (
          <div key={item.id} className="product-card">
            <div className="product-header">
              <h3 className="product-name">{item.name}</h3>
              <span className={`category-badge ${item.category}`}>
                {categories.find(cat => cat.value === item.category)?.label}
              </span>
            </div>
            <p className="product-description">{item.description}</p>
            <div className="product-details">
              <div className="reason-section">
                <h4>Why to Boycott:</h4>
                <p>{item.reason}</p>
              </div>
              <div className="alternatives-section">
                <h4>Better Alternatives:</h4>
                <ul>
                  {item.alternatives.map((alternative, index) => (
                    <li key={index}>{alternative}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredItems.length === 0 && (
        <div className="no-results">
          <p>No products found matching your search criteria.</p>
        </div>
      )}

      <div className="info-section">
        <h2>Why Boycott?</h2>
        <p>Economic boycotts are a peaceful way to express solidarity and support for justice. 
        By choosing not to support companies that contribute to oppression, we can make a difference 
        through our consumer choices.</p>
        
        <h3>How to Get Involved:</h3>
        <ul>
          <li>Share this information with family and friends</li>
          <li>Choose local and ethical alternatives</li>
          <li>Support businesses that align with your values</li>
          <li>Spread awareness on social media</li>
        </ul>
      </div>
    </div>
  )
}

export default BoycottedProducts 