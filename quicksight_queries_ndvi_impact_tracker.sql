-- Ndvi Impact Tracker
-- AfriClimate Analytics Lake
-- Generated: 2026-02-05 13:39:45


-- NDVI Impact Tracker Dataset
SELECT 
    area_name,
    ecosystem,
    overall_metrics,
    risk_level,
    biodiversity_impact,
    key_threats,
    recommendations,
    assessment_date
FROM africlimate_climate_db.biodiversity_risk_assessments
ORDER BY assessment_date DESC
    