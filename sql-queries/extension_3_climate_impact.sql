-- Climate Impact Metrics for Southern Africa
-- NDVI trends and vegetation health indicators

SELECT 
  year,
  month,
  precipitation,
  -- Simulated NDVI values based on precipitation
  ROUND(
    CASE 
      WHEN precipitation > 100 THEN 0.8 + (precipitation - 100) * 0.002
      WHEN precipitation > 50 THEN 0.5 + (precipitation - 50) * 0.006
      WHEN precipitation > 25 THEN 0.3 + (precipitation - 25) * 0.008
      ELSE 0.1 + precipitation * 0.008
    END, 3
  ) as ndvi_value,
  -- Vegetation health classification
  CASE 
    WHEN ndvi_value > 0.6 THEN 'Excellent Vegetation'
    WHEN ndvi_value > 0.4 THEN 'Good Vegetation'
    WHEN ndvi_value > 0.2 THEN 'Moderate Vegetation'
    WHEN ndvi_value > 0.1 THEN 'Poor Vegetation'
    ELSE 'Bare Soil'
  END as vegetation_health,
  -- Agricultural suitability
  CASE 
    WHEN ndvi_value > 0.5 AND precipitation > 50 THEN 'Highly Suitable'
    WHEN ndvi_value > 0.3 AND precipitation > 30 THEN 'Suitable'
    WHEN ndvi_value > 0.2 AND precipitation > 20 THEN 'Marginally Suitable'
    ELSE 'Not Suitable'
  END as agricultural_suitability,
  -- Climate risk index
  ROUND(
    CASE 
      WHEN precipitation < 20 AND ndvi_value < 0.2 THEN 4
      WHEN precipitation < 40 AND ndvi_value < 0.3 THEN 3
      WHEN precipitation < 60 AND ndvi_value < 0.4 THEN 2
      WHEN precipitation < 80 AND ndvi_value < 0.5 THEN 1
      ELSE 0
    END, 1
  ) as climate_risk_index,
  region
FROM chirps_monthly_processed
ORDER BY year, month;
