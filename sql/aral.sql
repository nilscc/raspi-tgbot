create table if not exists t_aral_stations
(
    id          serial primary key,

    api_key     int not null,
    name        text,

    unique (api_key)
);

create table if not exists t_aral_fuels
(
    id          serial primary key,

    api_key     text not null,
    name        text,

    unique (api_key)
);

create table if not exists t_aral_prices
(
    id          bigserial primary key,

    station_id  int not null references t_aral_stations(id),
    fuel_id     int not null references t_aral_fuels(id),

    valid_from  timestamp with time zone not null,
    price       double precision not null,

    unique (station_id, fuel_id, valid_from)
);

create or replace view v_aral_prices_most_recent_by_fuel as
    with most_recent as (
        select
            station_id,
            fuel_id,
            max(valid_from) as valid_from
        from
            t_aral_prices
        group by
            station_id,
            fuel_id
    )
    select
        p.id,
        r.station_id,
        r.fuel_id,
        r.valid_from,
        p.price
    from
        most_recent r
        join
        t_aral_prices p
        using (
            station_id,
            fuel_id,
            valid_from
        )
    order by
        station_id,
        fuel_id
;
