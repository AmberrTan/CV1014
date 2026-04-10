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
    <main className="shell section">
      <section className="hero">
        <div className="hero-panel">
          <div className="eyebrow" style={{ marginBottom: 16 }}>Welcome to Fitness Finder</div>
          <h1 style={{ marginBottom: 24, fontSize: "clamp(2.8rem, 8vw, 6rem)" }}>
            Find the right gym, without the guesswork.
          </h1>
          <p style={{ fontSize: "1.2rem", maxWidth: "65ch", marginBottom: 40 }}>
            This system helps you navigate the complex gym landscape. Whether you're a beginner
            looking for a friendly community or an advanced lifter needing specific equipment, our
            scoring engine has you covered.
          </p>
          <div className="cta-row">
            <Link className="button" href="/browse">
              Explore the database
            </Link>
          </div>
        </div>
        <div className="hero-grid">
          <div className="stat">
            <span style={{ fontSize: "0.9rem", color: "var(--muted)", textTransform: "uppercase" }}>Dataset</span>
            <strong style={{ fontSize: "2.5rem", marginTop: 4 }}>{gyms.length}</strong>
            <p style={{ margin: 0 }}>Verified gym locations in Singapore</p>
          </div>
          <div className="stat">
            <span style={{ fontSize: "0.9rem", color: "var(--muted)", textTransform: "uppercase" }}>Scoring</span>
            <strong style={{ fontSize: "2.5rem", marginTop: 4 }}>20+</strong>
            <p style={{ margin: 0 }}>Data points used per gym match</p>
          </div>
          <div className="stat">
            <span style={{ fontSize: "0.9rem", color: "var(--muted)", textTransform: "uppercase" }}>Technology</span>
            <strong style={{ fontSize: "2.5rem", marginTop: 4 }}>Python</strong>
            <p style={{ margin: 0 }}>High-performance scoring & search backend</p>
          </div>
        </div>
      </section>

      <section className="section" style={{ marginTop: 64 }}>
        <div className="panel" style={{ background: "rgba(255, 250, 242, 0.6)" }}>
          <header style={{ marginBottom: 32 }}>
            <div className="eyebrow">Local Highlights</div>
            <h2 style={{ fontSize: "2.4rem" }}>Featured gyms</h2>
            <p style={{ maxWidth: "60ch" }}>
              A selection from the shared gym dataset. Use the filters to find more tailored
              options.
            </p>
          </header>
          
          {loadError ? (
            <div className="notice" data-tone="error" style={{ marginBottom: 24, display: "flex", gap: 16, alignItems: "center" }}>
              <span style={{ fontSize: "1.5rem" }}>⚠️</span>
              <p style={{ margin: 0 }}>
                The backend is currently offline. Please ensure the Python API is running to view
                live gym data.
              </p>
            </div>
          ) : null}

          <div className="grid cards">
            {gyms.slice(0, 3).map((gym) => (
              <GymCard key={gym.gym_id} gym={gym} />
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
