import React, { useState } from 'react';
import OpenAI from 'openai';
import './App.css';

const App: React.FC = () => {
  const [occasion, setOccasion] = useState('');
  const [recommendation, setRecommendation] = useState('');
  const [loading, setLoading] = useState(false);

  const openai = new OpenAI({
    apiKey: process.env.REACT_APP_OPENAI_API_KEY,
    dangerouslyAllowBrowser: true
  });

  const generateRecommendation = async () => {
    if (!occasion.trim()) {
      alert('Please enter an occasion');
      return;
    }

    setLoading(true);
    try {
      const response = await openai.chat.completions.create({
        model: "gpt-3.5-turbo",
        messages: [
          {
            role: "system", 
            content: "You are a fashion advisor. Provide detailed clothing recommendations based on the occasion."
          },
          {
            role: "user", 
            content: `What should I wear for a ${occasion}? Give specific outfit suggestions with details about style, color, and accessories.`
          }
        ],
        max_tokens: 200
      });

      const recommendationText = response.choices[0].message?.content || 'No recommendation available';
      setRecommendation(recommendationText);
    } catch (error) {
      console.error('Error generating recommendation:', error);
      setRecommendation('Sorry, unable to generate recommendation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>WearWise 👗👔</h1>
        <p>Get personalized outfit recommendations for any occasion!</p>
      </header>
      <main>
        <div className="input-container">
          <input 
            type="text" 
            value={occasion} 
            onChange={(e) => setOccasion(e.target.value)}
            placeholder="Enter occasion (e.g., job interview, beach party)"
          />
          <button onClick={generateRecommendation} disabled={loading}>
            {loading ? 'Generating...' : 'Get Recommendation'}
          </button>
        </div>
        {recommendation && (
          <div className="recommendation-container">
            <h2>Your Outfit Recommendation:</h2>
            <p>{recommendation}</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
