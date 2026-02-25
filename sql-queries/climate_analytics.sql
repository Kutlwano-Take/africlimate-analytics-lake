-- AfriClimate Analytics Lake - Climate Analytics SQL Queries
-- Athena queries for precipitation and drought analysis

-- ==========================================
-- 1. Monthly Precipitation Analysis
-- ==========================================
-- Query to analyze monthly precipitation trends for 2023
SELECT 
    month,
    year,
    AVG(precipitation) as avg_precipitation_mm,
    MIN(precipitation) as min_precipitation_mm,
    MAX(precipitation) as max_precipitation_mm,
    COUNT(*) as data_points,
    ROUND(AVG(precipitation), 2) as monthly_avg
FROM africlimate_climate_db.chirps_data 
WHERE year >= 2020 AND year <= 2023
GROUP BY year, month 
ORDER BY month;

-- ==========================================
-- 2. Regional Precipitation Comparison
-- ==========================================
-- Query to compare precipitation across different regions
SELECT 
    CASE 
        WHEN latitude BETWEEN -35 AND -30 THEN 'Western Cape'
        WHEN latitude BETWEEN -30 AND -25 THEN 'Northern Cape'
        WHEN latitude BETWEEN -25 AND -22 THEN 'Gauteng'
        ELSE 'Other Region'
    END as region,
    month,
    AVG(precipitation) as avg_precipitation_mm,
    COUNT(*) as data_points
FROM africlimate_climate_db.chirps_data 
WHERE year >= 2020 AND year <= 2023
GROUP BY 
    CASE 
        WHEN latitude BETWEEN -35 AND -30 THEN 'Western Cape'
        WHEN latitude BETWEEN -30 AND -25 THEN 'Northern Cape'
        WHEN latitude BETWEEN -25 AND -22 THEN 'Gauteng'
        ELSE 'Other Region'
    END,
    month
ORDER BY region, month;

-- ==========================================
-- 3. Drought Metrics Analysis
-- ==========================================
-- Query to calculate drought indicators
WITH monthly_avg AS (
    SELECT 
        year,
        month,
        AVG(precipitation) as monthly_precip
    FROM africlimate_climate_db.chirps_data 
    GROUP BY year, month
),
long_term_avg AS (
    SELECT 
        month,
        AVG(monthly_precip) as climatological_avg
    FROM monthly_avg
    GROUP BY month
)
SELECT 
    m.year,
    m.month,
    m.monthly_precip,
    l.climatological_avg,
    ROUND((m.monthly_precip - l.climatological_avg) / l.climatological_avg * 100, 2) as precipitation_anomaly_percent,
    CASE 
        WHEN m.monthly_precip < l.climatological_avg * 0.5 THEN 'Severe Drought'
        WHEN m.monthly_precip < l.climatological_avg * 0.75 THEN 'Moderate Drought'
        WHEN m.monthly_precip < l.climatological_avg * 0.9 THEN 'Mild Drought'
        ELSE 'No Drought'
    END as drought_status
FROM monthly_avg m
JOIN long_term_avg l ON m.month = l.month
WHERE m.year = 2023
ORDER BY m.month;

-- ==========================================
-- 4. Year-over-Year Comparison
-- ==========================================
-- Query to compare precipitation across multiple years
SELECT 
    month,
    SUM(CASE WHEN year = 2021 THEN precipitation ELSE 0 END) as precipitation_2021,
    SUM(CASE WHEN year = 2022 THEN precipitation ELSE 0 END) as precipitation_2022,
    SUM(CASE WHEN year = 2023 THEN precipitation ELSE 0 END) as precipitation_2023,
    ROUND(AVG(CASE WHEN year = 2021 THEN precipitation ELSE NULL END), 2) as avg_2021,
    ROUND(AVG(CASE WHEN year = 2022 THEN precipitation ELSE NULL END), 2) as avg_2022,
    ROUND(AVG(CASE WHEN year = 2023 THEN precipitation ELSE NULL END), 2) as avg_2023
FROM africlimate_climate_db.chirps_data 
WHERE year IN (2020, 2021, 2022, 2023)
GROUP BY month
ORDER BY month;

