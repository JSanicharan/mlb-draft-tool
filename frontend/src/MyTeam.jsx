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

function FieldCard({ slot, player }) {
  return (
    <div className={`field-card ${!player ? 'field-card-empty' : ''}`}>
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

export default function MyTeam() {
  const { roster, rosterCount } = useTeam();

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
        <svg
          className="diamond-lines"
          viewBox="0 0 640 480"
          preserveAspectRatio="none"
        >
          <line x1="320" y1="408" x2="0" y2="110" stroke="#97c459" strokeWidth="1.5" />
          <line x1="320" y1="408" x2="640" y2="110" stroke="#97c459" strokeWidth="1.5" />

          <polygon
            points="320,408 160,259 320,144 480,259"
            fill="none"
            stroke="#97c459"
            strokeWidth="1.5"
          />
        </svg>

        {FIELD_POSITIONS.map(({ slot, top, left }) => (
          <div key={slot} className="diamond-slot" style={{ top, left }}>
            <FieldCard slot={slot} player={roster[slot]} />
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
              <div key={player.playerId} className="bench-card">
                <PlayerAvatar player={player} />
                <span className="bench-card-position">{player.position}</span>
                <span className="bench-card-name">{player.name}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}