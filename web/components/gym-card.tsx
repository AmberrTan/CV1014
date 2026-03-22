import type { Gym } from "../lib/types";

export function GymCard({ gym }: { gym: Gym }) {
  return (
    <article className="card">
      <div className="eyebrow">{gym.area}</div>
      <h3>{gym.gym_name}</h3>
      <div className="meta">
        <span>${gym.monthly_price.toFixed(2)}/month</span>
        <span>Rating {gym.rating.toFixed(1)}</span>
        <span>{gym.gym_type}</span>
        <span>{gym.display_hours}</span>
      </div>
      <p>{gym.address}</p>
      {gym.distance !== undefined ? <p>Distance: {gym.distance.toFixed(2)} units</p> : null}
      {gym.recommendation_score !== undefined ? (
        <p className="score">Match score: {gym.recommendation_score.toFixed(2)}</p>
      ) : null}
      {gym.recommendation_reason ? <p>{gym.recommendation_reason}</p> : null}
      <div className="pill-row">
        {gym.facilities.slice(0, 6).map((facility) => (
          <span key={facility} className="pill">
            {facility}
          </span>
        ))}
      </div>
    </article>
  );
}
