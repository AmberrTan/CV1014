"use client";

import { useEffect, useState, type FormEvent } from "react";

import { createGym, updateGym } from "../lib/api";
import type { Gym } from "../lib/types";

const blankGym = {
  gym_name: "",
  area: "",
  address: "",
  x_coordinate: 0,
  y_coordinate: 0,
  monthly_price: 0,
  day_pass_price: 0,
  rating: 4,
  opening_time: 600,
  closing_time: 2200,
  is_24_hours: false,
  gym_type: "commercial",
  facilities: ["cardio"],
  beginner_friendly: true,
  female_friendly: true,
  student_discount: false,
  peak_crowd_level: "medium",
  parking_available: false,
  near_mrt: false,
  trainer_available: false,
  classes_available: false,
};

type EditableGym = Omit<Gym, "gym_id" | "display_hours" | "distance" | "recommendation_score" | "recommendation_reason">;

export function AdminForm({ gyms }: { gyms: Gym[] }) {
  const [mode, setMode] = useState<"create" | "update">("create");
  const [selectedId, setSelectedId] = useState<number>(gyms[0]?.gym_id || 0);
  const [status, setStatus] = useState<string>("");
  const [statusTone, setStatusTone] = useState<"default" | "error" | "success">("default");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function gymToEditable(gym: Gym): EditableGym {
    return {
      gym_name: gym.gym_name,
      area: gym.area,
      address: gym.address,
      x_coordinate: gym.x_coordinate,
      y_coordinate: gym.y_coordinate,
      monthly_price: gym.monthly_price,
      day_pass_price: gym.day_pass_price,
      rating: gym.rating,
      opening_time: gym.opening_time,
      closing_time: gym.closing_time,
      is_24_hours: gym.is_24_hours,
      gym_type: gym.gym_type,
      facilities: gym.facilities,
      beginner_friendly: gym.beginner_friendly,
      female_friendly: gym.female_friendly,
      student_discount: gym.student_discount,
      peak_crowd_level: gym.peak_crowd_level,
      parking_available: gym.parking_available,
      near_mrt: gym.near_mrt,
      trainer_available: gym.trainer_available,
      classes_available: gym.classes_available,
    };
  }

  function createBlankGym(): EditableGym {
    return {
      ...blankGym,
      facilities: [...blankGym.facilities],
    };
  }

  const [form, setForm] = useState<EditableGym>(() => createBlankGym());

  function updateField<Key extends keyof EditableGym>(key: Key, value: EditableGym[Key]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  useEffect(() => {
    if (mode === "create") {
      setForm(createBlankGym());
      return;
    }

    const selectedGym = gyms.find((gym) => gym.gym_id === selectedId);
    if (selectedGym) {
      setForm(gymToEditable(selectedGym));
    }
  }, [gyms, mode, selectedId]);

  function selectGym(gymId: number) {
    setSelectedId(gymId);
    const gym = gyms.find((item) => item.gym_id === gymId);
    if (gym) {
      setForm(gymToEditable(gym));
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setStatusTone("default");
    setStatus("Saving...");
    try {
      if (mode === "create") {
        await createGym(form);
        setForm(createBlankGym());
      } else {
        await updateGym(selectedId, form);
      }
      setStatus("Saved successfully. Refresh the page to see the latest data.");
      setStatusTone("success");
    } catch {
      setStatus("Could not save. Check that the FastAPI server is running.");
      setStatusTone("error");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="panel">
      <div className="cta-row">
        <button className="button-secondary" type="button" onClick={() => setMode("create")}>
          Create New
        </button>
        <button className="button-secondary" type="button" onClick={() => setMode("update")}>
          Update Existing
        </button>
      </div>
      {mode === "update" ? (
        <div className="field" style={{ marginTop: 16 }}>
          <label htmlFor="gym-select">Gym to update</label>
          <select
            id="gym-select"
            value={selectedId}
            onChange={(event) => selectGym(Number(event.target.value))}
          >
            {gyms.map((gym) => (
              <option key={gym.gym_id} value={gym.gym_id}>
                {gym.gym_name}
              </option>
            ))}
          </select>
        </div>
      ) : null}
      <form className="toolbar" style={{ marginTop: 16 }} onSubmit={onSubmit}>
        <div className="field">
          <label htmlFor="admin-gym-name">Gym Name</label>
          <input
            id="admin-gym-name"
            value={form.gym_name}
            onChange={(event) => updateField("gym_name", event.target.value)}
          />
        </div>
        <div className="field">
          <label htmlFor="admin-area">Area</label>
          <input id="admin-area" value={form.area} onChange={(event) => updateField("area", event.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="admin-address">Address</label>
          <input
            id="admin-address"
            value={form.address}
            onChange={(event) => updateField("address", event.target.value)}
          />
        </div>
        <div className="field">
          <label htmlFor="admin-monthly-price">Monthly Price</label>
          <input
            id="admin-monthly-price"
            type="number"
            value={form.monthly_price}
            onChange={(event) => updateField("monthly_price", Number(event.target.value))}
          />
        </div>
        <div className="field">
          <label htmlFor="admin-rating">Rating</label>
          <input
            id="admin-rating"
            type="number"
            min="0"
            max="5"
            step="0.1"
            value={form.rating}
            onChange={(event) => updateField("rating", Number(event.target.value))}
          />
        </div>
        <div className="field">
          <label htmlFor="admin-gym-type">Gym Type</label>
          <input
            id="admin-gym-type"
            value={form.gym_type}
            onChange={(event) => updateField("gym_type", event.target.value)}
          />
        </div>
        <div className="field" style={{ gridColumn: "1 / -1" }}>
          <label htmlFor="admin-facilities">Facilities</label>
          <textarea
            id="admin-facilities"
            rows={3}
            value={form.facilities.join(", ")}
            onChange={(event) =>
              updateField(
                "facilities",
                event.target.value
                  .split(",")
                  .map((value) => value.trim())
                  .filter(Boolean),
              )
            }
          />
        </div>
        <button className="button" type="submit" disabled={isSubmitting} aria-busy={isSubmitting}>
          {isSubmitting ? "Saving..." : mode === "create" ? "Create gym" : "Update gym"}
        </button>
      </form>
      {status ? (
        <p className="notice" data-tone={statusTone} style={{ marginTop: 16 }} aria-live="polite">
          {status}
        </p>
      ) : null}
    </div>
  );
}
