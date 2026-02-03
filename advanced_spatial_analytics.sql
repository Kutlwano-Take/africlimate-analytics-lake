-- ========================================
-- WEEK 2: ADVANCED SPATIAL ANALYTICS QUERIES
-- AfriClimate Analytics Lake - Southern Africa Focus
-- ========================================

-- ========================================
-- QUERY 1: Regional Drought Analysis
-- Identifies regions experiencing drought conditions
-- ========================================
WITH regional_monthly_precip AS (
    SELECT
        year,
        month,
        AVG(precipitation_mm) as regional_avg_precip,
        COUNT(*) as data_points,
        STDDEV(precipitation_mm) as precip_stddev
    FROM africlimate_climate_db.chirps_monthly_processed
    WHERE latitude BETWEEN -35 AND -22 
      AND longitude BETWEEN 16 AND 33
    GROUP BY year, month
),
historical_baseline AS (
    SELECT
        month,
        AVG(regional_avg_precip) as historical_avg,
        STDDEV(regional_avg_precip) as historical_std
    FROM regional_monthly_precip
    WHERE year BETWEEN 2016 AND 2020
    GROUP BY month
),
drought_analysis AS (
    SELECT
        r.year,
        r.month,
        r.regional_avg_precip,
        h.historical_avg,
        h.historical_std,
        (r.regional_avg_precip - h.historical_avg) / NULLIF(h.historical_std, 0) as precipitation_zscore,
        CASE 
            WHEN r.regional_avg_precip < 25 THEN 'EXTREME_DROUGHT'
            WHEN r.regional_avg_precip < 50 THEN 'SEVERE_DROUGHT'
            WHEN r.regional_avg_precip < 75 THEN 'MODERATE_DROUGHT'
            WHEN r.regional_avg_precip < 100 THEN 'ABNORMALLY_DRY'
            ELSE 'NORMAL'
        END as drought_classification
    FROM regional_monthly_precip r
    JOIN historical_baseline h ON r.month = h.month
)
SELECT 
    year,
    month,
    drought_classification,
    regional_avg_precip,
    historical_avg,
    precipitation_zscore,
    ROUND((regional_avg_precip / historical_avg - 1) * 100, 2) as precipitation_anomaly_percent
FROM drought_analysis
WHERE precipitation_zscore < -1.0  -- Below normal precipitation
ORDER BY year DESC, month DESC;

-- ========================================
-- QUERY 2: Seasonal Precipitation Trends
-- Analyzes seasonal patterns and trends over time
-- ========================================
WITH seasonal_data AS (
    SELECT
        year,
        CASE 
            WHEN month IN (12, 1, 2) THEN 'SUMMER'
            WHEN month IN (3, 4, 5) THEN 'AUTUMN'
            WHEN month IN (6, 7, 8) THEN 'WINTER'
            ELSE 'SPRING'
        END as season,
        AVG(precipitation_mm) as seasonal_precip,
        COUNT(*) as data_points
    FROM africlimate_climate_db.chirps_monthly_processed
    WHERE latitude BETWEEN -35 AND -22 
      AND longitude BETWEEN 16 AND 33
    GROUP BY year, season
),
seasonal_trends AS (
    SELECT
        season,
        AVG(seasonal_precip) as avg_seasonal_precip,
        STDDEV(seasonal_precip) as seasonal_variability,
        COUNT(DISTINCT year) as years_analyzed
    FROM seasonal_data
    GROUP BY season
)
SELECT 
    s.season,
    s.year,
    s.seasonal_precip,
    t.avg_seasonal_precip as historical_average,
    ROUND((s.seasonal_precip / t.avg_seasonal_precip - 1) * 100, 2) as seasonal_anomaly_percent,
    CASE 
        WHEN s.seasonal_precip < t.avg_seasonal_precip * 0.7 THEN 'DRY_SEASON'
        WHEN s.seasonal_precip > t.avg_seasonal_precip * 1.3 THEN 'WET_SEASON'
        ELSE 'NORMAL_SEASON'
    END as season_type
