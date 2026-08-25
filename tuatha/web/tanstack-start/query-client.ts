// tuatha.web.tanstack-start.query-client — the React Query client (for TanStack Start).
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // The Phase 1-3 DuckDB is the source of truth (not the server).
      // Phase 4 is a thin renderer of the Phase 1-5 evidence ladder.
      staleTime: 5 * 60 * 1000,  // 5 minutes
      gcTime: 30 * 60 * 1000,    // 30 minutes
      refetchOnWindowFocus: true,
    },
  },
});
