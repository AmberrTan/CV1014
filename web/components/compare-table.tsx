import type { Gym } from "../lib/types";

const rows: Array<[string, (gym: Gym) => string]> = [
  ["Area", (gym) => gym.area],
  ["Monthly Price", (gym) => `$${gym.monthly_price.toFixed(2)}`],
  ["Day Pass", (gym) => `$${gym.day_pass_price.toFixed(2)}`],
  ["Rating", (gym) => gym.rating.toFixed(1)],
  ["Hours", (gym) => gym.display_hours],
  ["Gym Type", (gym) => gym.gym_type],
  ["Classes", (gym) => (gym.classes_available ? "Yes" : "No")],
  ["Female-friendly", (gym) => (gym.female_friendly ? "Yes" : "No")],
  ["Facilities", (gym) => gym.facilities.join(", ")],
  ["Recommendation Score", (gym) => gym.recommendation_score?.toFixed(2) || "-"],
];

export function CompareTable({ gyms }: { gyms: Gym[] }) {
  return (
    <div className="table-wrap panel">
      <table>
        <thead>
          <tr>
            <th>Field</th>
            {gyms.map((gym) => (
              <th key={gym.gym_id}>{gym.gym_name}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map(([label, formatter]) => (
            <tr key={label}>
              <td>{label}</td>
              {gyms.map((gym) => (
                <td key={`${label}-${gym.gym_id}`}>{formatter(gym)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
