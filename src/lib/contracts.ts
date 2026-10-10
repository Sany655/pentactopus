import Ajv2020, { type ValidateFunction } from "ajv/dist/2020.js";
import apiSchema from "../../contracts/v1/api.schema.json";
import taskSchema from "../../contracts/v1/task-envelope.schema.json";

const ajv = new Ajv2020({ allErrors: true, strict: false });
const apiValidators = new Map<string, ValidateFunction>();

for (const [name, schema] of Object.entries(apiSchema.$defs)) {
  apiValidators.set(name, ajv.compile({ ...schema, $defs: apiSchema.$defs }));
}

export const validateTaskEnvelope = ajv.compile(taskSchema);

export function validateApiPayload(name: string, value: unknown): boolean {
  const validator = apiValidators.get(name);
  if (!validator) throw new Error(`Unknown API contract: ${name}`);
  return validator(value);
}
