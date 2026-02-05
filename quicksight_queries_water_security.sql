-- Water Security
-- AfriClimate Analytics Lake
-- Generated: 2026-02-05 13:39:45


-- Water Security Dataset
SELECT 
    dam_name,
    province,
    current_capacity_percent,
    rainfall_status,
    overall_security_score,
    risk_level,
    days_until_critical,
    recommendations,
    analysis_date
FROM africlimate_climate_db.water_security_metrics
ORDER BY analysis_date DESC
    