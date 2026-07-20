import { useParams, useNavigate } from 'react-router-dom'
import { useState, useEffect, useRef } from 'react'
import { useTeam } from './TeamContext'
import './PlayerCard.css'
import { API_BASE_URL } from './config';

function StatRow({ label, value, percentile }) {
  const isBelowAverage = percentile < 50;
  return (
    <div className="stat-row">
      <span className="stat-label">{label}</span>
      <span className="stat-value">{value}</span>
      <div className="stat-bar-track">
        <div
          className={`stat-bar-fill ${isBelowAverage ? 'below-average' : ''}`}
          style={{ width: `${percentile}%` }}
        />
      </div>
      <span className="stat-percentile">{percentile}th</span>
    </div>
  )
}

function PlayerCard() {
  const { playerId } = useParams()
  const navigate = useNavigate()
  const [profile, setProfile] = useState(null)
  const [notFound, setNotFound] = useState(false)
  const hasFetched = useRef(false)
  const { addPlayer, removePlayer, isOnTeam } = useTeam()

  useEffect(() => {
    if (hasFetched.current) return
    hasFetched.current = true

    async function fetchProfile() {
      const response = await fetch(`${API_BASE_URL}/players/${playerId}/profile`)
      if (!response.ok) {
        setNotFound(true)
        return
      }
      const data = await response.json()
      setProfile(data)
    }
    fetchProfile()
  }, [playerId])

  function handleBack() {
    if (window.history.state && window.history.state.idx > 0) {
      navigate(-1)
    } else {
      navigate("/")
    }
  }

  if (notFound) {
    return (
      <div className="player-page">
        <button className="back-button" onClick={handleBack}>
          <i className="ti ti-arrow-left"></i> Back
        </button>
        <div className="player-status">Player not found</div>
      </div>
    )
  }
  if (!profile) {
    return (
      <div className="player-page">
        <button className="back-button" onClick={handleBack}>
          <i className="ti ti-arrow-left"></i> Back
        </button>
        <div className="player-status">Loading...</div>
      </div>
    )
  }

  const { player, draft_score, ml_score, ai_summary, scoring_stats, baseline_stats } = profile;
  const onTeam = isOnTeam(playerId);

  function handleTeamToggle() {
    if (onTeam) {
      removePlayer(playerId);
      return;
    }
    addPlayer(
      {
        playerId,
        name: player.name,
        position: player.position,
        photoUrl: player.headshot_url,
        team: player.team,
      },
      player.position
    );
  }

  return (
    <div className="player-page">
      <button className="back-button" onClick={handleBack}>
        <i className="ti ti-arrow-left"></i> Back
      </button>

      <div className="player-header">
        <div className="player-identity">
          <img className="player-headshot" src={player.headshot_url} alt={player.name} />
          <h2 className="player-name">{player.name}</h2>
          <p className="player-meta">{player.position} - {player.team}</p>
          <p className="player-meta-sub">Age {player.age} · Bats {player.bat_side.description} / Throws {player.throw_side.description}</p>
          <button
            className={`team-toggle-button ${onTeam ? 'team-toggle-active' : ''}`}
            onClick={handleTeamToggle}
          >
            {onTeam ? 'Remove from team' : 'Add to team'}
          </button>
        </div>

        <div className="player-scores">
          <div className="score-card score-card-primary">
            <span className="score-label">Draft score</span>
            <span className="score-value">{draft_score.toFixed(2)}</span>
          </div>
          <div className="score-card">
            <span className="score-label">Next season projection <span className="beta-tag">Beta</span></span>
            <span className="score-value">{ml_score ?? '—'}</span>
          </div>
        </div>
      </div>

      {ai_summary && (
        <div className="ai-summary">
          <span className="ai-summary-label">AI summary</span>
          <p>{ai_summary}</p>
        </div>
      )}

      {scoring_stats && scoring_stats.length > 0 && (
        <div className="stat-section">
          <span className="stat-section-label">Scoring categories</span>
          {scoring_stats.map((stat) => (
            <StatRow key={stat.label} {...stat} />
          ))}
        </div>
      )}

      {baseline_stats && baseline_stats.length > 0 && (
        <div className="stat-section">
          <span className="stat-section-label">Baseline stats</span>
          {baseline_stats.map((stat) => (
            <StatRow key={stat.label} {...stat} />
          ))}
        </div>
      )}
    </div>
  )
}

export default PlayerCard