FROM seasonal_data s
JOIN seasonal_trends t ON s.season = t.season
ORDER BY s.year DESC, s.season;

-- ========================================
-- QUERY 3: Precipitation Anomaly Detection
-- Identifies areas with unusual precipitation patterns
-- ========================================
WITH monthly_climatology AS (
    SELECT
        month,
        latitude,
        longitude,
        AVG(precipitation_mm) as climatology_mean,
        STDDEV(precipitation_mm) as climatology_std
    FROM africlimate_climate_db.chirps_monthly_processed
    WHERE year BETWEEN 2016 AND 2020
      AND latitude BETWEEN -35 AND -22 
      AND longitude BETWEEN 16 AND 33
    GROUP BY month, latitude, longitude
),
current_anomalies AS (
    SELECT
        c.year,
        c.month,
        c.latitude,
        c.longitude,
        c.precipitation_mm,
        m.climatology_mean,
        m.climatology_std,
        (c.precipitation_mm - m.climatology_mean) / NULLIF(m.climatology_std, 0) as anomaly_zscore,
        CASE 
            WHEN ABS((c.precipitation_mm - m.climatology_mean) / NULLIF(m.climatology_std, 0)) > 2 THEN 'EXTREME_ANOMALY'
            WHEN ABS((c.precipitation_mm - m.climatology_mean) / NULLIF(m.climatology_std, 0)) > 1.5 THEN 'SIGNIFICANT_ANOMALY'
            WHEN ABS((c.precipitation_mm - m.climatology_mean) / NULLIF(m.climatology_std, 0)) > 1 THEN 'MODERATE_ANOMALY'
            ELSE 'NORMAL'
        END as anomaly_classification
    FROM africlimate_climate_db.chirps_monthly_processed c
    JOIN monthly_climatology m ON c.month = m.month 
        AND c.latitude = m.latitude 
        AND c.longitude = m.longitude
    WHERE c.year >= 2021
      AND c.latitude BETWEEN -35 AND -22 
      AND c.longitude BETWEEN 16 AND 33
)
SELECT 
    year,
    month,
    anomaly_classification,
    COUNT(*) as affected_locations,
    AVG(ABS(anomaly_zscore)) as avg_anomaly_magnitude,
    MAX(ABS(anomaly_zscore)) as max_anomaly_magnitude,
    ROUND(AVG(precipitation_mm), 2) as avg_current_precip,
    ROUND(AVG(climatology_mean), 2) as avg_climatology_precip
FROM current_anomalies
WHERE anomaly_classification != 'NORMAL'
GROUP BY year, month, anomaly_classification
ORDER BY year DESC, month DESC, affected_locations DESC;

-- ========================================
-- QUERY 4: Year-over-Year Precipitation Comparison
-- Compares precipitation patterns between consecutive years
-- ========================================
WITH yearly_comparison AS (
    SELECT
        current.year as current_year,
        previous.year as previous_year,
        current.month,
        AVG(current.precipitation_mm) as current_avg,
        AVG(previous.precipitation_mm) as previous_avg,
        COUNT(*) as data_points
    FROM africlimate_climate_db.chirps_monthly_processed current
    JOIN africlimate_climate_db.chirps_monthly_processed previous 
        ON current.month = previous.month 
        AND current.latitude = previous.latitude 
        AND current.longitude = previous.longitude
        AND current.year = previous.year + 1
    WHERE current.latitude BETWEEN -35 AND -22 
      AND current.longitude BETWEEN 16 AND 33
      AND current.year >= 2020
    GROUP BY current.year, previous.year, current.month
),
yearly_changes AS (
    SELECT
        current_year,
        previous_year,
        month,
        current_avg,
        previous_avg,
        (current_avg - previous_avg) as absolute_change,
        ROUND((current_avg / previous_avg - 1) * 100, 2) as percent_change,
        CASE 
            WHEN (current_avg / previous_avg - 1) * 100 > 50 THEN 'SIGNIFICANT_INCREASE'
            WHEN (current_avg / previous_avg - 1) * 100 > 20 THEN 'MODERATE_INCREASE'
            WHEN (current_avg / previous_avg - 1) * 100 < -50 THEN 'SIGNIFICANT_DECREASE'
            WHEN (current_avg / previous_avg - 1) * 100 < -20 THEN 'MODERATE_DECREASE'
            ELSE 'STABLE'
        END as change_classification
    FROM yearly_comparison
    WHERE previous_avg > 0
)
SELECT 
    current_year,
    previous_year,
    month,
    change_classification,
    current_avg,
    previous_avg,
    absolute_change,
    percent_change
