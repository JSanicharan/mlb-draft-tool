import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'

function App() {
  const [name, setName] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState (null);
  const [loading, setLoading] = useState(false);


  return (
    <>
      
    </>
  )
}

export default App
