import { createContext, useContext, useState, useEffect } from "react";

const TeamContext = createContext(null);
const STORAGE_KEY = "diamondReport.myTeam";

const EMPTY_ROSTER = {
  C: null,
  "1B": null,
  "2B": null,
  "3B": null,
  SS: null,
  LF: null,
  CF: null,
  RF: null,
  DH: null,
  P: null,
  bench: [],
};

function loadRoster() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return EMPTY_ROSTER;
    const parsed = JSON.parse(raw);
    return { ...EMPTY_ROSTER, ...parsed };
  } catch (err) {
    console.error("Failed to load saved team, starting fresh", err);
    return EMPTY_ROSTER;
  }
}

export function TeamProvider({ children }) {
  const [roster, setRoster] = useState(loadRoster);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(roster));
    } catch (err) {
      console.error("Failed to save team", err);
    }
  }, [roster]);

  function addPlayer(player, slot) {
    setRoster((prev) => {
      if (slot && slot !== "bench" && !prev[slot]) {
        return { ...prev, [slot]: player };
      }
      return { ...prev, bench: [...prev.bench, player] };
    });
  }

  function removePlayer(playerId) {
    setRoster((prev) => {
      const next = { ...prev };
      for (const key of Object.keys(next)) {
        if (key === "bench") continue;
        if (next[key]?.playerId === playerId) next[key] = null;
      }
      next.bench = next.bench.filter((p) => p.playerId !== playerId);
      return next;
    });
  }

  function isOnTeam(playerId) {
    if (roster.bench.some((p) => p.playerId === playerId)) return true;
    return Object.entries(roster).some(
      ([key, val]) => key !== "bench" && val?.playerId === playerId
    );
  }

  function clearTeam() {
    setRoster(EMPTY_ROSTER);
  }

  const rosterCount =
    Object.entries(roster).filter(([k, v]) => k !== "bench" && v).length +
    roster.bench.length;

  return (
    <TeamContext.Provider
      value={{ roster, addPlayer, removePlayer, isOnTeam, clearTeam, rosterCount }}
    >
      {children}
    </TeamContext.Provider>
  );
}

export function useTeam() {
  const ctx = useContext(TeamContext);
  if (!ctx) throw new Error("useTeam must be used within a TeamProvider");
  return ctx;
}