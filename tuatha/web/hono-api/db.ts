// tuatha.web.hono-api.db — the DuckDB connection (read-write for writes, read-only for reads).
import { Database } from "duckdb";

const DB_PATH = process.env.TUATHA_DUCKDB_PATH
  ?? "../../sources/duckdb/tuatha_official_documents.duckdb";

export const db = {
  query: async <T = unknown>(sql: string, params: any[] = []): Promise<T[]> => {
    // The connection is opened per query because the Phase 4 server is
    // intentionally stateless (matches the Phase 1/2/3 design).
    const con = new Database(DB_PATH, { access_mode: "READ_ONLY" });
    try {
      const stmt = con.prepare(sql);
      const rows = stmt.all(...params) as T[];
      return rows;
    } finally {
      con.close();
    }
  },
  insert: async <T = unknown>(sql: string, params: any[] = []): Promise<void> => {
    const con = new Database(DB_PATH);
    try {
      const stmt = con.prepare(sql);
      stmt.run(...params);
    } finally {
      con.close();
    }
  },
};
