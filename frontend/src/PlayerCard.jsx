import { useParams } from 'react-router-dom'
import { useState, useEffect } from 'react'

function PlayerCard() {
  const { playerId } = useParams()
  const [profile, setProfile] = useState(null)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    async function fetchProfile() {
      const response = await fetch("http://127.0.0.1:8000/players/" + playerId + "/profile")
      if (!response.ok) {
        setNotFound(true)
        return
      }
      const data = await response.json()
      setProfile(data)
    }
    fetchProfile()
  }, [playerId])

  if (notFound) {
    return <div>Player not found</div>
  }
  if (!profile) {
    return <div>Loading...</div>
  }

  return (
    <div>
      <img src={profile.player.headshot_url} alt={profile.player.name} />
      <h2>{profile.player.name}</h2>
      <p>{profile.player.team}</p>
      <p>{profile.player.position}</p>
      <p>Age: {profile.player.age}</p>
      <p>Bats: {profile.player.bat_side.description} / Throws: {profile.player.throw_side.description}</p>
      <p>Draft Score: {profile.draft_score}</p>
    </div>
  )
}

export default PlayerCard