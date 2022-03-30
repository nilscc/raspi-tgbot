create schema if not exists tgbot_2203;
set search_path = tgbot_2203;

begin;

    \ir 'aral.sql'

commit;
