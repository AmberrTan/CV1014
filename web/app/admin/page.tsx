import { AdminForm } from "../../components/admin-form";
import { getGyms } from "../../lib/api";

export default async function AdminPage() {
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
      <div className="panel">
        <div className="eyebrow">Admin</div>
        <h1 style={{ fontSize: "clamp(2rem, 5vw, 4rem)" }}>Create or update gym records</h1>
        <p>
          This page sends add and update requests to the Python API. The JSON database remains the
          single source of truth for both console and web demos.
        </p>
        {loadError ? (
          <p className="notice" data-tone="error" style={{ marginTop: 16 }}>
            Existing gyms could not be loaded from the backend. Create and update actions may fail
            until the API is running again.
          </p>
        ) : null}
      </div>
      <div style={{ marginTop: 24 }}>
        <AdminForm gyms={gyms} />
      </div>
    </main>
  );
}
