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
create table If Not exists investitgroup.market_trend_price (
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
CREATE INDEX IF NOT EXISTS idx_market_trend_price_area_id
ON investitgroup.market_trend_price (area_id);


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
create table If Not exists investitgroup.market_trends_yield (
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
CREATE INDEX IF NOT EXISTS idx_market_trends_yield_area_id
ON investitgroup.market_trends_yield (area_id);


-- Table for /markets/trends/growth-rates
create table If Not exists investitgroup.market_trends_growth_rates (
    area_id text not null,
    period_end text not null,
    property_type text not null,
    bedrooms text,
    price_chg text,
    sales_chg text,
    rent_chg text,
    rentals_chg text,
    buy_si_chg text,
    rent_si_chg text,
    yield_chg text,

    PRIMARY KEY (
        area_id,
        period_end,
        property_type
    )

);
CREATE INDEX IF NOT EXISTS idx_market_trends_growth_rates_area_id
ON investitgroup.market_trends_growth_rates (area_id);


-- Table for /markets/trends/years-to-own
create table If Not exists investitgroup.market_trends_years_to_own (
    area_id text not null,
    period_end text not null,
    property_type text not null,
    bedrooms text,
    years_to_own text,

    PRIMARY KEY (
        area_id,
        period_end,
        property_type
    )

);
CREATE INDEX IF NOT EXISTS idx_market_trends_years_to_own_area_id
ON investitgroup.market_trends_years_to_own (area_id);


-- Table for /markets/trends/demand-profile
create table If Not exists investitgroup.market_trends_demand_profile (
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
CREATE INDEX IF NOT EXISTS idx_market_trends_demand_profile_area_id
ON investitgroup.market_trends_demand_profile (area_id);


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


-- Table for /markets/supply/ls
create table If Not exists investitgroup.market_supply_ls (
    area_id text not null,
    period_end text not null,
    property_type text not null,
    ls_som_perc text,
    ls_inventory text,
    ls_hold_period text,

    PRIMARY KEY (
        area_id,
        period_end,
        property_type
    )

);
CREATE INDEX IF NOT EXISTS idx_market_supply_ls_area_id
ON investitgroup.market_supply_ls (area_id);


-- Table for /markets/supply/ss
create table If Not exists investitgroup.market_supply_ss (
    area_id text not null,
    period_end text not null,
    property_type text not null,
    ss_som_perc text,
    ss_inventory text,
    ss_hold_period text,

    PRIMARY KEY (
        area_id,
        period_end,
        property_type
    )

);
CREATE INDEX IF NOT EXISTS idx_market_supply_ss_area_id
ON investitgroup.market_supply_ss (area_id);

-- Table for /markets/scores
create table If Not exists investitgroup.market_scores (
    area_id text not null,
    period_end text not null,
    property_type text not null,
    rcs_lower_risk text,
    rcs_cashflow text,
    rcs_capital_growth text,
    rcs_overall text,
    hapi_score text,
    volatility_index text,

    PRIMARY KEY (
        area_id,
        period_end,
        property_type
    )

);
CREATE INDEX IF NOT EXISTS idx_market_scores_area_id
ON investitgroup.market_scores (area_id);


-- Table for /markets/risk
create table If Not exists investitgroup.market_risk (
    area_id text not null,
    period_end text not null,
    property_type text not null,
    hrp_flood text,
    hrp_fire text,
    ediv_ind text,
    madi text,
    gpo_dist text,

    PRIMARY KEY (
        area_id,
        period_end,
        property_type
    )

);
CREATE INDEX IF NOT EXISTS idx_market_risk_area_id
ON investitgroup.market_risk (area_id);


-- Table for /markets/fundamentals
create table If Not exists investitgroup.market_fundamentals (
    area_id text not null,
    period_end text not null,
    property_type text not null,
    irsad text,
    ro_ratio text,
    uh_ratio text,
    uhv_ratio text,
    years_to_own text,
    non_res_ba_per_capita_value text,

    PRIMARY KEY (
        area_id,
        period_end,
        property_type
    )

);
CREATE INDEX IF NOT EXISTS idx_market_fundamentals_area_id
ON investitgroup.market_fundamentals (area_id);

-- Table for /markets/cycle
create table If Not exists investitgroup.market_cycle (
    area_id text not null,
    period_end text not null,
    property_type text not null,
    growth_rate_cycle text,
    grc_price_index text,
    min_grc text,
    gpd_3 text,
    gpd_5 text,
    gpd_10 text,
    gsp_3 text,
    gsp_5 text,
    projected_annual_capital_growth_low text,
    projected_annual_capital_growth_high text,
    projected_annual_rent_increase text,
    projected_annual_roi_low text,
    projected_annual_roi_high text,

    PRIMARY KEY (
        area_id,
        period_end,
        property_type
    )

);
CREATE INDEX IF NOT EXISTS idx_market_cycle_area_id
ON investitgroup.market_cycle (area_id);


-- Table for /markets/growth/cumulative
create table If Not exists investitgroup.market_growth_cumulative (
    area_id text not null,
    period_end text not null,
    property_type text not null,
    bedrooms text,
    price_1m_growth text,
    price_1q_growth text,
    price_6m_growth text,
    price_1y_growth text,
    price_3y_growth text,
    price_5y_growth text,
    price_10y_growth text,
    rent_1m_growth text,
    rent_1q_growth text,
    rent_6m_growth text,
    rent_1y_growth text,
    rent_3y_growth text,
    rent_5y_growth text,
    rent_10y_growth text,
    yield_1m_growth text,
    yield_1q_growth text,
    yield_6m_growth text,
    yield_1y_growth text,
    yield_3y_growth text,
    yield_5y_growth text,
    yield_10y_growth text,
    PRIMARY KEY (
        area_id,
        period_end,
        property_type
    )

);
CREATE INDEX IF NOT EXISTS idx_market_growth_cumulative_area_id
ON investitgroup.market_growth_cumulative (area_id);