FROM yearly_changes
WHERE change_classification != 'STABLE'
ORDER BY current_year DESC, month DESC, ABS(percent_change) DESC;

-- ========================================
-- QUERY 5: Precipitation Intensity Analysis
-- Analyzes the distribution of precipitation intensities
-- ========================================
WITH intensity_categories AS (
    SELECT
        year,
        month,
        COUNT(*) as total_locations,
        COUNT(CASE WHEN precipitation_mm < 1 THEN 1 END) as no_rain_locations,
        COUNT(CASE WHEN precipitation_mm >= 1 AND precipitation_mm < 10 THEN 1 END) as light_rain_locations,
        COUNT(CASE WHEN precipitation_mm >= 10 AND precipitation_mm < 25 THEN 1 END) as moderate_rain_locations,
        COUNT(CASE WHEN precipitation_mm >= 25 AND precipitation_mm < 50 THEN 1 END) as heavy_rain_locations,
        COUNT(CASE WHEN precipitation_mm >= 50 AND precipitation_mm < 100 THEN 1 END) as very_heavy_rain_locations,
        COUNT(CASE WHEN precipitation_mm >= 100 THEN 1 END) as extreme_rain_locations,
        AVG(precipitation_mm) as avg_precipitation,
        MAX(precipitation_mm) as max_precipitation
    FROM africlimate_climate_db.chirps_monthly_processed
    WHERE latitude BETWEEN -35 AND -22 
      AND longitude BETWEEN 16 AND 33
    GROUP BY year, month
)
SELECT 
    year,
    month,
    total_locations,
    ROUND(no_rain_locations * 100.0 / total_locations, 2) as no_rain_percentage,
    ROUND(light_rain_locations * 100.0 / total_locations, 2) as light_rain_percentage,
    ROUND(moderate_rain_locations * 100.0 / total_locations, 2) as moderate_rain_percentage,
    ROUND(heavy_rain_locations * 100.0 / total_locations, 2) as heavy_rain_percentage,
    ROUND(very_heavy_rain_locations * 100.0 / total_locations, 2) as very_heavy_rain_percentage,
    ROUND(extreme_rain_locations * 100.0 / total_locations, 2) as extreme_rain_percentage,
    ROUND(avg_precipitation, 2) as avg_precipitation_mm,
    ROUND(max_precipitation, 2) as max_precipitation_mm,
    CASE 
        WHEN extreme_rain_locations > total_locations * 0.1 THEN 'EXTREME_RAIN_EVENT'
        WHEN very_heavy_rain_locations > total_locations * 0.2 THEN 'HEAVY_RAIN_EVENT'
        WHEN no_rain_locations > total_locations * 0.8 THEN 'WIDESPREAD_DROUGHT'
        ELSE 'NORMAL_PATTERN'
    END as weather_pattern_type
FROM intensity_categories
ORDER BY year DESC, month DESC;

