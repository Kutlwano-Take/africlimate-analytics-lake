-- Drought Early Warning
-- AfriClimate Analytics Lake
-- Generated: 2026-02-05 13:39:45


-- Drought Early Warning Dataset
SELECT 
    year,
    month,
    province,
    region,
    drought_level,
    risk_level,
    monthly_precip,
    avg_spi,
    farmer_message,
    analysis_date
FROM africlimate_climate_db.drought_alerts
ORDER BY analysis_date DESC
    