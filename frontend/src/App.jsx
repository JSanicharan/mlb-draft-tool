import { useState } from 'react'
import './App.css'

function App() {
  const [name, setName] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState (null);
  const [loading, setLoading] = useState(false);

  async function handleSearch() {
    const response = await fetch("http://127.0.0.1:8000/players/search?name=" + name);
    const data = await response.json();
    const people= data.people;
    setSearchResults(people);
  }

  return (
    <>
      <input 
        value={name} 
        onChange={(event) => setName(event.target.value)}
      />
      <button onClick={() => handleSearch()}>Search</button>
      {searchResults.map((player) =>(
        <div key = {player.id}>
          {player.fullName}
          <button onClick= {() => setSelectedPlayer(player)}>Select</button>
        </div>
      ))}
    </>
  )
}

export default App
