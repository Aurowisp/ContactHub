-- ContactHub connects directly from FastAPI through Psycopg and does not use
-- Supabase REST/GraphQL. Run this after the application has created its tables.
-- Prefer also disabling the Data API in Supabase Dashboard if it is not needed.

begin;

alter table public.contacts enable row level security;
alter table public.contact_methods enable row level security;

revoke all on table public.contacts from anon, authenticated;
revoke all on table public.contact_methods from anon, authenticated;
revoke all on sequence public.contacts_id_seq from anon, authenticated;
revoke all on sequence public.contact_methods_id_seq from anon, authenticated;

commit;
