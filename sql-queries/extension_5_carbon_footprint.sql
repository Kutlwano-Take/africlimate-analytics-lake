-- Carbon Footprint and Energy Data for Southern Africa
-- Simulated energy consumption and emissions data

SELECT 
  year,
  month,
  precipitation,
  -- Energy consumption (simulated based on season and precipitation)
  ROUND(
    CASE 
      WHEN month IN (6, 7, 8) THEN 8500 + (100 - precipitation) * 20  -- Winter heating
      WHEN month IN (12, 1, 2) THEN 7500 + precipitation * 10      -- Summer cooling
      ELSE 7000 + ABS(50 - precipitation) * 15
    END, 0
  ) as energy_consumption_mwh,
  -- Carbon emissions (based on energy mix)
  ROUND(
    CASE 
      WHEN month IN (6, 7, 8) THEN (8500 + (100 - precipitation) * 20) * 0.9  -- Coal-heavy winter
      WHEN month IN (12, 1, 2) THEN (7500 + precipitation * 10) * 0.7       -- More renewables summer
      ELSE (7000 + ABS(50 - precipitation) * 15) * 0.8
    END, 0
  ) as carbon_emissions_tons,
  -- Renewable energy percentage (inversely related to energy demand)
  ROUND(
    CASE 
      WHEN month IN (12, 1, 2) THEN 35 + precipitation * 0.3  -- Summer solar
      WHEN month IN (6, 7, 8) THEN 15 - (100 - precipitation) * 0.1  -- Winter less renewable
      ELSE 25 + ABS(50 - precipitation) * 0.1
    END, 1
  ) as renewable_percentage,
  -- Energy security index
  CASE 
    WHEN energy_consumption_mwh > 9000 THEN 'High Stress'
    WHEN energy_consumption_mwh > 8000 THEN 'Moderate Stress'
    WHEN energy_consumption_mwh > 7000 THEN 'Adequate'
    ELSE 'Good'
  END as energy_security_status,
  -- Carbon intensity
  ROUND(carbon_emissions_tons / energy_consumption_mwh, 3) as carbon_intensity,
  region
FROM chirps_monthly_processed
ORDER BY year, month;
