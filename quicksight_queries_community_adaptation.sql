-- Community Adaptation
-- AfriClimate Analytics Lake
-- Generated: 2026-02-05 13:39:45


-- Community Adaptation Dataset
SELECT 
    settlement_name,
    population,
    overall_risk_level,
    primary_risks,
    requires_immediate_action,
    vulnerability_factors,
    assessment_date
FROM africlimate_climate_db.community_vulnerability_assessments
ORDER BY assessment_date DESC
    