create table public.app_feedback (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null default auth.uid()
        references auth.users(id) on delete cascade,
    name text not null,
    message text not null,
    created_at timestamptz not null default now()
);

alter table public.app_feedback enable row level security;

grant usage on schema public to authenticated;
grant select, insert on public.app_feedback to authenticated;

create policy "Read own feedback"
on public.app_feedback for select
to authenticated
using ((select auth.uid()) = user_id);

create policy "Insert own feedback"
on public.app_feedback for insert
to authenticated
with check ((select auth.uid()) = user_id);