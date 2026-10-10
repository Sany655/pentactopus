import { readdir, readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { getPool } from "../src/lib/db";

async function migrate(): Promise<void> {
  const pool = getPool();
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    await client.query("SELECT pg_advisory_xact_lock(hashtext('pentactopus:migrations'))");
    await client.query(`
      CREATE TABLE IF NOT EXISTS schema_migrations (
        name text PRIMARY KEY,
        applied_at timestamptz NOT NULL DEFAULT now()
      )
    `);
    const directory = resolve(process.cwd(), "migrations");
    const files = (await readdir(directory)).filter((file) => /^\d+_.+\.sql$/.test(file)).sort();
    for (const name of files) {
      const exists = await client.query("SELECT 1 FROM schema_migrations WHERE name = $1", [name]);
      if (exists.rowCount) continue;
      const sql = await readFile(resolve(directory, name), "utf8");
      for (const statement of sql.split(";").map((item) => item.trim()).filter(Boolean)) {
        await client.query(statement);
      }
      await client.query("INSERT INTO schema_migrations (name) VALUES ($1)", [name]);
      console.log(`Applied migration ${name}`);
    }
    await client.query("COMMIT");
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
    await pool.end();
  }
}

migrate().catch((error: unknown) => {
  console.error("Database migration failed", error);
  process.exitCode = 1;
});
