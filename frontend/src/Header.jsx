import { useState } from "react";
import { NavLink } from "react-router-dom";
import { useTeam } from "./TeamContext";
import "./Header.css";

export default function Header() {
  const { rosterCount } = useTeam();
  const [menuOpen, setMenuOpen] = useState(false);
  const hasTeam = rosterCount > 0;

  function navLinkClass({ isActive }) {
    if (isActive) return "nav-link nav-link-active";
    return "nav-link";
  }

  function teamLinkClass({ isActive }) {
    if (isActive) return "nav-link nav-link-active";
    if (hasTeam) return "nav-link";
    return "nav-link nav-link-disabled";
  }

  return (
    <header className="header">
      <div className="header-inner">
        <NavLink to="/" end className="logo">
          <span className="logo-dot" />
          <span className="logo-text">Diamond Report</span>
        </NavLink>

        <nav className="nav nav-desktop">
          <NavLink to="/" end className={navLinkClass}>
            Search
          </NavLink>
          <NavLink to="/leaderboard" className={navLinkClass}>
            Leaderboard
          </NavLink>
          <NavLink
            to="/my-team"
            className={teamLinkClass}
            onClick={(e) => { if (!hasTeam) e.preventDefault(); }}
          >
            My team{hasTeam ? ` (${rosterCount})` : ""}
          </NavLink>
        </nav>

        <button
          className="menu-toggle"
          onClick={() => setMenuOpen((v) => !v)}
          aria-label="Toggle navigation"
          aria-expanded={menuOpen}
        >
          <span className="menu-bar" />
          <span className="menu-bar" />
          <span className="menu-bar" />
        </button>
      </div>

      {menuOpen && (
        <nav className="nav nav-mobile">
          <NavLink to="/" end className={navLinkClass} onClick={() => setMenuOpen(false)}>
            Search
          </NavLink>
          <NavLink to="/leaderboard" className={navLinkClass} onClick={() => setMenuOpen(false)}>
            Leaderboard
          </NavLink>
          <NavLink
            to="/my-team"
            className={teamLinkClass}
            onClick={(e) => {
              if (!hasTeam) { e.preventDefault(); return; }
              setMenuOpen(false);
            }}
          >
            My team{hasTeam ? ` (${rosterCount})` : ""}
          </NavLink>
        </nav>
      )}
    </header>
  );
}