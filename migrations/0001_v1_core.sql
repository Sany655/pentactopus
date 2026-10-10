CREATE TYPE device_platform AS ENUM ('windows', 'android');
CREATE TYPE message_presentation AS ENUM ('full', 'summary');
CREATE TYPE task_status AS ENUM (
  'queued', 'claimed', 'awaiting_approval', 'running',
  'done', 'failed', 'rejected', 'expired'
);
CREATE TYPE pipeline_status AS ENUM (
  'queued', 'running', 'awaiting_approval', 'done', 'failed', 'rejected', 'expired'
);
CREATE TYPE approval_status AS ENUM ('pending', 'approved', 'rejected', 'expired', 'used');

CREATE TABLE users (
  id uuid PRIMARY KEY,
  email text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  disabled_at timestamptz,
  CHECK (email = lower(email))
);

CREATE TABLE magic_link_tokens (
  id uuid PRIMARY KEY,
  email text NOT NULL,
  token_hash bytea NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  consumed_at timestamptz,
  CHECK (octet_length(token_hash) = 32),
  CHECK (email = lower(email)),
  CHECK (expires_at > created_at)
);
CREATE INDEX magic_link_tokens_expiry_idx ON magic_link_tokens (expires_at);

CREATE TABLE web_sessions (
  id uuid PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES users(id),
  token_hash bytea NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  revoked_at timestamptz,
  last_seen_at timestamptz,
  CHECK (octet_length(token_hash) = 32),
  CHECK (expires_at > created_at)
);
CREATE INDEX web_sessions_user_idx ON web_sessions (user_id, expires_at);

CREATE TABLE devices (
  id uuid PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES users(id),
  name text NOT NULL,
  platform device_platform NOT NULL,
  public_key bytea NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  revoked_at timestamptz,
  last_seen_at timestamptz,
  UNIQUE (user_id, id),
  CHECK (name ~ '^[A-Za-z0-9][A-Za-z0-9 ._-]{0,79}$'),
  CHECK (octet_length(public_key) = 32)
);
CREATE UNIQUE INDEX devices_user_name_ci_idx ON devices (user_id, lower(name));

CREATE TABLE pairing_codes (
  id uuid PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES users(id),
  code_hash bytea NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  consumed_at timestamptz,
  CHECK (octet_length(code_hash) = 32),
  CHECK (expires_at > created_at),
  CHECK (expires_at <= created_at + interval '10 minutes')
);
CREATE INDEX pairing_codes_user_expiry_idx ON pairing_codes (user_id, expires_at);

CREATE TABLE device_nonces (
  device_id uuid NOT NULL REFERENCES devices(id),
  nonce text NOT NULL,
  request_timestamp timestamptz NOT NULL,
  expires_at timestamptz NOT NULL,
  PRIMARY KEY (device_id, nonce),
  CHECK (length(nonce) BETWEEN 16 AND 128),
  CHECK (expires_at > request_timestamp)
);
CREATE INDEX device_nonces_expiry_idx ON device_nonces (expires_at);

