-- Track ms-v2 async job lifecycle for each analysis_run

alter table public.analysis_runs
  add column if not exists status text not null default 'created', -- created | pending | running | done | done_partial | error
  add column if not exists progress text not null default '', -- e.g. "2/6"
  add column if not exists job_id text not null default '',
  add column if not exists outputs jsonb not null default '{}'::jsonb,
  add column if not exists warnings jsonb not null default '{}'::jsonb,
  add column if not exists error text not null default '',
  add column if not exists started_at timestamptz,
  add column if not exists finished_at timestamptz;

create index if not exists idx_analysis_runs_status on public.analysis_runs(status);
create index if not exists idx_analysis_runs_job_id on public.analysis_runs(job_id);