-- ========================================
-- QUERY 6: Spatial Correlation Analysis
-- Analyzes precipitation patterns across different regions
-- ========================================
WITH regional_monthly AS (
    SELECT
        year,
        month,
        CASE 
            WHEN latitude BETWEEN -35 AND -30 THEN 'SOUTHERN_REGION'
            WHEN latitude BETWEEN -30 AND -25 THEN 'CENTRAL_REGION'
            WHEN latitude BETWEEN -25 AND -22 THEN 'NORTHERN_REGION'
        END as region,
        AVG(precipitation_mm) as regional_precip
    FROM africlimate_climate_db.chirps_monthly_processed
    WHERE latitude BETWEEN -35 AND -22 
      AND longitude BETWEEN 16 AND 33
    GROUP BY year, month, region
),
regional_pivot AS (
    SELECT 
        year,
        month,
        MAX(CASE WHEN region = 'SOUTHERN_REGION' THEN regional_precip END) as southern_precip,
        MAX(CASE WHEN region = 'CENTRAL_REGION' THEN regional_precip END) as central_precip,
        MAX(CASE WHEN region = 'NORTHERN_REGION' THEN regional_precip END) as northern_precip
    FROM regional_monthly
    GROUP BY year, month
),
correlation_analysis AS (
    SELECT
        CORR(southern_precip, central_precip) as southern_central_corr,
        CORR(southern_precip, northern_precip) as southern_northern_corr,
        CORR(central_precip, northern_precip) as central_northern_corr,
        COUNT(*) as months_analyzed
    FROM regional_pivot
    WHERE southern_precip IS NOT NULL 
      AND central_precip IS NOT NULL 
      AND northern_precip IS NOT NULL
)
SELECT 
    ROUND(southern_central_corr, 3) as southern_central_correlation,
    ROUND(southern_northern_corr, 3) as southern_northern_correlation,
    ROUND(central_northern_corr, 3) as central_northern_correlation,
    months_analyzed,
    CASE 
        WHEN ABS(southern_central_corr) > 0.7 THEN 'STRONG_CORRELATION'
        WHEN ABS(southern_central_corr) > 0.4 THEN 'MODERATE_CORRELATION'
        ELSE 'WEAK_CORRELATION'
    END as southern_central_relationship,
    CASE 
        WHEN ABS(southern_northern_corr) > 0.7 THEN 'STRONG_CORRELATION'
        WHEN ABS(southern_northern_corr) > 0.4 THEN 'MODERATE_CORRELATION'
        ELSE 'WEAK_CORRELATION'
    END as southern_northern_relationship
FROM correlation_analysis;

-- ========================================
-- QUERY 7: Long-term Precipitation Trends
-- Identifies multi-year precipitation trends
-- ========================================
WITH annual_precipitation AS (
    SELECT
        year,
        AVG(precipitation_mm) as annual_avg_precip,
        COUNT(*) as data_points,
        STDDEV(precipitation_mm) as annual_stddev
    FROM africlimate_climate_db.chirps_monthly_processed
    WHERE latitude BETWEEN -35 AND -22 
      AND longitude BETWEEN 16 AND 33
    GROUP BY year
),
trend_analysis AS (
    SELECT
        year,
        annual_avg_precip,
        LAG(annual_avg_precip, 1) OVER (ORDER BY year) as prev_year_precip,
        LAG(annual_avg_precip, 5) OVER (ORDER BY year) as five_year_avg_precip,
        ROUND(annual_avg_precip - LAG(annual_avg_precip, 1) OVER (ORDER BY year), 2) as year_over_year_change,
        ROUND((annual_avg_precip / LAG(annual_avg_precip, 1) OVER (ORDER BY year) - 1) * 100, 2) as year_over_year_percent_change
    FROM annual_precipitation
),
trend_summary AS (
    SELECT
        AVG(year_over_year_change) as avg_annual_change,
        STDDEV(year_over_year_change) as change_volatility,
        COUNT(*) as years_analyzed,
        CORR(year, annual_avg_precip) as long_term_trend_correlation
    FROM trend_analysis
    WHERE year_over_year_change IS NOT NULL
)
SELECT 
    t.year,
    t.annual_avg_precip,
    t.prev_year_precip,
    t.year_over_year_change,
    t.year_over_year_percent_change,
    CASE 
        WHEN t.year_over_year_percent_change > 20 THEN 'SIGNIFICANT_INCREASE'
        WHEN t.year_over_year_percent_change > 10 THEN 'MODERATE_INCREASE'
        WHEN t.year_over_year_percent_change < -20 THEN 'SIGNIFICANT_DECREASE'
        WHEN t.year_over_year_percent_change < -10 THEN 'MODERATE_DECREASE'
        ELSE 'STABLE'
    END as annual_trend_type,
    s.avg_annual_change as overall_trend_direction,
    ROUND(s.long_term_trend_correlation, 3) as long_term_correlation
