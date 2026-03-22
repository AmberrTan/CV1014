"use client";

import { useState, type FormEvent } from "react";

import { GymCard } from "../../components/gym-card";
import { recommendGyms } from "../../lib/api";
import type { Gym } from "../../lib/types";

export default function RecommendPage() {
  const [results, setResults] = useState<Gym[]>([]);
  const [status, setStatus] = useState("Fill in your preferences to see the top matches.");
  const [statusTone, setStatusTone] = useState<"default" | "error" | "success">("default");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const preferredFacilities = String(formData.get("preferred_facilities") || "")
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);

    setIsSubmitting(true);
    setStatusTone("default");
    setStatus("Calculating recommendations...");
    try {
      const gyms = await recommendGyms({
        preferred_area: String(formData.get("preferred_area") || "") || undefined,
        max_budget: formData.get("max_budget") ? Number(formData.get("max_budget")) : undefined,
        min_rating: formData.get("min_rating") ? Number(formData.get("min_rating")) : undefined,
        preferred_facilities: preferredFacilities,
        preferred_time: formData.get("preferred_time")
          ? Number(formData.get("preferred_time"))
          : undefined,
        fitness_goal: String(formData.get("fitness_goal") || "") || undefined,
        skill_level: String(formData.get("skill_level") || "") || undefined,
        preferred_gym_type: String(formData.get("preferred_gym_type") || "") || undefined,
        female_friendly: formData.get("female_friendly") === "on" ? true : undefined,
        classes_required: formData.get("classes_required") === "on" ? true : undefined,
        user_x: formData.get("user_x") ? Number(formData.get("user_x")) : undefined,
        user_y: formData.get("user_y") ? Number(formData.get("user_y")) : undefined,
      });
      setResults(gyms);
      setStatus(gyms.length ? "Top recommendation results ready." : "No gyms matched those requirements.");
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
        <div className="eyebrow">Recommend</div>
        <h1 style={{ fontSize: "clamp(2rem, 5vw, 4rem)" }}>Personalized gym matching</h1>
        <p>Send your preferences to the Python scoring engine and review the top-ranked results.</p>
        <form
          onSubmit={handleSubmit}
          className="toolbar"
          style={{ marginTop: 18 }}
        >
          <div className="field">
            <label htmlFor="recommend-area">Preferred area</label>
            <input id="recommend-area" name="preferred_area" placeholder="Raffles Place" />
          </div>
          <div className="field">
            <label htmlFor="recommend-max-budget">Max budget</label>
            <input id="recommend-max-budget" name="max_budget" type="number" placeholder="200" />
          </div>
          <div className="field">
            <label htmlFor="recommend-min-rating">Minimum rating</label>
            <input
              id="recommend-min-rating"
              name="min_rating"
              type="number"
              min="0"
              max="5"
              step="0.1"
              placeholder="4.2"
            />
          </div>
          <div className="field">
            <label htmlFor="recommend-preferred-facilities">Preferred facilities</label>
            <input
              id="recommend-preferred-facilities"
              name="preferred_facilities"
              placeholder="group classes, shower"
            />
          </div>
          <div className="field">
            <label htmlFor="recommend-preferred-time">Preferred time</label>
            <input id="recommend-preferred-time" name="preferred_time" type="number" placeholder="1900" />
          </div>
          <div className="field">
            <label htmlFor="recommend-fitness-goal">Fitness goal</label>
            <input id="recommend-fitness-goal" name="fitness_goal" placeholder="general fitness" />
          </div>
          <div className="field">
            <label htmlFor="recommend-skill-level">Skill level</label>
            <select id="recommend-skill-level" name="skill_level" defaultValue="beginner">
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="recommend-gym-type">Preferred gym type</label>
            <input id="recommend-gym-type" name="preferred_gym_type" placeholder="commercial" />
          </div>
          <div className="field">
            <label htmlFor="recommend-user-x">User X</label>
            <input id="recommend-user-x" name="user_x" type="number" placeholder="60" />
          </div>
          <div className="field">
            <label htmlFor="recommend-user-y">User Y</label>
            <input id="recommend-user-y" name="user_y" type="number" placeholder="70" />
          </div>
          <div className="field">
            <label htmlFor="recommend-female-friendly">Female-friendly</label>
            <input id="recommend-female-friendly" name="female_friendly" type="checkbox" />
          </div>
          <div className="field">
            <label htmlFor="recommend-classes-required">Classes required</label>
            <input id="recommend-classes-required" name="classes_required" type="checkbox" />
          </div>
          <button className="button" type="submit" disabled={isSubmitting} aria-busy={isSubmitting}>
            {isSubmitting ? "Calculating..." : "Recommend gyms"}
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
