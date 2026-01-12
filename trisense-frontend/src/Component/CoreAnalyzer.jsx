/// src/components/CoreAnalyzer.jsx
// YEH FULLY UPDATED CODE HAI

import React, { useState } from 'react'; // Step 1: useState ko import kiya
import './CoreAnalyzer.css';

function CoreAnalyzer() {
  // Step 2: State variables banaye - text, score, aur interpretation ko store karne ke liye
  const [text, setText] = useState('');
  const [score, setScore] = useState('0.00');
  const [interpretation, setInterpretation] = useState('Analysis will appear here.');

  // Step 3: Backend ko call karne wala function banaya
  const handleAnalyze = async () => {
    // Yeh hamara "jaasoos" hai jo check karega ki function chal raha hai ya nahi
    console.log("Analyze button was clicked! The function has started.");
    console.log("Sending this text to backend:", text);

    setInterpretation('Analyzing...'); // User ko bataya ki process shuru ho gaya hai

    try {
      // fetch API ka istemal karke backend ko POST request bhej rahe hain
      const response = await fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // Data ko JSON format mein bhej rahe hain
        body: JSON.stringify({
          text: text,
        } ),
      });

      // Agar response theek nahi hai (jaise 404 ya 500 error), to error throw karega
      if (!response.ok) {
        throw new Error(`Network response was not ok, status: ${response.status}`);
      }

      // Backend se aaye JSON response ko padh rahe hain
      const result = await response.json();
      console.log("Data received from backend:", result);

      // Step 4: UI ko backend se mile data se update kar rahe hain
      const anxietyScore = result.anxiety_score;
      setScore(anxietyScore.toFixed(2)); // Score ko 2 decimal places tak dikha rahe hain

      if (anxietyScore > 0.7) {
        setInterpretation('High anxiety detected. Please take a moment to relax.');
      } else if (anxietyScore > 0.4) {
        setInterpretation('Moderate anxiety detected. Consider taking a short break.');
      } else {
        setInterpretation('Low anxiety detected. You seem to be doing great!');
      }

    } catch (error) {
      // Agar API call mein koi bhi error aata hai, to use console mein dikhayega
      console.error("Error during API call:", error);
      setInterpretation('Could not connect to the server. Is it running?');
    }
  };

  return (
    <div className="analyzer-container">
      <div className="input-section">
        <label htmlFor="text-input">How are you feeling today? Type your thoughts here.</label>
        <textarea
          id="text-input"
          className="text-input-area"
          rows="5"
          placeholder="The more you write, the more accurate the analysis..."
          // Step 5: Textarea ko 'text' state se joda
          value={text}
          onChange={(e) => setText(e.target.value)}
        ></textarea>
      </div>

      <div className="button-section">
        <button className="action-btn record-btn">Record Voice</button>
        <button className="action-btn camera-btn">Use Camera</button>
        {/* Step 6: Button ke click par 'handleAnalyze' function ko joda */}
        <button className="action-btn analyze-btn" onClick={handleAnalyze}>
          Analyze
        </button>
      </div>

      <div className="results-section">
        <h2>Anxiety Score</h2>
        <div className="score-display">
          {/* Step 7: Score ko 'score' state se joda */}
          <p>{score}</p>
        </div>
        {/* Step 8: Interpretation ko 'interpretation' state se joda */}
        <p className="score-interpretation">{interpretation}</p>
      </div>
    </div>
  );
}

export default CoreAnalyzer;
