import { Pool, type PoolClient, type QueryResult, type QueryResultRow } from "@neondatabase/serverless";

declare global {
  var pentactopusPool: Pool | undefined;
}

let localPool: Pool | undefined;

function createPool(): Pool {
  const connectionString = process.env.DATABASE_URL;
  if (!connectionString) throw new Error("DATABASE_URL is required");
  return new Pool({ connectionString, max: 5, idleTimeoutMillis: 20_000 });
}

export function getPool(): Pool {
  if (localPool) return localPool;
  localPool = globalThis.pentactopusPool ?? createPool();
  if (process.env.NODE_ENV !== "production") globalThis.pentactopusPool = localPool;
  return localPool;
}

export async function query<T extends QueryResultRow = QueryResultRow>(
  text: string,
  values: unknown[] = [],
): Promise<QueryResult<T>> {
  return getPool().query<T>(text, values);
}

export async function transaction<T>(work: (client: PoolClient) => Promise<T>): Promise<T> {
  const client = await getPool().connect();
  try {
    await client.query("BEGIN");
    const result = await work(client);
    await client.query("COMMIT");
    return result;
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
}
