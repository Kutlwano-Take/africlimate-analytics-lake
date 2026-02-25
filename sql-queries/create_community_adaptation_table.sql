-- Create Community Adaptation Table
CREATE TABLE IF NOT EXISTS community_adaptation_metrics AS
SELECT 
  year,
  month,
  precipitation,
  CASE 
    WHEN precipitation < 20 THEN 'Extreme Vulnerability'
    WHEN precipitation < 40 THEN 'High Vulnerability'
    WHEN precipitation < 60 THEN 'Moderate Vulnerability'
    WHEN precipitation < 80 THEN 'Low Vulnerability'
    ELSE 'Minimal Vulnerability'
  END as vulnerability_level,
  ROUND(
    CASE 
      WHEN precipitation < 20 THEN 2.1
      WHEN precipitation < 40 THEN 3.2
      WHEN precipitation < 60 THEN 4.5
      WHEN precipitation < 80 THEN 6.8
      ELSE 8.2
    END, 1
  ) as adaptation_capacity_score,
  CASE 
    WHEN precipitation < 25 AND month IN (6, 7, 8) THEN 'Critical Food Insecurity'
    WHEN precipitation < 40 AND month IN (5, 6, 7, 8, 9) THEN 'High Food Insecurity'
    WHEN precipitation < 60 THEN 'Moderate Food Insecurity'
    WHEN precipitation < 80 THEN 'Low Food Insecurity'
    ELSE 'Food Secure'
  END as food_security_status,
  CASE 
    WHEN precipitation < 30 THEN 85
    WHEN precipitation < 50 THEN 65
    WHEN precipitation < 70 THEN 40
    WHEN precipitation < 90 THEN 20
    ELSE 10
  END as water_access_challenges_percentage,
  ROUND(
    (adaptation_capacity_score * 0.4 + 
     (100 - water_access_challenges_percentage) * 0.3 + 
     CASE 
       WHEN food_security_status = 'Food Secure' THEN 100
       WHEN food_security_status = 'Low Food Insecurity' THEN 75
       WHEN food_security_status = 'Moderate Food Insecurity' THEN 50
       WHEN food_security_status = 'High Food Insecurity' THEN 25
       ELSE 10
     END * 0.3), 1
  ) as adaptation_readiness_index,
  region
FROM africlimate_climate_db.chirps_data
WHERE year >= 2020 AND year <= 2023;
