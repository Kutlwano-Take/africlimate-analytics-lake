-- Create Water Security Table
CREATE TABLE IF NOT EXISTS water_security_metrics
WITH (
  format = 'PARQUET',
  write_compression = 'SNAPPY'
) AS
SELECT 
  year,
  month,
  precipitation,
  CASE 
    WHEN precipitation < 20 THEN 'Critical Water Shortage'
    WHEN precipitation < 40 THEN 'Severe Water Stress'
    WHEN precipitation < 60 THEN 'Moderate Water Stress'
    WHEN precipitation < 80 THEN 'Adequate Supply'
    ELSE 'Water Surplus'
  END as water_security_level,
  CASE 
    WHEN precipitation < 20 THEN 4
    WHEN precipitation < 40 THEN 3
    WHEN precipitation < 60 THEN 2
    WHEN precipitation < 80 THEN 1
    ELSE 0
  END as water_stress_index,
  ROUND(
    CASE 
      WHEN month IN (12, 1, 2) THEN precipitation * 0.8 + 20
      WHEN month IN (6, 7, 8) THEN precipitation * 0.3 + 10
      ELSE precipitation * 0.5 + 15
    END, 1
  ) as dam_level_percentage,
  CASE 
    WHEN month IN (12, 1, 2) THEN 0.9
    WHEN month IN (6, 7, 8) THEN 0.4
    ELSE 0.6
  END as water_demand_index
FROM chirps_monthly_processed;
