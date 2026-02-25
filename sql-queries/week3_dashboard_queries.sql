-- Week 3 Dashboard Queries for AfriClimate Analytics Lake
-- 5 Required Visualizations per Weekly Documentation

-- ==========================================
-- VISUALIZATION 1: African Precipitation Heatmap
-- ==========================================
SELECT 
    latitude,
    longitude,
    AVG(rainfall) as avg_annual_rainfall,
    year
FROM africlimate_climate_db.chirps_data 
WHERE latitude BETWEEN -35 AND -22 
    AND longitude BETWEEN 16 AND 33
    AND year >= 2020
GROUP BY latitude, longitude, year
ORDER BY year, latitude, longitude;

-- ==========================================
-- VISUALIZATION 2: Drought Trend Analysis
-- ==========================================
SELECT 
    date_trunc('month', date) as month,
    AVG(spi_3month) as avg_spi_3month,
    AVG(spi_6month) as avg_spi_6month,
    AVG(spi_12month) as avg_spi_12month,
    COUNT(CASE WHEN spi_3month < -1.0 THEN 1 END) as drought_days,
    COUNT(*) as total_days
FROM africlimate_climate_db.drought_metrics 
WHERE date >= '2020-01-01'
GROUP BY date_trunc('month', date)
ORDER BY month;

-- ==========================================
-- VISUALIZATION 3: Regional Comparison Charts
-- ==========================================
WITH regional_stats AS (
    SELECT 
        CASE 
            WHEN latitude BETWEEN -22 AND -25 THEN 'Northern Region'
            WHEN latitude BETWEEN -25 AND -30 THEN 'Central Region' 
            WHEN latitude BETWEEN -30 AND -35 THEN 'Southern Region'
        END as region,
        year,
        AVG(rainfall) as avg_annual_rainfall,
        STDDEV(rainfall) as rainfall_variability,
        MIN(rainfall) as min_rainfall,
        MAX(rainfall) as max_rainfall
    FROM africlimate_climate_db.chirps_data 
    WHERE latitude BETWEEN -35 AND -22 
        AND longitude BETWEEN 16 AND 33
        AND year >= 2020
    GROUP BY region, year
)
SELECT 
    region,
    year,
    avg_annual_rainfall,
    rainfall_variability,
    LAG(avg_annual_rainfall) OVER (PARTITION BY region ORDER BY year) as prev_year_rainfall,
    ROUND((avg_annual_rainfall - LAG(avg_annual_rainfall) OVER (PARTITION BY region ORDER BY year)) / 
          LAG(avg_annual_rainfall) OVER (PARTITION BY region ORDER BY year) * 100, 2) as year_over_year_change
FROM regional_stats
ORDER BY region, year;

-- ==========================================
-- VISUALIZATION 4: Year-over-Year Changes
-- ==========================================
WITH yearly_comparison AS (
    SELECT 
        year,
        AVG(rainfall) as avg_annual_rainfall,
        SUM(rainfall) as total_annual_rainfall,
        COUNT(*) as observation_count,
        STDDEV(rainfall) as rainfall_stddev
    FROM africlimate_climate_db.chirps_data 
    WHERE latitude BETWEEN -35 AND -22 
        AND longitude BETWEEN 16 AND 33
        AND year >= 2020
    GROUP BY year
),
year_over_year AS (
    SELECT 
        year,
        avg_annual_rainfall,
        total_annual_rainfall,
        LAG(avg_annual_rainfall) OVER (ORDER BY year) as prev_year_avg,
        LAG(total_annual_rainfall) OVER (ORDER BY year) as prev_year_total,
        ROUND((avg_annual_rainfall - LAG(avg_annual_rainfall) OVER (ORDER BY year)) / 
              LAG(avg_annual_rainfall) OVER (ORDER BY year) * 100, 2) as rainfall_change_percent,
        ROUND((total_annual_rainfall - LAG(total_annual_rainfall) OVER (ORDER BY year)) / 
              LAG(total_annual_rainfall) OVER (ORDER BY year) * 100, 2) as total_change_percent
    FROM yearly_comparison
)
SELECT 
    year,
    avg_annual_rainfall,
    prev_year_avg,
    rainfall_change_percent,
    total_annual_rainfall,
    prev_year_total,
    total_change_percent,
    CASE 
        WHEN rainfall_change_percent > 10 THEN 'Above Normal'
        WHEN rainfall_change_percent < -10 THEN 'Below Normal'
        ELSE 'Normal'
    END as rainfall_status
FROM year_over_year
WHERE prev_year_avg IS NOT NULL
ORDER BY year;

-- ==========================================
-- VISUALIZATION 5: Anomaly Detection Scatter Plot
-- ==========================================
WITH monthly_normals AS (
    SELECT 
        EXTRACT(month FROM date) as month,
        AVG(rainfall) as climatology_rainfall,
        STDDEV(rainfall) as rainfall_stddev
    FROM africlimate_climate_db.chirps_data 
    WHERE latitude BETWEEN -35 AND -22 
        AND longitude BETWEEN 16 AND 33
        AND date >= '2020-01-01'
    GROUP BY EXTRACT(month FROM date)
),
anomalies AS (
    SELECT 
        c.date,
        c.year,
        EXTRACT(month FROM c.date) as month,
        c.latitude,
        c.longitude,
        c.rainfall,
        n.climatology_rainfall,
        n.rainfall_stddev,
        (c.rainfall - n.climatology_rainfall) / n.rainfall_stddev as rainfall_anomaly
    FROM africlimate_climate_db.chirps_data c
    JOIN monthly_normals n ON EXTRACT(month FROM c.date) = n.month
    WHERE c.latitude BETWEEN -35 AND -22 
        AND c.longitude BETWEEN 16 AND 33
        AND c.date >= '2020-01-01'
)
SELECT 
    date,
    year,
    month,
    latitude,
    longitude,
    rainfall,
    climatology_rainfall,
    rainfall_anomaly,
    CASE 
        WHEN ABS(rainfall_anomaly) > 2.0 THEN 'Extreme Anomaly'
        WHEN ABS(rainfall_anomaly) > 1.5 THEN 'Severe Anomaly'
        WHEN ABS(rainfall_anomaly) > 1.0 THEN 'Moderate Anomaly'
        ELSE 'Normal'
    END as anomaly_category
FROM anomalies
WHERE ABS(rainfall_anomaly) > 1.0  -- Only show significant anomalies
ORDER BY ABS(rainfall_anomaly) DESC;

-- ==========================================
-- ADDITIONAL: Drought Early Warning Metrics
-- ==========================================
SELECT 
    date,
    spi_3month,
    spi_6month,
    spi_12month,
    CASE 
        WHEN spi_3month < -2.0 THEN 'Extreme Drought'
        WHEN spi_3month < -1.5 THEN 'Severe Drought'
        WHEN spi_3month < -1.0 THEN 'Moderate Drought'
        WHEN spi_3month < -0.5 THEN 'Mild Drought'
        ELSE 'No Drought'
    END as drought_category,
    LAG(spi_3month, 7) OVER (ORDER BY date) as spi_3month_week_ago,
    ROUND(spi_3month - LAG(spi_3month, 7) OVER (ORDER BY date), 2) as spi_change_7days
FROM africlimate_climate_db.drought_metrics 
WHERE date >= DATEADD('day', -30, CURRENT_DATE)
ORDER BY date DESC;