FROM trend_analysis t
CROSS JOIN trend_summary s
ORDER BY t.year DESC;

-- ========================================
-- QUERY 8: Extreme Weather Event Detection
-- Identifies months with extreme precipitation events
-- ========================================
WITH extreme_events AS (
    SELECT
        year,
        month,
        COUNT(*) as total_locations,
        COUNT(CASE WHEN precipitation_mm > 150 THEN 1 END) as extreme_wet_locations,
        COUNT(CASE WHEN precipitation_mm < 5 THEN 1 END) as extreme_dry_locations,
        MAX(precipitation_mm) as max_precipitation,
        MIN(precipitation_mm) as min_precipitation,
        AVG(precipitation_mm) as avg_precipitation,
        STDDEV(precipitation_mm) as precip_variability
    FROM africlimate_climate_db.chirps_monthly_processed
    WHERE latitude BETWEEN -35 AND -22 
      AND longitude BETWEEN 16 AND 33
    GROUP BY year, month
),
event_classification AS (
    SELECT
        year,
        month,
        total_locations,
        extreme_wet_locations,
        extreme_dry_locations,
        max_precipitation,
        min_precipitation,
        avg_precipitation,
        precip_variability,
        ROUND(extreme_wet_locations * 100.0 / total_locations, 2) as extreme_wet_percentage,
        ROUND(extreme_dry_locations * 100.0 / total_locations, 2) as extreme_dry_percentage,
        CASE 
            WHEN extreme_wet_locations > total_locations * 0.15 OR max_precipitation > 300 THEN 'EXTREME_FLOODING'
            WHEN extreme_wet_locations > total_locations * 0.08 OR max_precipitation > 200 THEN 'HEAVY_RAINFALL'
            WHEN extreme_dry_locations > total_locations * 0.8 OR avg_precipitation < 10 THEN 'EXTREME_DROUGHT'
            WHEN extreme_dry_locations > total_locations * 0.6 OR avg_precipitation < 25 THEN 'SEVERE_DRYNESS'
            WHEN precip_variability > 100 THEN 'HIGH_VARIABILITY'
            ELSE 'NORMAL_CONDITIONS'
        END as event_type
    FROM extreme_events
)
SELECT 
    year,
    month,
    event_type,
    extreme_wet_percentage,
    extreme_dry_percentage,
    max_precipitation,
    min_precipitation,
    ROUND(avg_precipitation, 2) as avg_precipitation_mm,
    ROUND(precip_variability, 2) as precipitation_variability
FROM event_classification
WHERE event_type != 'NORMAL_CONDITIONS'
ORDER BY year DESC, month DESC;

