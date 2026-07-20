import { useState } from 'react'
import './App.css'
import { Routes, Route, useNavigate } from 'react-router-dom'
import PlayerCard from './PlayerCard'
import Header from './Header'
import MyTeam from './MyTeam'
import Leaderboard from './Leaderboard'
import PitcherCard from './PitcherCard'
import { API_BASE_URL } from './config';

const POSITIONS = ["ALL", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH", "P"]

const HITTER_STAT_OPTIONS = [
  { value: "home_runs", label: "HR" },
  { value: "runs", label: "R" },
  { value: "rbi", label: "RBI" },
  { value: "stolen_bases", label: "SB" },
  { value: "avg", label: "AVG" },
  { value: "hits", label: "H" },
  { value: "ops", label: "OPS" },
  { value: "iso", label: "ISO" },
  { value: "discipline", label: "Discipline" },
]

const PITCHER_STAT_OPTIONS = [
  { value: "wins", label: "W" },
  { value: "saves", label: "SV" },
  { value: "strikeouts", label: "K" },
  { value: "era", label: "ERA" },
  { value: "whip", label: "WHIP" },
]

function getStatOptions(position) {
  return position === "P" ? PITCHER_STAT_OPTIONS : HITTER_STAT_OPTIONS
}

function App() {
  const [name, setName] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const [showFilters, setShowFilters] = useState(false);
  const [browsePosition, setBrowsePosition] = useState("ALL");
  const [filterRows, setFilterRows] = useState([{ stat: getStatOptions("ALL")[0].value, min: "" }]);
  const [browseResults, setBrowseResults] = useState([]);
  const [browseLoading, setBrowseLoading] = useState(false);
  const [hasBrowsed, setHasBrowsed] = useState(false);

  async function handleSearch() {
    setLoading(true);
    const response = await fetch(`${API_BASE_URL}/players/search?name=` + name);
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

  function handlePositionChange(newPosition) {
    setBrowsePosition(newPosition);
    setFilterRows([{ stat: getStatOptions(newPosition)[0].value, min: "" }]);
  }

  function addFilterRow() {
    setFilterRows([...filterRows, { stat: getStatOptions(browsePosition)[0].value, min: "" }]);
  }

  function removeFilterRow(index) {
    setFilterRows(filterRows.filter((_, i) => i !== index));
  }

  function updateFilterRow(index, field, value) {
    const updated = filterRows.map((row, i) => (i === index ? { ...row, [field]: value } : row));
    setFilterRows(updated);
  }

  async function handleBrowse() {
    setBrowseLoading(true);
    setHasBrowsed(true);

    const activeFilters = filterRows.filter((row) => row.min !== "");
    const filtersParam = activeFilters.map((row) => `${row.stat}:${row.min}`).join(",");

    const params = new URLSearchParams({ position: browsePosition, limit: "100" });
    if (filtersParam) {
      params.set("filters", filtersParam);
    }

    const response = await fetch(`${API_BASE_URL}/players/browse?` + params.toString());
    const data = await response.json();
    setBrowseResults(data.players || []);
    setBrowseLoading(false);
  }

  return (
    <>
      <Header />
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

            <div className="filter-toggle-row">
              <button
                className={`filter-toggle-button ${showFilters ? 'filter-toggle-active' : ''}`}
                onClick={() => setShowFilters(!showFilters)}
              >
                Filter by position &amp; stats
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
                      onClick={() => {
                        setSelectedPlayer(player);
                        const isPitcher = player.primaryPosition?.abbreviation === "P";
                        navigate(isPitcher ? "/pitchers/" + player.id : "/players/" + player.id);
                      }}
                    >
                      Select
                    </button>
                  </div>
                ))}
              </div>
            )}

            {!loading && searchResults.length === 0 && name.trim() !== "" && (
              <p className="search-status">No players found</p>
            )}

            {showFilters && (
              <div className="browse-card">
                <div className="browse-field">
                  <label className="browse-field-label">Position</label>
                  <div className="select-wrapper">
                    <select
                      className="browse-position-select"
                      value={browsePosition}
                      onChange={(event) => handlePositionChange(event.target.value)}
                    >
                      {POSITIONS.map((pos) => (
                        <option key={pos} value={pos}>{pos === "ALL" ? "All positions" : pos}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {filterRows.map((row, index) => (
                  <div key={index} className="filter-row">
                    <div className="browse-field">
                      <label className="browse-field-label">Stat</label>
                      <div className="select-wrapper">
                        <select
                          className="filter-stat-select"
                          value={row.stat}
                          onChange={(event) => updateFilterRow(index, "stat", event.target.value)}
                        >
                          {getStatOptions(browsePosition).map((option) => (
                            <option key={option.value} value={option.value}>{option.label}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                    <div className="browse-field">
                      <label className="browse-field-label">Minimum</label>
                      <input
                        className="filter-min-input"
                        type="number"
                        step="any"
                        placeholder="0"
                        value={row.min}
                        onChange={(event) => updateFilterRow(index, "min", event.target.value)}
                      />
                    </div>
                    {filterRows.length > 1 && (
                      <button className="filter-remove-button" onClick={() => removeFilterRow(index)}>
                        Remove
                      </button>
                    )}
                  </div>
                ))}

                <div className="browse-actions">
                  <button className="filter-add-button" onClick={addFilterRow}>
                    Add filter
                  </button>
                  <button className="browse-apply-button" onClick={handleBrowse}>
                    Apply filters
                  </button>
                </div>
              </div>
            )}

            {browseLoading && <p className="search-status">Loading players...</p>}

            {!browseLoading && hasBrowsed && browseResults.length === 0 && (
              <p className="search-status">No players match those filters</p>
            )}

            {!browseLoading && browseResults.length > 0 && (
              <div className="browse-results">
                {browseResults.map((player) => (
                  <div key={player.player_id} className="result-row">
                    <img className="browse-headshot" src={player.headshot_url} alt={player.name} />
                    <span className="result-name">{player.name}</span>
                    <span className="result-meta">{player.position} - {player.team}</span>
                    <button
                      className="result-select"
                      onClick={() => {
                        navigate(player.position === "P" ? "/pitchers/" + player.player_id : "/players/" + player.player_id);
                      }}
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
        <Route path="/my-team" element={<MyTeam />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/pitchers/:playerId" element={<PitcherCard />} />
      </Routes>
    </>
  )
}

export default App