-- ==========================================
-- 5. Southern Africa Focus Analysis
-- ==========================================
-- Query focused on Southern Africa region
SELECT 
    year,
    month,
    COUNT(*) as data_points,
    AVG(precipitation) as avg_precipitation_mm,
    MIN(precipitation) as min_precipitation_mm,
    MAX(precipitation) as max_precipitation_mm,
    ROUND(STDDEV(precipitation), 2) as precipitation_std_dev,
    -- Geographic bounds
    MIN(latitude) as southernmost_lat,
    MAX(latitude) as northernmost_lat,
    MIN(longitude) as westernmost_lon,
    MAX(longitude) as easternmost_lon
FROM africlimate_climate_db.chirps_data 
WHERE latitude BETWEEN -35 AND -22 
  AND longitude BETWEEN 16 AND 33
  AND year = 2023
GROUP BY year, month
ORDER BY month;

-- ==========================================
-- 6. Seasonal Analysis
-- ==========================================
-- Query to analyze seasonal precipitation patterns
SELECT 
    CASE 
        WHEN month IN (12, 1, 2) THEN 'Summer'
        WHEN month IN (3, 4, 5) THEN 'Autumn'
        WHEN month IN (6, 7, 8) THEN 'Winter'
        WHEN month IN (9, 10, 11) THEN 'Spring'
    END as season,
    AVG(precipitation) as seasonal_avg_precipitation,
    MIN(precipitation) as seasonal_min,
    MAX(precipitation) as seasonal_max,
    COUNT(*) as data_points
FROM africlimate_climate_db.chirps_data 
WHERE year >= 2020 AND year <= 2023
GROUP BY 
    CASE 
        WHEN month IN (12, 1, 2) THEN 'Summer'
        WHEN month IN (3, 4, 5) THEN 'Autumn'
        WHEN month IN (6, 7, 8) THEN 'Winter'
        WHEN month IN (9, 10, 11) THEN 'Spring'
    END
ORDER BY 
    CASE 
        WHEN month IN (12, 1, 2) THEN 1
        WHEN month IN (3, 4, 5) THEN 2
        WHEN month IN (6, 7, 8) THEN 3
        WHEN month IN (9, 10, 11) THEN 4
    END;

-- ==========================================
-- 7. Extreme Events Detection
-- ==========================================
-- Query to detect extreme precipitation events
WITH daily_stats AS (
    SELECT 
        year,
        month,
        day,
        precipitation,
        AVG(precipitation) OVER (PARTITION BY year, month) as monthly_avg,
        STDDEV(precipitation) OVER (PARTITION BY year, month) as monthly_std
    FROM africlimate_climate_db.chirps_data 
    WHERE year >= 2020 AND year <= 2023
)
SELECT 
    year,
    month,
    day,
    precipitation,
    monthly_avg,
    ROUND(precipitation / monthly_avg, 2) as precipitation_ratio,
    CASE 
        WHEN precipitation > monthly_avg + (2 * monthly_std) THEN 'Extreme Heavy Rain'
        WHEN precipitation > monthly_avg + monthly_std THEN 'Heavy Rain'
        WHEN precipitation < monthly_avg - (2 * monthly_std) THEN 'Extreme Dry'
        WHEN precipitation < monthly_avg - monthly_std THEN 'Unusually Dry'
        ELSE 'Normal'
    END as event_type
FROM daily_stats
WHERE ABS(precipitation - monthly_avg) > monthly_std
ORDER BY year, month, day;

-- ==========================================
-- 8. Data Quality Report
-- ==========================================
-- Query to assess data quality and coverage
SELECT 
    year,
    month,
    COUNT(*) as total_records,
    COUNT(DISTINCT latitude) as unique_latitudes,
    COUNT(DISTINCT longitude) as unique_longitudes,
    MIN(precipitation) as min_precipitation,
    MAX(precipitation) as max_precipitation,
    AVG(precipitation) as avg_precipitation,
    ROUND(STDDEV(precipitation), 2) as std_precipitation,
    COUNT(CASE WHEN precipitation < 0 THEN 1 END) as negative_values,
    COUNT(CASE WHEN precipitation IS NULL THEN 1 END) as null_values
FROM africlimate_climate_db.chirps_data 
WHERE year >= 2020 AND year <= 2023
GROUP BY year, month
ORDER BY year, month;