-- ========================================
-- QUERY 9: Precipitation Distribution Analysis
-- Analyzes the statistical distribution of precipitation
-- ========================================
WITH monthly_statistics AS (
    SELECT
        year,
        month,
        COUNT(*) as sample_size,
        AVG(precipitation_mm) as mean_precip,
        STDDEV(precipitation_mm) as std_precip,
        MIN(precipitation_mm) as min_precip,
        MAX(precipitation_mm) as max_precip,
        APPROX_PERCENTILE(precipitation_mm, 0.25) as q25_precip,
        APPROX_PERCENTILE(precipitation_mm, 0.5) as median_precip,
        APPROX_PERCENTILE(precipitation_mm, 0.75) as q75_precip,
        APPROX_PERCENTILE(precipitation_mm, 0.90) as q90_precip,
        APPROX_PERCENTILE(precipitation_mm, 0.95) as q95_precip
    FROM africlimate_climate_db.chirps_monthly_processed
    WHERE latitude BETWEEN -35 AND -22 
      AND longitude BETWEEN 16 AND 33
    GROUP BY year, month
),
distribution_characteristics AS (
    SELECT
        year,
        month,
        mean_precip,
        median_precip,
        std_precip,
        min_precip,
        max_precip,
        q25_precip,
        q75_precip,
        q90_precip,
        q95_precip,
        (q75_precip - q25_precip) as iqr_precip,
        ROUND((mean_precip - median_precip) / NULLIF(std_precip, 0), 2) as skewness_indicator,
        ROUND((max_precip - min_precip) / NULLIF(mean_precip, 0), 2) as range_to_mean_ratio
    FROM monthly_statistics
)
SELECT 
    year,
    month,
    ROUND(mean_precip, 2) as mean_precipitation,
    ROUND(median_precip, 2) as median_precipitation,
    ROUND(std_precip, 2) as precipitation_stddev,
    ROUND(min_precip, 2) as min_precipitation,
    ROUND(max_precip, 2) as max_precipitation,
    ROUND(q25_precip, 2) as q25_precipitation,
    ROUND(q75_precip, 2) as q75_precipitation,
    ROUND(q90_precip, 2) as q90_precipitation,
    ROUND(q95_precip, 2) as q95_precipitation,
    ROUND(iqr_precip, 2) as interquartile_range,
    skewness_indicator,
    range_to_mean_ratio,
    CASE 
        WHEN ABS(skewness_indicator) > 1 THEN 'HIGHLY_SKEWED'
        WHEN ABS(skewness_indicator) > 0.5 THEN 'MODERATELY_SKEWED'
        ELSE 'NORMALLY_DISTRIBUTED'
    END as distribution_type,
    CASE 
        WHEN range_to_mean_ratio > 5 THEN 'HIGH_VARIABILITY'
        WHEN range_to_mean_ratio > 3 THEN 'MODERATE_VARIABILITY'
        ELSE 'LOW_VARIABILITY'
    END as variability_classification
FROM distribution_characteristics
ORDER BY year DESC, month DESC;

-- ========================================
-- QUERY 10: Regional Precipitation Ranking
-- Ranks regions by precipitation performance
-- ========================================
WITH regional_performance AS (
    SELECT
        year,
        month,
        CASE 
            WHEN latitude BETWEEN -35 AND -30 THEN 'SOUTHERN_REGION'
            WHEN latitude BETWEEN -30 AND -25 THEN 'CENTRAL_REGION'
            WHEN latitude BETWEEN -25 AND -22 THEN 'NORTHERN_REGION'
        END as region,
        AVG(precipitation_mm) as regional_avg_precip,
        COUNT(*) as data_points,
        STDDEV(precipitation_mm) as regional_stddev
    FROM africlimate_climate_db.chirps_monthly_processed
    WHERE latitude BETWEEN -35 AND -22 
      AND longitude BETWEEN 16 AND 33
    GROUP BY year, month, region
),
monthly_rankings AS (
    SELECT
        year,
        month,
        region,
        regional_avg_precip,
        regional_stddev,
        data_points,
        ROW_NUMBER() OVER (PARTITION BY year, month ORDER BY regional_avg_precip DESC) as precipitation_rank,
        ROUND(regional_avg_precip * 100.0 / SUM(regional_avg_precip) OVER (PARTITION BY year, month), 2) as precipitation_percentage
    FROM regional_performance
),
regional_summaries AS (
    SELECT
        region,
        AVG(regional_avg_precip) as overall_avg_precip,
        AVG(precipitation_rank) as average_rank,
        COUNT(*) as months_analyzed,
        COUNT(CASE WHEN precipitation_rank = 1 THEN 1 END) as wettest_months,
        COUNT(CASE WHEN precipitation_rank = 3 THEN 1 END) as driest_months
    FROM monthly_rankings
    GROUP BY region
)
SELECT 
    r.region,
    ROUND(r.overall_avg_precip, 2) as overall_average_precipitation,
    ROUND(r.average_rank, 1) as average_ranking,
    r.months_analyzed,
    r.wettest_months,
    r.driest_months,
    ROUND(r.wettest_months * 100.0 / r.months_analyzed, 2) as wettest_percentage,
    ROUND(r.driest_months * 100.0 / r.months_analyzed, 2) as driest_percentage,
    CASE 
        WHEN r.average_rank <= 1.5 THEN 'CONSISTENTLY_WET'
        WHEN r.average_rank >= 2.5 THEN 'CONSISTENTLY_DRY'
        ELSE 'VARIABLE'
    END as precipitation_pattern
