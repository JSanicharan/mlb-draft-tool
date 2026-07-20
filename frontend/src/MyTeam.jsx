import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTeam } from './TeamContext';
import './MyTeam.css';

const FIELD_POSITIONS = [
  { slot: 'C', top: '85%', left: '50%' },
  { slot: 'P', top: '62%', left: '50%' },
  { slot: '3B', top: '54%', left: '25%' },
  { slot: '1B', top: '54%', left: '75%' },
  { slot: 'SS', top: '41%', left: '38%' },
  { slot: '2B', top: '41%', left: '62%' },
  { slot: 'LF', top: '26%', left: '12%' },
  { slot: 'CF', top: '12%', left: '50%' },
  { slot: 'RF', top: '26%', left: '88%' },
  { slot: 'DH', top: '90%', left: '92%' },
];

const CATEGORY_KEY_MAP = {
  HR: 'home_runs', R: 'runs', RBI: 'rbi', SB: 'stolen_bases',
  AVG: 'avg', H: 'hits', OPS: 'ops', ISO: 'iso', Discipline: 'discipline',
  W: 'wins', SV: 'saves', K: 'strikeouts', ERA: 'era', WHIP: 'whip',
};

const CATEGORY_DISPLAY_LABELS = {
  home_runs: 'HR', runs: 'R', rbi: 'RBI', stolen_bases: 'SB',
  avg: 'AVG', hits: 'H', ops: 'OPS', iso: 'ISO', discipline: 'Discipline',
  wins: 'W', saves: 'SV', strikeouts: 'K', era: 'ERA', whip: 'WHIP',
};

const PITCHER_CATEGORY_KEYS = ['wins', 'saves', 'strikeouts', 'era', 'whip'];
const RATE_LABELS = new Set(['AVG', 'OPS', 'ISO', 'Discipline', 'ERA', 'WHIP', 'FIP']);
const PITCHER_ONLY_LABELS = new Set(['W', 'SV', 'K', 'ERA', 'WHIP', 'FIP']);

function computeTeamStats(profiles) {
  const totals = {};

  for (const profile of Object.values(profiles)) {
    if (!profile) continue;
    const allStats = [...(profile.scoring_stats || []), ...(profile.baseline_stats || [])];
    for (const stat of allStats) {
      if (!totals[stat.label]) totals[stat.label] = { sum: 0, count: 0 };
      totals[stat.label].sum += stat.value;
      totals[stat.label].count += 1;
    }
  }

  const hitting = [];
  const pitching = [];

  for (const [label, { sum, count }] of Object.entries(totals)) {
    const isRate = RATE_LABELS.has(label);
    let value;
    if (isRate) {
      const decimals = (label === 'AVG' || label === 'OPS' || label === 'ISO') ? 3 : 2;
      value = (sum / count).toFixed(decimals);
    } else {
      value = Math.round(sum);
    }
    const entry = { label, value };
    if (PITCHER_ONLY_LABELS.has(label)) {
      pitching.push(entry);
    } else {
      hitting.push(entry);
    }
  }

  return { hitting, pitching };
}

function PlayerAvatar({ player }) {
  if (player?.photoUrl) {
    return (
      <img
        className="player-avatar-img"
        src={player.photoUrl}
        alt={player.name}
        onError={(e) => { e.target.style.display = 'none'; }}
      />
    );
  }
  return (
    <div className="player-avatar-fallback">
      <i className="ti ti-user"></i>
    </div>
  );
}

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
  );
}

function FieldCard({ slot, player, onClick }) {
  return (
    <div
      className={`field-card ${!player ? 'field-card-empty' : ''}`}
      onClick={player ? onClick : undefined}
    >
      <div className="field-card-avatar-slot">
        {player ? <PlayerAvatar player={player} /> : <div className="avatar-placeholder" />}
      </div>
      <span className="field-card-slot">{slot}</span>
      <span className="field-card-name">
        {player ? player.name : 'Empty'}
      </span>
    </div>
  );
}

function PlayerModal({ player, profile, loading, onClose, onViewFullPage }) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Close">
          ×
        </button>

        <div className="modal-header">
          <PlayerAvatar player={player} />
          <div>
            <h3 className="modal-name">{player.name}</h3>
            <p className="modal-meta">{player.position} · {player.team}</p>
          </div>
        </div>

        {loading && <p className="modal-status">Loading stats...</p>}

        {!loading && profile && (
          <>
            <div className="modal-score">
              <span className="score-label">Draft score</span>
              <span className="score-value">{profile.draft_score.toFixed(2)}</span>
            </div>

            {profile.scoring_stats && profile.scoring_stats.length > 0 && (
              <div className="stat-section">
                <span className="stat-section-label">Scoring categories</span>
                {profile.scoring_stats.map((stat) => (
                  <StatRow key={stat.label} {...stat} />
                ))}
              </div>
            )}

            {profile.baseline_stats && profile.baseline_stats.length > 0 && (
              <div className="stat-section">
                <span className="stat-section-label">Baseline stats</span>
                {profile.baseline_stats.map((stat) => (
                  <StatRow key={stat.label} {...stat} />
                ))}
              </div>
            )}
          </>
        )}

        {!loading && !profile && (
          <p className="modal-status">Couldn't load stats for this player.</p>
        )}

        <button className="modal-view-full" onClick={onViewFullPage}>
          View full page
        </button>
      </div>
    </div>
  );
}

