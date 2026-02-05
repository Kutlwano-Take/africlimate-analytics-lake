-- Carbon Footprint
-- AfriClimate Analytics Lake
-- Generated: 2026-02-05 13:39:45


-- Carbon Footprint Dataset
SELECT 
    energy_type,
    carbon_intensity_trend,
    climate_resilience,
    transition_opportunities,
    carbon_risk_score,
    key_insights,
    assessment_date
FROM africlimate_climate_db.carbon_impact_assessments
ORDER BY assessment_date DESC
    