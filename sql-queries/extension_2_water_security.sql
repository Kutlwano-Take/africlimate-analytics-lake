-- AfriClimate Extension 2: Urban Water Security Dashboard SQL Queries
-- These queries support the water security analysis and Metabase dashboard

-- Query 1: Dam Level Overview with Rainfall Correlation
WITH dam_rainfall_correlation AS (
    SELECT 
        dam_name,
        province,
        dam_level_percent,
        rainfall_30d_mm,
        correlation_score,
        risk_level,
        major_cities,
        analysis_date,
        CASE 
            WHEN dam_level_percent < 40 THEN 'Critical'
            WHEN dam_level_percent < 60 THEN 'Warning'
            WHEN dam_level_percent < 80 THEN 'Caution'
            ELSE 'Normal'
        END as dam_status,
        CASE 
            WHEN rainfall_30d_mm < 20 THEN 'Severe Drought'
            WHEN rainfall_30d_mm < 40 THEN 'Moderate Drought'
            WHEN rainfall_30d_mm < 60 THEN 'Below Normal'
            ELSE 'Normal'
        END as rainfall_status
    FROM africlimate_climate_db.chirps_data
    WHERE year >= 2020
      AND year <= 2023
)
SELECT 
    dam_name,
    province,
    dam_level_percent,
    rainfall_30d_mm,
    correlation_score,
    risk_level,
    dam_status,
    rainfall_status,
    major_cities,
    analysis_date
FROM dam_rainfall_correlation
ORDER BY dam_level_percent ASC;

-- Query 2: Provincial Water Security Summary
SELECT 
    province,
    COUNT(*) as total_dams,
    ROUND(AVG(dam_level_percent), 1) as avg_dam_level_percent,
    ROUND(AVG(rainfall_30d_mm), 1) as avg_rainfall_30d_mm,
    COUNT(CASE WHEN risk_level = 'Critical' THEN 1 END) as critical_dams,
    COUNT(CASE WHEN risk_level = 'High' THEN 1 END) as high_risk_dams,
    COUNT(CASE WHEN risk_level = 'Medium' THEN 1 END) as medium_risk_dams,
    COUNT(CASE WHEN risk_level = 'Low' THEN 1 END) as low_risk_dams,
    ROUND(AVG(correlation_score), 3) as avg_correlation_score,
    MAX(analysis_date) as latest_analysis
FROM africlimate_climate_db.chirps_data
WHERE year >= 2020
  AND year <= 2023
GROUP BY province
ORDER BY avg_dam_level_percent ASC;

-- Query 3: Dam Level Trends (Last 30 Days)
WITH dam_level_trends AS (
    SELECT 
        dam_name,
        province,
        dam_level_percent,
        rainfall_30d_mm,
        analysis_date,
        LAG(dam_level_percent) OVER (PARTITION BY dam_name ORDER BY analysis_date) as previous_level,
        LAG(rainfall_30d_mm) OVER (PARTITION BY dam_name ORDER BY analysis_date) as previous_rainfall
    FROM africlimate_climate_db.chirps_data
    WHERE year >= 2020
      AND year <= 2023
)
SELECT 
    dam_name,
    province,
    dam_level_percent,
    previous_level,
    ROUND(dam_level_percent - COALESCE(previous_level, dam_level_percent), 1) as level_change_7d,
    rainfall_30d_mm,
    previous_rainfall,
    ROUND(rainfall_30d_mm - COALESCE(previous_rainfall, rainfall_30d_mm), 1) as rainfall_change_7d,
    analysis_date
FROM dam_level_trends
ORDER BY dam_name, analysis_date DESC;

-- Query 4: Major Cities Water Security Impact
SELECT 
    city,
    COUNT(DISTINCT dam_name) as supplying_dams,
    ROUND(AVG(dam_level_percent), 1) as avg_supply_level,
    MIN(dam_level_percent) as min_supply_level,
    ROUND(AVG(rainfall_30d_mm), 1) as avg_rainfall,
    COUNT(CASE WHEN risk_level IN ('Critical', 'High') THEN 1 END) as at_risk_dams,
    MAX(analysis_date) as latest_analysis
FROM (
    SELECT 
        dam_name,
        province,
        dam_level_percent,
        rainfall_30d_mm,
        risk_level,
        major_cities,
        analysis_date
    FROM africlimate_climate_db.chirps_data
    WHERE year >= 2020
      AND year <= 2023
) dam_data,
UNNEST(major_cities) as t(city)
GROUP BY city
ORDER BY avg_supply_level ASC;

-- Query 5: Water Security Alert Dashboard
SELECT 
    analysis_date,
    COUNT(*) as total_dams_monitored,
    COUNT(CASE WHEN dam_level_percent < 40 THEN 1 END) as critical_dams,
    COUNT(CASE WHEN dam_level_percent >= 40 AND dam_level_percent < 60 THEN 1 END) as warning_dams,
    COUNT(CASE WHEN dam_level_percent >= 60 AND dam_level_percent < 80 THEN 1 END) as caution_dams,
    COUNT(CASE WHEN dam_level_percent >= 80 THEN 1 END) as normal_dams,
    ROUND(AVG(dam_level_percent), 1) as national_avg_level,
    ROUND(AVG(rainfall_30d_mm), 1) as national_avg_rainfall,
    COUNT(CASE WHEN rainfall_30d_mm < 20 THEN 1 END) as severe_drought_areas,
    COUNT(CASE WHEN rainfall_30d_mm >= 20 AND rainfall_30d_mm < 40 THEN 1 END) as moderate_drought_areas,
    COUNT(CASE WHEN risk_level = 'Critical' THEN 1 END) as critical_risk_situations,
    COUNT(CASE WHEN risk_level = 'High' THEN 1 END) as high_risk_situations
FROM africlimate_climate_db.chirps_data
WHERE year >= 2020
  AND year <= 2023
GROUP BY analysis_date
ORDER BY analysis_date DESC;

-- Query 6: Rainfall vs Dam Level Correlation Analysis
WITH correlation_buckets AS (
    SELECT 
        CASE 
            WHEN rainfall_30d_mm < 20 THEN 'Very Low (<20mm)'
            WHEN rainfall_30d_mm >= 20 AND rainfall_30d_mm < 40 THEN 'Low (20-40mm)'
            WHEN rainfall_30d_mm >= 40 AND rainfall_30d_mm < 60 THEN 'Moderate (40-60mm)'
            WHEN rainfall_30d_mm >= 60 AND rainfall_30d_mm < 80 THEN 'High (60-80mm)'
            ELSE 'Very High (>80mm)'
        END as rainfall_category,
        dam_level_percent,
        dam_name,
        province
    FROM africlimate_climate_db.chirps_data
    WHERE year >= 2020
      AND year <= 2023
)
SELECT 
    rainfall_category,
    COUNT(*) as dam_count,
    ROUND(AVG(dam_level_percent), 1) as avg_dam_level,
    MIN(dam_level_percent) as min_dam_level,
    MAX(dam_level_percent) as max_dam_level,
    ROUND(STDDEV(dam_level_percent), 1) as level_std_dev,
    STRING_AGG(DISTINCT province, ', ') as provinces_represented
FROM correlation_buckets
GROUP BY rainfall_category
ORDER BY avg_dam_level DESC;
