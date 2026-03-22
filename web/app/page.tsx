import Link from "next/link";

import { getGyms } from "../lib/api";
import { GymCard } from "../components/gym-card";

export default async function HomePage() {
  let gyms = [];
  let loadError = false;
  try {
    gyms = await getGyms();
  } catch {
    gyms = [];
    loadError = true;
  }

  return (
    <main className="shell">
      <section className="hero">
        <div className="hero-panel">
          <div className="eyebrow">Optional Showcase UI</div>
          <h1>Find the right gym without guesswork.</h1>
          <p>
            This frontend sits on top of the Python recommendation system. Browse gyms, filter by
            preferences, compare options, and surface stronger matches for different fitness goals.
          </p>
          <div className="cta-row">
            <Link className="button" href="/browse">
              Explore gyms
            </Link>
            <Link className="button-secondary" href="/recommend">
              Get recommendations
            </Link>
          </div>
        </div>
        <div className="hero-grid">
          <div className="stat">
            <strong>{gyms.length}</strong>
            <span>gyms in the offline database</span>
          </div>
          <div className="stat">
            <strong>5</strong>
            <span>main demo flows across browse, recommend, compare, and admin</span>
          </div>
          <div className="stat">
            <strong>Python</strong>
            <span>remains the source of truth for search, scoring, and updates</span>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="panel">
          <h2>Featured gyms</h2>
          <p>A quick sample from the shared JSON dataset used by both the console app and the API.</p>
          {loadError ? (
            <p className="notice" data-tone="error" style={{ marginTop: 16 }}>
              The backend is currently unavailable, so featured gyms could not be loaded.
            </p>
          ) : null}
          <div className="grid cards" style={{ marginTop: 20 }}>
            {gyms.slice(0, 3).map((gym) => (
              <GymCard key={gym.gym_id} gym={gym} />
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
