import { useState } from 'react'
import './App.css'
import { Routes, Route, useNavigate } from 'react-router-dom'
import PlayerCard from './PlayerCard'

function App() {
  const [name, setName] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSearch() {
    setLoading(true);
    const response = await fetch("http://127.0.0.1:8000/players/search?name=" + name);
    const data = await response.json();
    const people = data.people;
    setSearchResults(people);
    setLoading(false);
  }

  function handleKeyDown(event) {
    if (event.key === "Enter") {
      handleSearch();
    }
  }

  return (
    <Routes>
      <Route path="/" element={
        <div className="search-page">
          <h1 className="search-title">Diamond Report</h1>
          <div className="search-bar">
            <input
              className="search-input"
              placeholder="Search a player..."
              value={name}
              onChange={(event) => setName(event.target.value)}
              onKeyDown={handleKeyDown}
            />
            <button className="search-button" onClick={() => handleSearch()}>
              Search
            </button>
          </div>

          {loading && <p className="search-status">Searching...</p>}

          {searchResults.length > 0 && (
            <div className="search-results">
              {searchResults.map((player) => (
                <div key={player.id} className="result-row">
                  <span className="result-name">{player.fullName}</span>
                  <button
                    className="result-select"
                    onClick={() => { setSelectedPlayer(player); navigate("/players/" + player.id); }}
                  >
                    Select
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      } />
      <Route path="/players/:playerId" element={<PlayerCard />} />
    </Routes>
  )
}

export default App