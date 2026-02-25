-- Create Carbon Footprint Table
CREATE TABLE IF NOT EXISTS carbon_footprint_metrics AS
SELECT 
  year,
  month,
  precipitation,
  ROUND(
    CASE 
      WHEN month IN (6, 7, 8) THEN 8500 + (100 - precipitation) * 20
      WHEN month IN (12, 1, 2) THEN 7500 + precipitation * 10
      ELSE 7000 + ABS(50 - precipitation) * 15
    END, 0
  ) as energy_consumption_mwh,
  ROUND(
    CASE 
      WHEN month IN (6, 7, 8) THEN (8500 + (100 - precipitation) * 20) * 0.9
      WHEN month IN (12, 1, 2) THEN (7500 + precipitation * 10) * 0.7
      ELSE (7000 + ABS(50 - precipitation) * 15) * 0.8
    END, 0
  ) as carbon_emissions_tons,
  ROUND(
    CASE 
      WHEN month IN (12, 1, 2) THEN 35 + precipitation * 0.3
      WHEN month IN (6, 7, 8) THEN 15 - (100 - precipitation) * 0.1
      ELSE 25 + ABS(50 - precipitation) * 0.1
    END, 1
  ) as renewable_percentage,
  CASE 
    WHEN energy_consumption_mwh > 9000 THEN 'High Stress'
    WHEN energy_consumption_mwh > 8000 THEN 'Moderate Stress'
    WHEN energy_consumption_mwh > 7000 THEN 'Adequate'
    ELSE 'Good'
  END as energy_security_status,
  ROUND(carbon_emissions_tons / energy_consumption_mwh, 3) as carbon_intensity,
  region
FROM chirps_monthly_processed;
