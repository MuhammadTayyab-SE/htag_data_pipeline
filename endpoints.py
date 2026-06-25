ENDPOINTS = [
    {
        "path": "/markets/trends/price", 
        "table": "market_trend_price",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
        },
        "on_conflict": ["area_id","period_end","property_type"]
    },

    {
        "path": "/markets/trends/rent", 
        "table": "market_trends_rent",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
        },
        "on_conflict": ["area_id","period_end","property_type"]

    },

    {
        "path": "/markets/trends/yield", 
        "table": "market_trends_yield",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
        },
        "on_conflict": ["area_id","period_end","property_type"]

    },
    
    {
        "path": "/markets/trends/growth-rates", 
        "table": "market_trends_growth_rates",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
        },
        "on_conflict": ["area_id","period_end","property_type"]
    
    },

    {
        "path": "/markets/trends/years-to-own", 
        "table": "market_trends_years_to_own",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
        },
        "on_conflict": ["area_id","period_end","property_type"]
    },

    {
        "path": "/markets/trends/demand-profile", 
        "table": "market_trends_demand_profile",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
        },  
        "on_conflict": ["area_id","period_end"]

    },

    {
        "path": "/markets/demand", 
        "table": "market_demand",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
        },   
        "on_conflict": ["area_id","period_end","property_type"]
    
    },

    {
        "path": "/markets/supply", 
        "table": "market_supply",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
        },     
        "on_conflict": ["area_id","period_end","property_type"]

    },

    {
        "path": "/markets/supply/ls", 
        "table": "market_supply_ls",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
        },   
        "on_conflict": ["area_id","period_end","property_type"]
    },

    {
        "path": "/markets/supply/ss", 
        "table": "market_supply_ss",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
        },   
        "on_conflict": ["area_id","period_end","property_type"]
    },


    {
        "path": "/markets/scores", 
        "table": "market_scores",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
        },
        "on_conflict": ["area_id","period_end","property_type"]
    },

    {
        "path": "/markets/risk", 
        "table": "market_risk",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
        },
        "on_conflict": ["area_id","period_end","property_type"]
    },

    {
        "path": "/markets/fundamentals", 
        "table": "market_fundamentals",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
        },
        "on_conflict": ["area_id","period_end","property_type"]
    },


    {
        "path": "/markets/cycle", 
        "table": "market_cycle",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
        },
        "on_conflict": ["area_id","period_end","property_type"]
    },

    {
        "path": "/markets/growth/cumulative", 
        "table": "market_growth_cumulative",
        "params":{ 
            "limit": "1000",
            "offset": "0",
            "area_id":[],
            "level": "suburb"
        },
        "on_conflict": ["area_id","period_end","property_type"]
    },


# Post Requests
    # {
    #     "path": "/markets/rank", 
    #     "table": "market_rank"

    # },

]
