"use client";

import { useState, type FormEvent } from "react";

import { CompareTable } from "../../components/compare-table";
import { compareGyms } from "../../lib/api";
import type { Gym } from "../../lib/types";

export default function ComparePage() {
  const [gymIds, setGymIds] = useState("1,2");
  const [results, setResults] = useState<Gym[]>([]);
  const [status, setStatus] = useState("Choose 2 or 3 gym IDs to compare.");
  const [statusTone, setStatusTone] = useState<"default" | "error" | "success">("default");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const parsedIds = gymIds
      .split(",")
      .map((value) => Number(value.trim()))
      .filter((value) => !Number.isNaN(value));
    const uniqueIds = [...new Set(parsedIds)];

    if (uniqueIds.length < 2 || uniqueIds.length > 3) {
      setResults([]);
      setStatusTone("error");
      setStatus("Please enter 2 or 3 unique gym IDs.");
      return;
    }

    setIsSubmitting(true);
    setStatusTone("default");
    setStatus("Loading comparison...");
    try {
      const gyms = await compareGyms(uniqueIds);
      if (gyms.length < 2) {
        setResults([]);
        setStatusTone("error");
        setStatus("Comparison requires 2 or 3 valid gym IDs.");
        return;
      }
      setResults(gyms);
      setStatusTone("success");
      setStatus("Comparison ready.");
    } catch {
      setResults([]);
      setStatusTone("error");
      setStatus("Could not compare gyms. Check the backend and ID selection.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="shell section">
      <div className="panel">
        <div className="eyebrow">Compare</div>
        <h1 style={{ fontSize: "clamp(2rem, 5vw, 4rem)" }}>Shortlist gyms side by side</h1>
        <p>Enter 2 or 3 gym IDs from the database and view the key details in one table.</p>
        <form className="toolbar toolbar--baseline" onSubmit={onSubmit} style={{ marginTop: 18 }}>
          <div className="field">
            <label htmlFor="compare-gym-ids">Gym IDs</label>
            <input
              id="compare-gym-ids"
              value={gymIds}
              onChange={(event) => setGymIds(event.target.value)}
              aria-describedby="compare-help"
            />
          </div>
          <button className="button button--small" type="submit" disabled={isSubmitting} aria-busy={isSubmitting}>
            {isSubmitting ? "Comparing..." : "Compare"}
          </button>
        </form>
        <p id="compare-help">Use comma-separated IDs, for example: 1,2 or 2,5,7.</p>
        <p className="notice" data-tone={statusTone} style={{ marginTop: 18 }} aria-live="polite">
          {status}
        </p>
      </div>
      {results.length >= 2 ? (
        <div style={{ marginTop: 24 }}>
          <CompareTable gyms={results} />
        </div>
      ) : null}
    </main>
  );
}