FROM regional_summaries r
ORDER BY r.average_rank;

-- ========================================
-- QUERY 11: Precipitation Trend by Season
-- Analyzes seasonal trends over multiple years
-- ========================================
WITH seasonal_trends AS (
    SELECT
        year,
        CASE 
            WHEN month IN (12, 1, 2) THEN 'SUMMER'
            WHEN month IN (3, 4, 5) THEN 'AUTUMN'
            WHEN month IN (6, 7, 8) THEN 'WINTER'
            ELSE 'SPRING'
        END as season,
        AVG(precipitation_mm) as seasonal_precip,
        COUNT(*) as data_points,
        STDDEV(precipitation_mm) as seasonal_stddev
    FROM africlimate_climate_db.chirps_monthly_processed
    WHERE latitude BETWEEN -35 AND -22 
      AND longitude BETWEEN 16 AND 33
    GROUP BY year, season
),
seasonal_comparisons AS (
    SELECT
        season,
        year,
        seasonal_precip,
        LAG(seasonal_precip, 1) OVER (PARTITION BY season ORDER BY year) as prev_season_precip,
        ROUND(seasonal_precip - LAG(seasonal_precip, 1) OVER (PARTITION BY season ORDER BY year), 2) as year_over_year_change,
        ROUND((seasonal_precip / LAG(seasonal_precip, 1) OVER (PARTITION BY season ORDER BY year) - 1) * 100, 2) as year_over_year_percent_change
    FROM seasonal_trends
),
seasonal_statistics AS (
    SELECT
        season,
        AVG(seasonal_precip) as avg_seasonal_precip,
        STDDEV(seasonal_precip) as seasonal_variability,
        COUNT(DISTINCT year) as years_analyzed,
        CORR(year, seasonal_precip) as trend_correlation
    FROM seasonal_trends
    GROUP BY season
)
SELECT 
    s.season,
    s.year,
    ROUND(s.seasonal_precip, 2) as seasonal_precipitation,
    ROUND(s.prev_season_precip, 2) as previous_season_precipitation,
    s.year_over_year_change,
    s.year_over_year_percent_change,
    CASE 
        WHEN s.year_over_year_percent_change > 30 THEN 'SIGNIFICANT_INCREASE'
        WHEN s.year_over_year_percent_change > 15 THEN 'MODERATE_INCREASE'
        WHEN s.year_over_year_percent_change < -30 THEN 'SIGNIFICANT_DECREASE'
        WHEN s.year_over_year_percent_change < -15 THEN 'MODERATE_DECREASE'
        ELSE 'STABLE'
    END as seasonal_trend_type,
    ROUND(st.avg_seasonal_precip, 2) as seasonal_average,
    ROUND(st.trend_correlation, 3) as long_term_trend
FROM seasonal_comparisons s
JOIN seasonal_statistics st ON s.season = st.season
WHERE s.year_over_year_change IS NOT NULL
ORDER BY s.year DESC, s.season;

