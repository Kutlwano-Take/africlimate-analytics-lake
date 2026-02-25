-- AfriClimate Extension 1: Drought Early Warning System SQL Queries
-- These queries support the drought analyzer and Metabase dashboard

-- Query 1: 30-Day Precipitation Analysis by Province
WITH monthly_precip AS (
    SELECT 
        date,
        precipitation,
        latitude,
        longitude,
        -- Approximate province mapping based on coordinates
        CASE 
            WHEN latitude BETWEEN -30 AND -26 AND longitude BETWEEN 24 AND 29 THEN 'free_state'
            WHEN latitude BETWEEN -26 AND -24 AND longitude BETWEEN 29 AND 32 THEN 'mpumalanga'
            WHEN latitude BETWEEN -27 AND -25 AND longitude BETWEEN 22 AND 27 THEN 'north_west'
            WHEN latitude BETWEEN -27 AND -25 AND longitude BETWEEN 27 AND 29 THEN 'gauteng'
            WHEN latitude BETWEEN -24 AND -22 AND longitude BETWEEN 28 AND 32 THEN 'limpopo'
            WHEN latitude BETWEEN -32 AND -28 AND longitude BETWEEN 18 AND 24 THEN 'northern_cape'
            WHEN latitude BETWEEN -34 AND -31 AND longitude BETWEEN 18 AND 23 THEN 'western_cape'
            WHEN latitude BETWEEN -31 AND -28 AND longitude BETWEEN 23 AND 30 THEN 'eastern_cape'
            WHEN latitude BETWEEN -30 AND -27 AND longitude BETWEEN 29 AND 33 THEN 'kwazulu_natal'
            ELSE 'other'
        END as province
    FROM africlimate_climate_db.chirps_data
    WHERE year >= 2020
      AND year <= 2023
      AND precipitation IS NOT NULL
)
SELECT 
    province,
    CASE province
        WHEN 'free_state' THEN 'Free State'
        WHEN 'mpumalanga' THEN 'Mpumalanga'
        WHEN 'north_west' THEN 'North West'
        WHEN 'gauteng' THEN 'Gauteng'
        WHEN 'limpopo' THEN 'Limpopo'
        WHEN 'northern_cape' THEN 'Northern Cape'
        WHEN 'western_cape' THEN 'Western Cape'
        WHEN 'eastern_cape' THEN 'Eastern Cape'
        WHEN 'kwazulu_natal' THEN 'KwaZulu-Natal'
        ELSE 'Other'
    END as province_name,
    SUM(precipitation) as total_precipitation_30d,
    AVG(precipitation) as avg_daily_precipitation,
    COUNT(*) as data_points,
    SUM(precipitation) < 50 as is_drought_condition,
    SUM(precipitation) < 25 as is_severe_drought,
    ROUND((1 - SUM(precipitation) / 50) * 100, 1) as deficit_percentage
FROM monthly_precip
WHERE province != 'other'
GROUP BY province
ORDER BY total_precipitation_30d ASC;

-- Query 2: Historical Drought Trends (Last 12 Months)
WITH monthly_province_precip AS (
    SELECT 
        date,
        precipitation,
        CASE 
            WHEN latitude BETWEEN -30 AND -26 AND longitude BETWEEN 24 AND 29 THEN 'Free State'
            WHEN latitude BETWEEN -26 AND -24 AND longitude BETWEEN 29 AND 32 THEN 'Mpumalanga'
            WHEN latitude BETWEEN -27 AND -25 AND longitude BETWEEN 22 AND 27 THEN 'North West'
            WHEN latitude BETWEEN -27 AND -25 AND longitude BETWEEN 27 AND 29 THEN 'Gauteng'
            WHEN latitude BETWEEN -24 AND -22 AND longitude BETWEEN 28 AND 32 THEN 'Limpopo'
            WHEN latitude BETWEEN -32 AND -28 AND longitude BETWEEN 18 AND 24 THEN 'Northern Cape'
            WHEN latitude BETWEEN -34 AND -31 AND longitude BETWEEN 18 AND 23 THEN 'Western Cape'
            WHEN latitude BETWEEN -31 AND -28 AND longitude BETWEEN 23 AND 30 THEN 'Eastern Cape'
            WHEN latitude BETWEEN -30 AND -27 AND longitude BETWEEN 29 AND 33 THEN 'KwaZulu-Natal'
            ELSE 'Other'
        END as province
    FROM africlimate_climate_db.chirps_data
    WHERE year >= 2020
      AND year <= 2023
      AND precipitation IS NOT NULL
)
SELECT 
    province,
    date_trunc('month', date) as month,
    SUM(precipitation) as monthly_precipitation,
    LAG(SUM(precipitation)) OVER (PARTITION BY province ORDER BY date_trunc('month', date)) as previous_month_precip,
    ROUND(SUM(precipitation) - LAG(SUM(precipitation)) OVER (PARTITION BY province ORDER BY date_trunc('month', date)), 1) as month_over_month_change,
    CASE 
        WHEN SUM(precipitation) < 25 THEN 'Severe Drought'
        WHEN SUM(precipitation) < 50 THEN 'Moderate Drought'
        WHEN SUM(precipitation) < 75 THEN 'Below Normal'
        ELSE 'Normal'
    END as drought_status