CREATE TABLE user_settings (
  user_id uuid PRIMARY KEY REFERENCES users(id),
  message_presentation message_presentation NOT NULL DEFAULT 'full',
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE pipelines (
  id uuid PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES users(id),
  root_task_id uuid NOT NULL,
  orchestrator_device_id uuid NOT NULL,
  turn_count integer NOT NULL DEFAULT 0 CHECK (turn_count >= 0),
  max_turns integer NOT NULL DEFAULT 20,
  status pipeline_status NOT NULL DEFAULT 'queued',
  created_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  UNIQUE (user_id, id),
  FOREIGN KEY (user_id, orchestrator_device_id) REFERENCES devices (user_id, id),
  CHECK (max_turns = 20 AND turn_count <= max_turns),
  CHECK (expires_at > created_at)
);

CREATE TABLE tasks (
  id uuid PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES users(id),
  pipeline_id uuid NOT NULL,
  root_task_id uuid NOT NULL,
  parent_task_id uuid,
  origin_device_id uuid NOT NULL,
  orchestrator_device_id uuid NOT NULL,
  target_device_id uuid NOT NULL,
  hop_path uuid[] NOT NULL,
  depth smallint NOT NULL CHECK (depth BETWEEN 0 AND 2),
  turn_count integer NOT NULL CHECK (turn_count BETWEEN 0 AND 20),
  capability text NOT NULL CHECK (capability ~ '^[a-z][a-z0-9_.-]{0,99}$'),
  body jsonb NOT NULL,
  input_refs uuid[] NOT NULL DEFAULT '{}',
  requires_confirmation boolean NOT NULL DEFAULT false,
  status task_status NOT NULL DEFAULT 'queued',
  outcome_code text CHECK (outcome_code IS NULL OR outcome_code ~ '^[a-zA-Z0-9_.-]{1,80}$'),
  expires_at timestamptz NOT NULL,
  claimed_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (user_id, id),
  FOREIGN KEY (user_id, pipeline_id) REFERENCES pipelines (user_id, id),
  FOREIGN KEY (user_id, root_task_id) REFERENCES tasks (user_id, id) DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY (user_id, parent_task_id) REFERENCES tasks (user_id, id) DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY (user_id, origin_device_id) REFERENCES devices (user_id, id),
  FOREIGN KEY (user_id, orchestrator_device_id) REFERENCES devices (user_id, id),
  FOREIGN KEY (user_id, target_device_id) REFERENCES devices (user_id, id),
  CHECK (jsonb_typeof(body) = 'object'),
  CHECK (cardinality(hop_path) BETWEEN 1 AND 3),
  CHECK (array_position(hop_path, NULL) IS NULL),
  CHECK (origin_device_id = ANY(hop_path)),
  CHECK (target_device_id = hop_path[array_upper(hop_path, 1)]),
  CHECK (depth = cardinality(hop_path) - 1),
  CHECK (expires_at > created_at)
);
ALTER TABLE pipelines ADD CONSTRAINT pipelines_root_task_owner_fk
  FOREIGN KEY (user_id, root_task_id) REFERENCES tasks (user_id, id)
  DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX tasks_poll_idx ON tasks (target_device_id, status, expires_at);
CREATE INDEX tasks_user_created_idx ON tasks (user_id, created_at);
CREATE UNIQUE INDEX one_active_task_per_device_idx ON tasks (target_device_id)
  WHERE status IN ('claimed', 'awaiting_approval', 'running');

CREATE TABLE artifacts (
  id uuid PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES users(id),
  task_id uuid NOT NULL,
  created_by_device_id uuid NOT NULL,
  intended_device_id uuid,
  redis_key text NOT NULL UNIQUE,
  ciphertext_sha256 bytea NOT NULL,
  byte_length bigint NOT NULL CHECK (byte_length BETWEEN 1 AND 1048576),
  media_type text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  deleted_at timestamptz,
  UNIQUE (user_id, id),
  FOREIGN KEY (user_id, task_id) REFERENCES tasks (user_id, id),
  FOREIGN KEY (user_id, created_by_device_id) REFERENCES devices (user_id, id),
  FOREIGN KEY (user_id, intended_device_id) REFERENCES devices (user_id, id),
  CHECK (octet_length(ciphertext_sha256) = 32),
  CHECK (expires_at > created_at)
);
CREATE INDEX artifacts_task_expiry_idx ON artifacts (task_id, expires_at);

CREATE TABLE pipeline_steps (
  user_id uuid NOT NULL REFERENCES users(id),
  pipeline_id uuid NOT NULL,
  step_index integer NOT NULL CHECK (step_index >= 0),
  task_id uuid NOT NULL UNIQUE,
  target_device_id uuid NOT NULL,
  status task_status NOT NULL,
  output_artifact_id uuid,
  PRIMARY KEY (pipeline_id, step_index),
  FOREIGN KEY (user_id, pipeline_id) REFERENCES pipelines (user_id, id),
  FOREIGN KEY (user_id, task_id) REFERENCES tasks (user_id, id),
  FOREIGN KEY (user_id, target_device_id) REFERENCES devices (user_id, id),
  FOREIGN KEY (user_id, output_artifact_id) REFERENCES artifacts (user_id, id)
);

CREATE TABLE inbox_items (
  id uuid PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES users(id),
  source_device_id uuid NOT NULL,
  target_device_id uuid NOT NULL,
  task_id uuid NOT NULL,
  redis_key text NOT NULL UNIQUE,
  ciphertext_sha256 bytea NOT NULL,
  byte_length bigint NOT NULL CHECK (byte_length BETWEEN 1 AND 1048576),
  created_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  acked_at timestamptz,
  deleted_at timestamptz,
  UNIQUE (user_id, id),
  UNIQUE (user_id, id, target_device_id),
  FOREIGN KEY (user_id, source_device_id) REFERENCES devices (user_id, id),
  FOREIGN KEY (user_id, target_device_id) REFERENCES devices (user_id, id),
  FOREIGN KEY (user_id, task_id) REFERENCES tasks (user_id, id),
  CHECK (octet_length(ciphertext_sha256) = 32),
  CHECK (expires_at > created_at),
  CHECK (expires_at <= created_at + interval '10 minutes')
);
CREATE INDEX inbox_recipient_expiry_idx ON inbox_items (target_device_id, expires_at);

CREATE TABLE approvals (
  id uuid PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES users(id),
  task_id uuid NOT NULL,
  action_hash bytea NOT NULL,
  tier smallint NOT NULL CHECK (tier IN (4, 5)),
  status approval_status NOT NULL DEFAULT 'pending',
  requested_by_device_id uuid NOT NULL,
  approved_by_device_id uuid,
  created_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  approved_at timestamptz,
  used_at timestamptz,
  UNIQUE (user_id, id),
  FOREIGN KEY (user_id, task_id) REFERENCES tasks (user_id, id),
  FOREIGN KEY (user_id, requested_by_device_id) REFERENCES devices (user_id, id),
  FOREIGN KEY (user_id, approved_by_device_id) REFERENCES devices (user_id, id),
  CHECK (octet_length(action_hash) = 32),
  CHECK (expires_at > created_at),
  CHECK (expires_at <= created_at + interval '5 minutes')
);
CREATE INDEX approvals_pending_expiry_idx ON approvals (status, expires_at);
CREATE UNIQUE INDEX approvals_one_live_action_idx ON approvals (task_id, action_hash)
  WHERE status IN ('pending', 'approved');

CREATE TABLE approval_packets (
  user_id uuid NOT NULL REFERENCES users(id),
  approval_id uuid NOT NULL,
  approver_device_id uuid NOT NULL,
  inbox_item_id uuid NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (approval_id, approver_device_id),
  FOREIGN KEY (user_id, approval_id) REFERENCES approvals (user_id, id),
  FOREIGN KEY (user_id, approver_device_id) REFERENCES devices (user_id, id),
  FOREIGN KEY (user_id, inbox_item_id, approver_device_id)
    REFERENCES inbox_items (user_id, id, target_device_id)
);
CREATE INDEX approval_packets_device_idx ON approval_packets (approver_device_id, approval_id);

CREATE TABLE audit_events (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES users(id),
  actor_device_id uuid,
  task_id uuid,
  event_type text NOT NULL,
  metadata jsonb NOT NULL DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (user_id, actor_device_id) REFERENCES devices (user_id, id),
  FOREIGN KEY (user_id, task_id) REFERENCES tasks (user_id, id),
  CHECK (jsonb_typeof(metadata) = 'object')
);
CREATE INDEX audit_events_user_created_idx ON audit_events (user_id, created_at DESC);

CREATE TABLE rate_limit_buckets (
  bucket_hash bytea PRIMARY KEY,
  window_start timestamptz NOT NULL,
  hit_count integer NOT NULL CHECK (hit_count > 0),
  expires_at timestamptz NOT NULL
);
CREATE INDEX rate_limit_buckets_expiry_idx ON rate_limit_buckets (expires_at);
