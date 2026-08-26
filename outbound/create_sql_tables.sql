-- statement to create localities table in investit group
create table If Not exists investitgroup.localities (
    loc_pid text primary key,
    locality text not null,
    postcode text,
    state_name text,
    suburb_key text,
    lga_pid_ref text
);


-- Table for /markets/trends/price
create table If Not exists investitgroup.market_price_trends (
    area_id text not null,
    period_end text not null,
    property_type text not null,
    bedrooms text,
    typical_price text,
    sales text,

    PRIMARY KEY (
        area_id,
        period_end,
        property_type
    )
);
CREATE INDEX IF NOT EXISTS idx_market_price_trends_area_id
ON investitgroup.market_price_trends (area_id);


-- Table for /markets/trends/rent
create table If Not exists investitgroup.market_trends_rent (
    area_id text not null,
    period_end text not null,
    property_type text not null,
    bedrooms text,
    median_rent text,
    rentals text,

    PRIMARY KEY (
        area_id,
        period_end,
        property_type
    )

);
CREATE INDEX IF NOT EXISTS idx_market_trends_rent_area_id
ON investitgroup.market_trends_rent (area_id);


-- Table for /markets/trends/yield
create table If Not exists investitgroup.market_yield_trends (
    area_id text not null,
    period_end text not null,
    property_type text not null,
    bedrooms text,
    yield text,

    PRIMARY KEY (
        area_id,
        period_end,
        property_type
    )

);
CREATE INDEX IF NOT EXISTS idx_market_yield_trends_area_id
ON investitgroup.market_yield_trends (area_id);

-- Table for /markets/trends/demand-profile
create table If Not exists investitgroup.market_demand_profiles (
    area_id text not null,
    period_end text not null,
    dwelling_type text,
    bedrooms text,
    sales text,

    PRIMARY KEY (
        area_id,
        period_end
    )
);
CREATE INDEX IF NOT EXISTS idx_market_demand_profiles_area_id
ON investitgroup.market_demand_profiles (area_id);

-- Table for /markets/demand
create table If Not exists investitgroup.market_demand (
    area_id text not null,
    period_end text not null,
    property_type text not null,
    dom text,
    discounting text,
    vacancy_rate text,
    vacancies text,
    dorm text,
    clearance_rate text,
    auctions text,
    buy_si text,
    rent_si text,

    PRIMARY KEY (
        area_id,
        period_end,
        property_type
    )

);
CREATE INDEX IF NOT EXISTS idx_market_demand_area_id
ON investitgroup.market_demand (area_id);


-- Table for /markets/supply
create table If Not exists investitgroup.market_supply (
    area_id text not null,
    period_end text not null,
    property_type text not null,
    som_percent text,
    inventory text,
    building_approvals_estimated text,
    ba_ratio text,
    hold_period text,

    PRIMARY KEY (
        area_id,
        period_end,
        property_type
    )

);
CREATE INDEX IF NOT EXISTS idx_market_supply_area_id
ON investitgroup.market_supply (area_id);


-- Table for /markets/trends/days-on-market
create table If Not exists investitgroup.market_days_on_market_trends (
    area_id text not null,
    period_end text not null,
    property_type text not null,
    dom text,
    discounting text,

    PRIMARY KEY (
        area_id,
        period_end,
        property_type
    )

);
CREATE INDEX IF NOT EXISTS idx_market_days_on_market_trends_area_id
ON investitgroup.market_days_on_market_trends (area_id);