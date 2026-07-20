import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Leaderboard.css';
import { API_BASE_URL } from './config';

const HITTER_CATEGORIES = [
  { key: 'home_runs', label: 'HR' },
  { key: 'rbi', label: 'RBI' },
  { key: 'runs', label: 'R' },
  { key: 'stolen_bases', label: 'SB' },
  { key: 'avg', label: 'AVG' },
  { key: 'hits', label: 'H' },
  { key: 'ops', label: 'OPS' },
  { key: 'iso', label: 'ISO' },
  { key: 'discipline', label: 'Discipline' },
];

const PITCHER_CATEGORIES = [
  { key: 'wins', label: 'W' },
  { key: 'saves', label: 'SV' },
  { key: 'strikeouts', label: 'K' },
  { key: 'era', label: 'ERA' },
  { key: 'whip', label: 'WHIP' },
];

const PITCHER_CATEGORY_KEYS = PITCHER_CATEGORIES.map((c) => c.key);

function formatValue(category, value) {
  if (category === 'era' || category === 'whip') {
    return value.toFixed(2);
  }
  if (category === 'avg' || category === 'ops' || category === 'iso') {
    return value.toFixed(3);
  }
  if (category === 'discipline') {
    return value.toFixed(2);
  }
  return Math.round(value);
}

export default function Leaderboard() {
  const [activeCategory, setActiveCategory] = useState('home_runs');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    async function fetchLeaderboard() {
      const response = await fetch(
        `${API_BASE_URL}/leaderboard?category=${activeCategory}&limit=20`
      );
      const result = await response.json();
      if (!cancelled) {
        setData(result);
        setLoading(false);
      }
    }
    fetchLeaderboard();

    return () => { cancelled = true; };
  }, [activeCategory]);

  return (
    <div className="leaderboard-page">
      <h2 className="leaderboard-heading">Leaderboard</h2>
      <p className="leaderboard-subtext">
        Find the top players in any category to fill gaps in your roster.
      </p>

      <div className="category-pills">
        {HITTER_CATEGORIES.map((cat) => (
          <button
            key={cat.key}
            className={`category-pill ${activeCategory === cat.key ? 'category-pill-active' : ''}`}
            onClick={() => setActiveCategory(cat.key)}
          >
            {cat.label}
          </button>
        ))}
      </div>

      <div className="category-pills">
        {PITCHER_CATEGORIES.map((cat) => (
          <button
            key={cat.key}
            className={`category-pill category-pill-pitcher ${activeCategory === cat.key ? 'category-pill-active' : ''}`}
            onClick={() => setActiveCategory(cat.key)}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {loading && <p className="leaderboard-status">Loading...</p>}

      {!loading && data && data.players && (
        <div className="leaderboard-list">
          {data.players.map((player, index) => (
            <div
              key={player.player_id}
              className="leaderboard-row"
              onClick={() => {
                const isPitcher = PITCHER_CATEGORY_KEYS.includes(activeCategory);
                navigate(isPitcher ? '/pitchers/' + player.player_id : '/players/' + player.player_id);
              }}
            >
              <span className="leaderboard-rank">{index + 1}</span>
              <img
                className="leaderboard-avatar"
                src={player.headshot_url}
                alt={player.name}
                onError={(e) => { e.target.style.visibility = 'hidden'; }}
              />
              <div className="leaderboard-player-info">
                <span className="leaderboard-name">{player.name}</span>
                <span className="leaderboard-team">{player.team}</span>
              </div>
              <span className="leaderboard-value">
                {formatValue(activeCategory, player.value)}
              </span>
            </div>
          ))}
        </div>
      )}

      {!loading && data && data.error && (
        <p className="leaderboard-status">{data.error}</p>
      )}
    </div>
  );
}