-- ========================================
-- QUERY 12: Comprehensive Climate Summary
-- Provides a comprehensive overview of climate conditions
-- ========================================
WITH monthly_summary AS (
    SELECT
        year,
        month,
        COUNT(*) as total_locations,
        AVG(precipitation_mm) as avg_precipitation,
        STDDEV(precipitation_mm) as precip_stddev,
        MIN(precipitation_mm) as min_precipitation,
        MAX(precipitation_mm) as max_precipitation,
        APPROX_PERCENTILE(precipitation_mm, 0.10) as p10_precip,
        APPROX_PERCENTILE(precipitation_mm, 0.90) as p90_precip,
        COUNT(CASE WHEN precipitation_mm < 25 THEN 1 END) as dry_locations,
        COUNT(CASE WHEN precipitation_mm > 100 THEN 1 END) as wet_locations
    FROM africlimate_climate_db.chirps_monthly_processed
    WHERE latitude BETWEEN -35 AND -22 
      AND longitude BETWEEN 16 AND 33
    GROUP BY year, month
),
historical_baseline AS (
    SELECT
        month,
        AVG(avg_precipitation) as historical_avg,
        STDDEV(avg_precipitation) as historical_std
    FROM monthly_summary
    WHERE year BETWEEN 2016 AND 2020
    GROUP BY month
),
climate_assessment AS (
    SELECT
        m.year,
        m.month,
        m.avg_precipitation,
        h.historical_avg,
        h.historical_std,
        (m.avg_precipitation - h.historical_avg) / NULLIF(h.historical_std, 0) as precipitation_zscore,
        ROUND(m.dry_locations * 100.0 / m.total_locations, 2) as dry_percentage,
        ROUND(m.wet_locations * 100.0 / m.total_locations, 2) as wet_percentage,
        m.precip_stddev,
        CASE 
            WHEN m.avg_precipitation < h.historical_avg * 0.5 THEN 'EXTREMELY_DRY'
            WHEN m.avg_precipitation < h.historical_avg * 0.75 THEN 'VERY_DRY'
            WHEN m.avg_precipitation < h.historical_avg * 0.9 THEN 'SLIGHTLY_DRY'
            WHEN m.avg_precipitation > h.historical_avg * 1.5 THEN 'EXTREMELY_WET'
            WHEN m.avg_precipitation > h.historical_avg * 1.25 THEN 'VERY_WET'
            WHEN m.avg_precipitation > h.historical_avg * 1.1 THEN 'SLIGHTLY_WET'
            ELSE 'NORMAL'
        END as climate_condition,
        CASE 
            WHEN m.precip_stddev > h.historical_std * 1.5 THEN 'HIGHLY_VARIABLE'
            WHEN m.precip_stddev > h.historical_std * 1.2 THEN 'MODERATELY_VARIABLE'
            ELSE 'STABLE'
        END as variability_condition
    FROM monthly_summary m
    JOIN historical_baseline h ON m.month = h.month
)
SELECT 
    year,
    month,
    climate_condition,
    variability_condition,
    ROUND(avg_precipitation, 2) as current_avg_precip,
    ROUND(historical_avg, 2) as historical_avg_precip,
    ROUND(precipitation_zscore, 2) as precipitation_zscore,
    dry_percentage,
    wet_percentage,
    ROUND(precip_stddev, 2) as precipitation_variability,
    ROUND(min_precipitation, 2) as min_precipitation,
    ROUND(max_precipitation, 2) as max_precipitation,
    CASE 
        WHEN climate_condition IN ('EXTREMELY_DRY', 'VERY_DRY') AND variability_condition = 'HIGHLY_VARIABLE' THEN 'CRITICAL_DROUGHT'
        WHEN climate_condition IN ('EXTREMELY_WET', 'VERY_WET') AND variability_condition = 'HIGHLY_VARIABLE' THEN 'FLOOD_RISK'
        WHEN climate_condition IN ('EXTREMELY_DRY', 'VERY_DRY') THEN 'DROUGHT_WARNING'
        WHEN climate_condition IN ('EXTREMELY_WET', 'VERY_WET') THEN 'HEAVY_RAINFALL'
        ELSE 'NORMAL_CONDITIONS'
    END as overall_assessment
FROM climate_assessment
ORDER BY year DESC, month DESC;
