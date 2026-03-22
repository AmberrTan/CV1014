"use client";

import { useState, type FormEvent } from "react";

import { GymCard } from "../../components/gym-card";
import { searchGyms } from "../../lib/api";
import type { Gym } from "../../lib/types";

export default function BrowsePage() {
  const [results, setResults] = useState<Gym[]>([]);
  const [status, setStatus] = useState("Use filters to search the gym database.");
  const [statusTone, setStatusTone] = useState<"default" | "error" | "success">("default");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const requiredFacilities = String(formData.get("required_facilities") || "")
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);

    setIsSubmitting(true);
    setStatusTone("default");
    setStatus("Searching...");
    try {
      const gyms = await searchGyms({
        area: String(formData.get("area") || "") || undefined,
        max_budget: formData.get("max_budget") ? Number(formData.get("max_budget")) : undefined,
        min_rating: formData.get("min_rating") ? Number(formData.get("min_rating")) : undefined,
        required_facilities: requiredFacilities,
        gym_type: String(formData.get("gym_type") || "") || undefined,
        sort_key: String(formData.get("sort_key") || "none"),
        user_x: formData.get("user_x") ? Number(formData.get("user_x")) : undefined,
        user_y: formData.get("user_y") ? Number(formData.get("user_y")) : undefined,
      });
      setResults(gyms);
      setStatus(gyms.length ? `${gyms.length} gyms found.` : "No gyms matched those filters.");
      setStatusTone(gyms.length ? "success" : "default");
    } catch {
      setResults([]);
      setStatus("Could not reach the Python API. Start the backend and try again.");
      setStatusTone("error");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="shell section">
      <div className="panel">
        <div className="eyebrow">Browse</div>
        <h1 style={{ fontSize: "clamp(2rem, 5vw, 4rem)" }}>Search and sort gyms</h1>
        <p>Filter by area, budget, facilities, and sort order, then review the matching gyms.</p>
        <form
          onSubmit={handleSubmit}
          className="toolbar"
          style={{ marginTop: 18 }}
        >
          <div className="field">
            <label htmlFor="browse-area">Area</label>
            <input id="browse-area" name="area" placeholder="Jurong East" />
          </div>
          <div className="field">
            <label htmlFor="browse-max-budget">Max budget</label>
            <input id="browse-max-budget" name="max_budget" type="number" placeholder="120" />
          </div>
          <div className="field">
            <label htmlFor="browse-min-rating">Minimum rating</label>
            <input
              id="browse-min-rating"
              name="min_rating"
              type="number"
              min="0"
              max="5"
              step="0.1"
              placeholder="4.2"
            />
          </div>
          <div className="field">
            <label htmlFor="browse-gym-type">Gym type</label>
            <input id="browse-gym-type" name="gym_type" placeholder="commercial" />
          </div>
          <div className="field">
            <label htmlFor="browse-required-facilities">Facilities</label>
            <input
              id="browse-required-facilities"
              name="required_facilities"
              placeholder="cardio, shower"
            />
          </div>
          <div className="field">
            <label htmlFor="browse-sort-key">Sort by</label>
            <select id="browse-sort-key" name="sort_key" defaultValue="none">
              <option value="none">None</option>
              <option value="price">Lowest price</option>
              <option value="rating">Highest rating</option>
              <option value="distance">Distance</option>
              <option value="score">Match score</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="browse-user-x">User X</label>
            <input id="browse-user-x" name="user_x" type="number" placeholder="10" />
          </div>
          <div className="field">
            <label htmlFor="browse-user-y">User Y</label>
            <input id="browse-user-y" name="user_y" type="number" placeholder="30" />
          </div>
          <button className="button" type="submit" disabled={isSubmitting} aria-busy={isSubmitting}>
            {isSubmitting ? "Searching..." : "Search gyms"}
          </button>
        </form>
        <p className="notice" data-tone={statusTone} style={{ marginTop: 18 }} aria-live="polite">
          {status}
        </p>
      </div>

      <div className="grid cards" style={{ marginTop: 24 }}>
        {results.map((gym) => (
          <GymCard key={gym.gym_id} gym={gym} />
        ))}
      </div>
    </main>
  );
}