FROM monthly_province_precip
WHERE province != 'Other'
GROUP BY province, date_trunc('month', date)
ORDER BY province, month;

-- Query 3: Drought Hotspot Analysis (Lowest Precipitation Regions)
WITH region_precip AS (
    SELECT 
        latitude,
        longitude,
        precipitation,
        -- Create region grid (approximately 50km x 50km)
        FLOOR(latitude * 20) as lat_grid,
        FLOOR(longitude * 20) as lon_grid,
        date
    FROM africlimate_climate_db.chirps_data
    WHERE year >= 2020
      AND year <= 2023
      AND precipitation IS NOT NULL
      AND latitude BETWEEN -35 AND -22  -- South Africa bounds
      AND longitude BETWEEN 16 AND 33
)
SELECT 
    lat_grid / 20.0 as region_center_lat,
    lon_grid / 20.0 as region_center_lon,
    AVG(precipitation) as avg_precipitation_30d,
    COUNT(*) as data_points,
    CASE 
        WHEN AVG(precipitation) < 15 THEN 'Critical'
        WHEN AVG(precipitation) < 25 THEN 'Severe'
        WHEN AVG(precipitation) < 40 THEN 'Moderate'
        WHEN AVG(precipitation) < 60 THEN 'Low Risk'
        ELSE 'No Risk'
    END as risk_level
FROM region_precip
GROUP BY lat_grid, lon_grid
HAVING COUNT(*) >= 10  -- Ensure sufficient data points
ORDER BY avg_precipitation_30d ASC
LIMIT 20;

-- Query 4: Seasonal Drought Comparison
WITH seasonal_precip AS (
    SELECT 
        precipitation,
        date,
        CASE 
            WHEN EXTRACT(MONTH FROM date) IN (12, 1, 2) THEN 'Summer'
            WHEN EXTRACT(MONTH FROM date) IN (3, 4, 5) THEN 'Autumn'
            WHEN EXTRACT(MONTH FROM date) IN (6, 7, 8) THEN 'Winter'
            WHEN EXTRACT(MONTH FROM date) IN (9, 10, 11) THEN 'Spring'
        END as season,
        EXTRACT(YEAR FROM date) as year
    FROM africlimate_climate_db.chirps_data
    WHERE year >= 2020
      AND year <= 2023
      AND precipitation IS NOT NULL
      AND latitude BETWEEN -35 AND -22
      AND longitude BETWEEN 16 AND 33
)
SELECT 
    season,
    year,
    AVG(precipitation) as seasonal_avg_precip,
    MIN(precipitation) as seasonal_min_precip,
    MAX(precipitation) as seasonal_max_precip,
    COUNT(*) as data_points,
    LAG(AVG(precipitation)) OVER (PARTITION BY season ORDER BY year) as previous_year_same_season,
    ROUND(AVG(precipitation) - LAG(AVG(precipitation)) OVER (PARTITION BY season ORDER BY year), 1) as year_over_year_change
FROM seasonal_precip
GROUP BY season, year
ORDER BY season, year;

-- Query 5: Alert Summary for Dashboard (Last 7 Days)
SELECT 
    current_date as analysis_date,
    COUNT(DISTINCT CASE WHEN precipitation < 25 THEN 1 END) as severe_drought_regions,
    COUNT(DISTINCT CASE WHEN precipitation >= 25 AND precipitation < 50 THEN 1 END) as moderate_drought_regions,
    COUNT(DISTINCT CASE WHEN precipitation >= 50 AND precipitation < 75 THEN 1 END) as below_normal_regions,
    COUNT(DISTINCT CASE WHEN precipitation >= 75 THEN 1 END) as normal_regions,
    COUNT(*) as total_regions_analyzed,
    ROUND(AVG(precipitation), 1) as avg_precipitation_all_regions,
    MIN(precipitation) as min_precipitation,
    MAX(precipitation) as max_precipitation
FROM africlimate_climate_db.chirps_data
WHERE year >= 2020
  AND year <= 2023
  AND precipitation IS NOT NULL
  AND latitude BETWEEN -35 AND -22
  AND longitude BETWEEN 16 AND 33;
