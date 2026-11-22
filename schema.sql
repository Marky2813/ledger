CREATE SCHEMA hnparser; 
CREATE TABLE hnparser.posts (
id  BIGINT PRIMARY KEY, 
company text NOT NULL, 
role text[] NOT NULL DEFAULT '{}',
type text[] NOT NULL DEFAULT '{}',
mode text[] NOT NULL DEFAULT '{}',
salary text[] NOT NULL DEFAULT '{}',
url text[] NOT NULL DEFAULT '{}',
unclassified text[] NOT NULL DEFAULT '{}',
ambiguous text[] NOT NULL DEFAULT '{}',
skills text[] NOT NULL DEFAULT '{}',
india_evidence text,
india_eligible text CHECK (india_eligible IN ('no', 'yes', 'unclear')) NOT NULL, 
posted_at TIMESTAMPTZ NOT NULL, 
thread_id  BIGINT NOT NULL, 
raw JSONB NOT NULL
);          