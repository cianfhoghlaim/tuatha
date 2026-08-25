// tuatha.web.tanstack-start.router — the canonical TanStack Start router shell.
import { createRouter as createTanstackRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";

export const router = createTanstackRouter({ routeTree });
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
