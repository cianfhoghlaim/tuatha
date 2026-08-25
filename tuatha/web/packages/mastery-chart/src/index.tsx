/**
 * mastery-chart — the 8-axis spider chart for the Tuatha
 * cross-subject mastery dashboard.
 *
 * Recharts owns the layout + animation; D3 owns the per-axis
 * tick rounding. One axis per NCCA subject. The chart consumes
 * a `MasterySeries` (the 8 subject scores + the per-axis label
 * pair) and renders a PolarGrid + RadarChart with the bilingual
 * subject labels.
 */

import { useMemo } from "react";
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts";

export const SUBJECT_AXES = [
  { key: "mathematics", en: "Mathematics", ga: "Matamaitic" },
  { key: "applied_mathematics", en: "Applied Maths", ga: "Matamaitic Fheidhmeach" },
  { key: "chemistry", en: "Chemistry", ga: "Ceimic" },
  { key: "geography", en: "Geography", ga: "Tíreolaíocht" },
  { key: "history", en: "History", ga: "Stair" },
  { key: "english", en: "English", ga: "Béarla" },
  { key: "gaeilge", en: "Gaeilge", ga: "Gaeilge" },
  { key: "computer_science", en: "Computer Science", ga: "Ríomheolaíocht" },
] as const;

export type MasteryAxisKey = (typeof SUBJECT_AXES)[number]["key"];

export type Language = "en" | "ga";

export interface MasteryPoint {
  readonly subject: MasteryAxisKey;
  /** Mastery score in [0, 100]. Values outside the range are clamped. */
  readonly score: number;
}

export interface MasterySeries {
  readonly studentId: string;
  readonly language: Language;
  readonly points: ReadonlyArray<MasteryPoint>;
}

export interface MasteryChartProps {
  readonly series: MasterySeries;
  readonly height?: number;
  readonly accent?: string;
  readonly grid?: string;
  readonly fontSize?: number;
}

interface ChartDatum {
  readonly axis: string;
  readonly subject: MasteryAxisKey;
  readonly score: number;
}

/**
 * Normalise the per-subject mastery points into a flat array of
 * `{axis, subject, score}` rows for Recharts. The axis label is
 * resolved through the series' language toggle.
 */
function buildChartData(series: MasterySeries): ChartDatum[] {
  return SUBJECT_AXES.map((axis) => {
    const point = series.points.find((p) => p.subject === axis.key);
    const raw = point?.score ?? 0;
    const score = Math.max(0, Math.min(100, raw));
    return {
      axis: series.language === "ga" ? axis.ga : axis.en,
      subject: axis.key,
      score,
    };
  });
}

/**
 * Render the 8-axis spider chart. Wraps Recharts in a
 * ResponsiveContainer so it fills the parent width.
 */
export function MasteryChart({
  series,
  height = 360,
  accent = "#36d6c0",
  grid = "rgba(255,255,255,0.18)",
  fontSize = 12,
}: MasteryChartProps) {
  const data = useMemo(() => buildChartData(series), [series]);

  return (
    <div
      role="img"
      aria-label={`Mastery chart for student ${series.studentId}`}
      data-student-id={series.studentId}
      data-language={series.language}
      style={{ width: "100%", height }}
    >
      <ResponsiveContainer>
        <RadarChart data={data as ChartDatum[]} cx="50%" cy="50%" outerRadius="78%">
          <PolarGrid stroke={grid} strokeDasharray="2 4" />
          <PolarAngleAxis
            dataKey="axis"
            tick={{ fill: "currentColor", fontSize, fontWeight: 500 }}
          />
          <PolarRadiusAxis
            domain={[0, 100]}
            tick={{ fill: "currentColor", fontSize: fontSize - 2 }}
            tickCount={5}
            angle={90}
          />
          <Radar
            name={series.studentId}
            dataKey="score"
            stroke={accent}
            fill={accent}
            fillOpacity={0.35}
            isAnimationActive
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

/**
 * Compute the student's top subject (the axis with the highest
 * mastery score). Used by the mastery dashboard to key the
 * FIBO emblem cache. Ties are broken by the canonical
 * `SUBJECT_AXES` ordering — earlier axes win.
 */
export function topSubject(series: MasterySeries): MasteryAxisKey {
  const scoreByAxis = new Map<MasteryAxisKey, number>();
  for (const axis of SUBJECT_AXES) {
    scoreByAxis.set(axis.key, 0);
  }
  for (const point of series.points) {
    scoreByAxis.set(point.subject, point.score);
  }
  let best: MasteryAxisKey = SUBJECT_AXES[0].key;
  let bestScore = -1;
  for (const axis of SUBJECT_AXES) {
    const score = scoreByAxis.get(axis.key) ?? 0;
    if (score > bestScore) {
      best = axis.key;
      bestScore = score;
    }
  }
  return best;
}

export default MasteryChart;