export default function MyTeam() {
  const { roster, rosterCount } = useTeam();
  const navigate = useNavigate();
  const [profiles, setProfiles] = useState({});
  const [profilesLoading, setProfilesLoading] = useState(true);
  const [spotFillers, setSpotFillers] = useState({});
  const [boosterCategory, setBoosterCategory] = useState(null);
  const [boosterPlayers, setBoosterPlayers] = useState([]);
  const [modalPlayer, setModalPlayer] = useState(null);

  const allRosteredPlayers = [
    ...Object.entries(roster).filter(([key]) => key !== 'bench').map(([, p]) => p),
    ...roster.bench,
  ].filter(Boolean);

  const rosterIds = allRosteredPlayers.map((p) => p.playerId);
  const teamStats = computeTeamStats(profiles);

  useEffect(() => {
    if (allRosteredPlayers.length === 0) {
      setProfilesLoading(false);
      return;
    }

    let cancelled = false;
    setProfilesLoading(true);

    async function fetchAllProfiles() {
      const entries = await Promise.all(
        allRosteredPlayers.map(async (player) => {
          const isPitcher = player.position === 'P';
          const endpoint = isPitcher
            ? `http://127.0.0.1:8000/pitchers/${player.playerId}/profile`
            : `http://127.0.0.1:8000/players/${player.playerId}/profile`;
          try {
            const response = await fetch(endpoint);
            if (!response.ok) return [player.playerId, null];
            const data = await response.json();
            return [player.playerId, data];
          } catch {
            return [player.playerId, null];
          }
        })
      );

      if (cancelled) return;
      const profileMap = Object.fromEntries(entries);
      setProfiles(profileMap);
      setProfilesLoading(false);
    }

    fetchAllProfiles();
    return () => { cancelled = true; };
  }, [rosterCount]);

  useEffect(() => {
    if (profilesLoading || Object.keys(profiles).length === 0) return;

    const totals = {};
    for (const profile of Object.values(profiles)) {
      if (!profile) continue;
      const allStats = [...(profile.scoring_stats || []), ...(profile.baseline_stats || [])];
      for (const stat of allStats) {
        const key = CATEGORY_KEY_MAP[stat.label];
        if (!key) continue;
        if (!totals[key]) totals[key] = { sum: 0, count: 0 };
        totals[key].sum += stat.percentile;
        totals[key].count += 1;
      }
    }

    let weakestKey = null;
    let weakestAvg = 101;
    for (const [key, { sum, count }] of Object.entries(totals)) {
      const avg = sum / count;
      if (avg < weakestAvg) {
        weakestAvg = avg;
        weakestKey = key;
      }
    }

    setBoosterCategory(weakestKey);
  }, [profiles, profilesLoading]);

  useEffect(() => {
    if (!boosterCategory) return;
    let cancelled = false;

    async function fetchBooster() {
      const response = await fetch(
        `http://127.0.0.1:8000/leaderboard?category=${boosterCategory}&limit=10`
      );
      const result = await response.json();
      if (cancelled || !result.players) return;
      const filtered = result.players.filter((p) => !rosterIds.includes(p.player_id)).slice(0, 5);
      setBoosterPlayers(filtered);
    }

    fetchBooster();
    return () => { cancelled = true; };
  }, [boosterCategory]);

  useEffect(() => {
    if (rosterCount === 0) return;
    const emptySlots = FIELD_POSITIONS.filter(({ slot }) => !roster[slot]);
    if (emptySlots.length === 0) {
      setSpotFillers({});
      return;
    }

    let cancelled = false;

    async function fetchSpotFillers() {
      const excludeParam = rosterIds.join(',');
      const entries = await Promise.all(
        emptySlots.map(async ({ slot }) => {
          const response = await fetch(
            `http://127.0.0.1:8000/recommendations/spot-filler?position=${slot}&exclude=${excludeParam}&limit=3`
          );
          const result = await response.json();
          return [slot, result.players || []];
        })
      );
      if (!cancelled) setSpotFillers(Object.fromEntries(entries));
    }

    fetchSpotFillers();
    return () => { cancelled = true; };
  }, [rosterCount]);

  function openModal(player) {
    setModalPlayer(player);
  }

  function closeModal() {
    setModalPlayer(null);
  }

  if (rosterCount === 0) {
    return (
      <div className="search-page">
        <h2 className="my-team-heading">My team</h2>
        <p className="search-status">
          No players drafted yet. Search for a player and add them to your team.
        </p>
      </div>
    );
  }

  return (
    <div className="my-team-page">
      <h2 className="my-team-heading">My team</h2>

      <div className="diamond-field">
        <svg className="diamond-lines" viewBox="0 0 640 480" preserveAspectRatio="none">
          <line x1="320" y1="408" x2="0" y2="110" stroke="#97c459" strokeWidth="1.5" />
          <line x1="320" y1="408" x2="640" y2="110" stroke="#97c459" strokeWidth="1.5" />
          <polygon points="320,408 160,259 320,144 480,259" fill="none" stroke="#97c459" strokeWidth="1.5" />
        </svg>

        {FIELD_POSITIONS.map(({ slot, top, left }) => (
          <div key={slot} className="diamond-slot" style={{ top, left }}>
            <FieldCard
              slot={slot}
              player={roster[slot]}
              onClick={() => openModal(roster[slot])}
            />
          </div>
        ))}
      </div>

      <div className="bench-section">
        <span className="bench-label">Bench</span>
        {roster.bench.length === 0 ? (
          <p className="bench-empty">No bench players yet.</p>
        ) : (
          <div className="bench-grid">
            {roster.bench.map((player) => (
              <div key={player.playerId} className="bench-card" onClick={() => openModal(player)}>
                <PlayerAvatar player={player} />
                <span className="bench-card-position">{player.position}</span>
                <span className="bench-card-name">{player.name}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="recs-and-stats-row">
        <div className="recs-column">
          <div className="recommendations-section">
            <span className="bench-label">Spot fillers</span>
            {profilesLoading ? (
              <p className="leaderboard-status">Loading team data...</p>
            ) : Object.keys(spotFillers).length === 0 ? (
              <p className="bench-empty">Every position is filled.</p>
            ) : (
              Object.entries(spotFillers).map(([slot, players]) => (
                players.length > 0 && (
                  <div key={slot} className="spot-filler-row">
                    <span className="spot-filler-slot-label">{slot}</span>
                    <div className="spot-filler-players">
                      {players.map((p) => (
                        <div
                          key={p.player_id}
                          className="recommendation-chip"
                          onClick={() => navigate((p.position === 'P' ? '/pitchers/' : '/players/') + p.player_id)}
                        >
                          <img className="recommendation-chip-img" src={p.headshot_url} alt={p.name} onError={(e) => { e.target.style.visibility = 'hidden'; }} />
                          <span>{p.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              ))
            )}
          </div>

          <div className="recommendations-section">
            <span className="bench-label">
              Stat booster{boosterCategory ? ` — your team is weak in ${CATEGORY_DISPLAY_LABELS[boosterCategory]}` : ''}
            </span>
            {profilesLoading ? (
              <p className="leaderboard-status">Loading team data...</p>
            ) : boosterPlayers.length === 0 ? (
              <p className="bench-empty">No recommendations available.</p>
            ) : (
              <div className="spot-filler-players">
                {boosterPlayers.map((p) => (
                  <div
                    key={p.player_id}
                    className="recommendation-chip"
                    onClick={() => navigate((PITCHER_CATEGORY_KEYS.includes(boosterCategory) ? '/pitchers/' : '/players/') + p.player_id)}
                  >
                    <img className="recommendation-chip-img" src={p.headshot_url} alt={p.name} onError={(e) => { e.target.style.visibility = 'hidden'; }} />
                    <span>{p.name}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="team-stats-panel">
          <span className="bench-label">Team stats</span>
          {profilesLoading ? (
            <p className="leaderboard-status">Loading...</p>
          ) : (
            <>
              {teamStats.hitting.length > 0 && (
                <div className="team-stats-group">
                  <span className="team-stats-group-label">Hitting</span>
                  {teamStats.hitting.map((stat) => (
                    <div key={stat.label} className="team-stat-row">
                      <span>{stat.label}</span>
                      <span>{stat.value}</span>
                    </div>
                  ))}
                </div>
              )}
              {teamStats.pitching.length > 0 && (
                <div className="team-stats-group">
                  <span className="team-stats-group-label">Pitching</span>
                  {teamStats.pitching.map((stat) => (
                    <div key={stat.label} className="team-stat-row">
                      <span>{stat.label}</span>
                      <span>{stat.value}</span>
                    </div>
                  ))}
                </div>
              )}
              {teamStats.hitting.length === 0 && teamStats.pitching.length === 0 && (
                <p className="bench-empty">No stats yet.</p>
              )}
            </>
          )}
        </div>
      </div>

      {modalPlayer && (
        <PlayerModal
          player={modalPlayer}
          profile={profiles[modalPlayer.playerId]}
          loading={profilesLoading}
          onClose={closeModal}
          onViewFullPage={() => {
            const isPitcher = modalPlayer.position === 'P';
            navigate((isPitcher ? '/pitchers/' : '/players/') + modalPlayer.playerId);
          }}
        />
      )}
    </div>
  );
}