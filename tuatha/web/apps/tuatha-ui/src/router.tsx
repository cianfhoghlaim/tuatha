/**
 * router — the TanStack Start route registry.
 *
 * Phase 2 ADDS:
 * - 8 realm routes (`/realm/<subject>`) — the per-subject realm
 *   pages with the 2.5D PixiJS background + Convex quest list
 * - `/student/$id/mastery` — the cross-subject mastery dashboard
 *
 * The router is intentionally additive — existing routes are
 * preserved unchanged.
 *
 * The 9 routes are defined via `createFileRoute(...)` in their
 * respective files; the registry below re-exports the `Route`
 * constants for the route-tree wiring.
 */

import { Route as MathematicsRoute } from "./routes/realm/mathematics";
import { Route as AppliedMathematicsRoute } from "./routes/realm/applied_mathematics";
import { Route as ChemistryRoute } from "./routes/realm/chemistry";
import { Route as GeographyRoute } from "./routes/realm/geography";
import { Route as HistoryRoute } from "./routes/realm/history";
import { Route as EnglishRoute } from "./routes/realm/english";
import { Route as GaeilgeRoute } from "./routes/realm/gaeilge";
import { Route as ComputerScienceRoute } from "./routes/realm/computer_science";
import { Route as StudentMasteryRoute } from "./routes/student/[id]/mastery";

/**
 * The 9 new Phase 2 routes. The consuming router file (or the
 * generated `routeTree.gen.ts` produced by the TanStack Router
 * CLI from the file-based convention) imports these and adds
 * them to the route tree.
 */
export const phase2Routes = [
  MathematicsRoute,
  AppliedMathematicsRoute,
  ChemistryRoute,
  GeographyRoute,
  HistoryRoute,
  EnglishRoute,
  GaeilgeRoute,
  ComputerScienceRoute,
  StudentMasteryRoute,
] as const;