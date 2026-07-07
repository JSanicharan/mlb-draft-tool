import { useState } from 'react'
import './App.css'
import { Routes, Route, useNavigate} from 'react-router-dom'
import PlayerCard from './PlayerCard'

function App() {
  const [name, setName] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState (null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSearch() {
    const response = await fetch("http://127.0.0.1:8000/players/search?name=" + name);
    const data = await response.json();
    const people= data.people;
    setSearchResults(people);
  }
  
return (
    <Routes>
      <Route path="/" element={
        <>
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
          <button onClick={() => handleSearch()}>Search</button>
          {searchResults.map((player) => (
            <div key={player.id}>
              {player.fullName}
              <button onClick={() => { setSelectedPlayer(player);navigate("/players/" + player.id);}}>Select</button>
            </div>
          ))}
        </>
      } />
      <Route path="/players/:playerId" element={<PlayerCard />} />
    </Routes>
  )
}

export default App
