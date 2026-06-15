-- statement to create localities table in investit group
create table If Not exists investitgroup.localities (
    loc_pid text primary key,
    locality text not null,
    postcode text,
    state_name text,
    suburb_key text,
    lga_pid_ref text
);

create table If Not exists investitgroup.market_trend_price (
    area_id text not null,
    period_end text not null,
    property_type text,
    bedrooms text,
    typical_price text,
    sales text,

    PRIMARY KEY (
        area_id,
        period_end,
    )

);
CREATE INDEX IF NOT EXISTS idx_market_trend_price_area_id
ON investitgroup.market_trend_price (area_id);