import type { Gym } from "../lib/types";

export function GymCard({ gym }: { gym: Gym }) {
  return (
    <article className="card">
      <header style={{ marginBottom: 16 }}>
        <div className="eyebrow" style={{ marginBottom: 4 }}>{gym.area}</div>
        <h3 style={{ margin: 0, fontSize: "1.4rem" }}>{gym.gym_name}</h3>
      </header>

      <div className="meta" style={{ marginBottom: 16, display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px 12px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span>💰</span>
          <strong>${gym.monthly_price.toFixed(0)}/mo</strong>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span>⭐️</span>
          <strong>{gym.rating.toFixed(1)}</strong>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span>🏢</span>
          <span>{gym.gym_type}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span>🕒</span>
          <span>{gym.display_hours}</span>
        </div>
      </div>

      <p style={{ fontSize: "0.9rem", color: "var(--muted)", marginBottom: 16, flexGrow: 1 }}>
        📍 {gym.address}
      </p>

      {gym.distance !== undefined && (
        <div style={{ fontSize: "0.85rem", padding: "8px 12px", background: "var(--panel-strong)", borderRadius: 12, marginBottom: 12 }}>
          <strong>Distance:</strong> {gym.distance.toFixed(2)} units
        </div>
      )}

      {gym.recommendation_score !== undefined && (
        <div style={{ marginBottom: 16, padding: "12px", borderRadius: 16, background: "rgba(59, 122, 87, 0.08)", border: "1px solid rgba(59, 122, 87, 0.15)" }}>
          <div className="score" style={{ fontSize: "1.1rem", marginBottom: 4 }}>
            Match Score: {gym.recommendation_score.toFixed(0)}%
          </div>
          {gym.recommendation_reason && (
            <p style={{ margin: 0, fontSize: "0.85rem", fontStyle: "italic", color: "var(--ink)" }}>
              "{gym.recommendation_reason}"
            </p>
          )}
        </div>
      )}

      <div className="pill-row" style={{ marginTop: "auto" }}>
        {gym.facilities.slice(0, 4).map((facility) => (
          <span key={facility} className="pill" style={{ fontSize: "0.75rem", padding: "4px 10px" }}>
            {facility}
          </span>
        ))}
        {gym.facilities.length > 4 && (
          <span className="pill" style={{ fontSize: "0.75rem", padding: "4px 10px", opacity: 0.7 }}>
            +{gym.facilities.length - 4} more
          </span>
        )}
      </div>
    </article>
  );
}
