import numpy as np
import pandas as pd
from scipy import stats
from datetime import datetime, timedelta

class ClimateMetricsCalculator:
    """
    Advanced climate metrics calculation for CHIRPS data
    """
    
    def __init__(self):
        self.lat_min, self.lat_max = -35, -22
        self.lon_min, self.lon_max = 16, 33
        
    def calculate_drought_indices(self, precipitation_data, historical_data=None):
        """
        Calculate Standardized Precipitation Index (SPI) and other drought metrics
        """
        metrics = {}
        
        # Standardized Precipitation Index (SPI)
        if historical_data is not None and len(historical_data) >= 30:
            metrics['spi_1_month'] = self.calculate_spi(precipitation_data, historical_data, 1)
            metrics['spi_3_month'] = self.calculate_spi(precipitation_data, historical_data, 3)
            metrics['spi_6_month'] = self.calculate_spi(precipitation_data, historical_data, 6)
        
        # Drought classification
        current_precip = np.mean(precipitation_data)
        metrics['drought_class'] = self.classify_drought(current_precip)
        metrics['precipitation_anomaly'] = self.calculate_anomaly(precipitation_data, historical_data)
        
        return metrics
    
    def calculate_spi(self, current_data, historical_data, timescale_months):
        """
        Calculate Standardized Precipitation Index
        """
        if len(historical_data) < timescale_months:
            return None
            
        # Calculate rolling average for historical data
        historical_rolling = []
        for i in range(len(historical_data) - timescale_months + 1):
            window_data = historical_data[i:i + timescale_months]
            historical_rolling.append(np.mean(window_data))
        
        # Calculate current rolling average
        if len(current_data) >= timescale_months:
            current_rolling = np.mean(current_data[-timescale_months:])
        else:
            current_rolling = np.mean(current_data)
        
        # Standardize (z-score)
        if len(historical_rolling) > 0:
            mean_hist = np.mean(historical_rolling)
            std_hist = np.std(historical_rolling)
            
            if std_hist > 0:
                spi = (current_rolling - mean_hist) / std_hist
                return float(spi)
        
        return None
    
    def classify_drought(self, precipitation_mm):
        """
        Classify drought based on precipitation amount
        """
        if precipitation_mm < 10:
            return 'EXTREME_DROUGHT'
        elif precipitation_mm < 25:
            return 'SEVERE_DROUGHT'
        elif precipitation_mm < 50:
            return 'MODERATE_DROUGHT'
        elif precipitation_mm < 75:
            return 'ABNORMALLY_DRY'
        else:
            return 'NORMAL'
    
    def calculate_anomaly(self, current_data, historical_data):
        """
        Calculate precipitation anomaly (departure from normal)
        """
        if historical_data is None or len(historical_data) == 0:
            return None
            
        current_mean = np.mean(current_data)
        historical_mean = np.mean(historical_data)
        
        if historical_mean > 0:
            anomaly_percent = ((current_mean - historical_mean) / historical_mean) * 100
            return float(anomaly_percent)
        
        return None
    
    def calculate_rolling_averages(self, time_series_data):
        """
        Calculate rolling averages for different time periods
        """
        df = pd.DataFrame(time_series_data)
        
        # 30-day rolling average
        df['rolling_30d_avg'] = df['precipitation_mm'].rolling(window=30, min_periods=1).mean()
        
        # 90-day rolling average
        df['rolling_90d_avg'] = df['precipitation_mm'].rolling(window=90, min_periods=1).mean()
        
        # 6-month rolling average
        df['rolling_6m_avg'] = df['precipitation_mm'].rolling(window=6, min_periods=1).mean()
        
        # 12-month rolling average
        df['rolling_12m_avg'] = df['precipitation_mm'].rolling(window=12, min_periods=1).mean()
        
        return df
    
    def calculate_regional_statistics(self, df):
        """
        Calculate regional statistics for Southern Africa
        """
        regional_stats = {}
        
        # Group by region (can be extended with actual regions)
        regional_stats['southern_africa'] = {
            'mean_precipitation': df['precipitation_mm'].mean(),
            'median_precipitation': df['precipitation_mm'].median(),
            'std_precipitation': df['precipitation_mm'].std(),
            'min_precipitation': df['precipitation_mm'].min(),
            'max_precipitation': df['precipitation_mm'].max(),
            'total_points': len(df),
            'dry_points': len(df[df['precipitation_mm'] < 25]),
            'wet_points': len(df[df['precipitation_mm'] > 100])
        }
        
        # Calculate by latitude bands
        lat_bands = [
            (-35, -30, "Southern"),
            (-30, -25, "Central"), 
            (-25, -22, "Northern")
        ]
        
        regional_stats['by_latitude'] = {}
        for lat_min, lat_max, band_name in lat_bands:
            band_data = df[(df['latitude'] >= lat_min) & (df['latitude'] <= lat_max)]
            
            if len(band_data) > 0:
                regional_stats['by_latitude'][band_name] = {
                    'mean_precipitation': band_data['precipitation_mm'].mean(),
                    'total_points': len(band_data),
                    'drought_percentage': len(band_data[band_data['precipitation_mm'] < 25]) / len(band_data) * 100
                }
        
        return regional_stats
    
    def calculate_seasonal_metrics(self, df):
        """
        Calculate seasonal metrics for Southern Africa
        """
        # Southern Africa seasons
        def get_season(month):
            if month in [12, 1, 2]:
                return 'SUMMER'
            elif month in [3, 4, 5]:
                return 'AUTUMN'
            elif month in [6, 7, 8]:
                return 'WINTER'
            else:
                return 'SPRING'
        
        df['season'] = df['month'].apply(get_season)
        
        seasonal_stats = {}
        for season in ['SUMMER', 'AUTUMN', 'WINTER', 'SPRING']:
            season_data = df[df['season'] == season]
            
            if len(season_data) > 0:
                seasonal_stats[season] = {
                    'mean_precipitation': season_data['precipitation_mm'].mean(),
                    'total_precipitation': season_data['precipitation_mm'].sum(),
                    'dry_months': len(season_data[season_data['precipitation_mm'] < 25]),
                    'total_months': len(season_data)
                }
        
        return seasonal_stats
    
    def enhance_climate_data(self, df, historical_data=None):
        """
        Enhance climate data with advanced metrics
        """
        enhanced_df = df.copy()
        
        # Add drought indices
        if historical_data is not None:
            drought_metrics = self.calculate_drought_indices(
                df['precipitation_mm'].values, 
                historical_data
            )
            
            for key, value in drought_metrics.items():
                if value is not None:
                    enhanced_df[key] = value
        
        # Add rolling averages
        enhanced_df = self.calculate_rolling_averages(enhanced_df)
        
        # Add drought classification
        enhanced_df['drought_class'] = enhanced_df['precipitation_mm'].apply(self.classify_drought)
        
        # Add precipitation percentiles
        enhanced_df['precipitation_percentile'] = enhanced_df['precipitation_mm'].rank(pct=True) * 100
        
        # Add extreme weather flags
        enhanced_df['extreme_dry'] = enhanced_df['precipitation_mm'] < 10
        enhanced_df['extreme_wet'] = enhanced_df['precipitation_mm'] > 200
        
        # Add season
        def get_season(month):
            if month in [12, 1, 2]:
                return 'SUMMER'
            elif month in [3, 4, 5]:
                return 'AUTUMN'
            elif month in [6, 7, 8]:
                return 'WINTER'
            else:
                return 'SPRING'
        
        enhanced_df['season'] = enhanced_df['month'].apply(get_season)
        
        return enhanced_df

# Example usage and testing
if __name__ == "__main__":
    calculator = ClimateMetricsCalculator()
    
    # Test data
    test_data = np.random.normal(50, 30, 100)  # 100 months of precipitation data
    historical_data = np.random.normal(60, 25, 120)  # Historical data
    
    # Calculate metrics
    drought_metrics = calculator.calculate_drought_indices(test_data, historical_data)
    print("Drought Metrics:", drought_metrics)
    
    # Test with DataFrame
    test_df = pd.DataFrame({
        'year': [2024] * 100,
        'month': [1] * 100,
        'latitude': np.random.uniform(-35, -22, 100),
        'longitude': np.random.uniform(16, 33, 100),
        'precipitation_mm': test_data
    })
    
    enhanced_df = calculator.enhance_climate_data(test_df, historical_data)
    print("Enhanced DataFrame columns:", enhanced_df.columns.tolist())
    print("Sample enhanced data:")
    print(enhanced_df.head())
