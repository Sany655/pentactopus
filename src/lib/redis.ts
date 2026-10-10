import { Redis } from "@upstash/redis";

let redisClient: Redis | undefined;

export function redis(): Redis {
  if (!redisClient) {
    const url = process.env.UPSTASH_REDIS_REST_URL;
    const token = process.env.UPSTASH_REDIS_REST_TOKEN;
    if (!url || !token) throw new Error("Upstash Redis configuration is required");
    redisClient = new Redis({ url, token, automaticDeserialization: false });
  }
  return redisClient;
}

export const MAX_CIPHERTEXT_BYTES = 1024 * 1024;
export const MAX_INBOX_TTL_MS = 10 * 60 * 1000;
