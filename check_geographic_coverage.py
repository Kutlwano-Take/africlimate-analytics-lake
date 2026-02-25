import pandas as pd
import awswrangler as wr
import boto3
import os

# Setup AWS session
boto3.setup_default_session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION', 'af-south-1')
)

try:
    # Get sample data to understand coverage
    query = '''
    SELECT latitude, longitude, year, month, day, precipitation
    FROM africlimate_climate_db.chirps_data
    ORDER BY latitude, longitude
    LIMIT 50
    '''
    
    df_sample = wr.athena.read_sql_query(query, database="africlimate_climate_db")
    print('=== CHIRPS Data Sample (First 50 points) ===')
    for idx, row in df_sample.iterrows():
        # Determine province based on coordinates
        lat, lon = row['latitude'], row['longitude']
        province = 'Other'
        if -27 <= lat <= -25 and 27 <= lon <= 29:
            province = 'Gauteng'
        elif -24 <= lat <= -22 and 28 <= lon <= 32:
            province = 'Limpopo'
        elif -26 <= lat <= -24 and 29 <= lon <= 32:
            province = 'Mpumalanga'
        elif -30 <= lat <= -27 and 29 <= lon <= 33:
            province = 'KwaZulu-Natal'
        elif -31 <= lat <= -28 and 23 <= lon <= 30:
            province = 'Eastern Cape'
        elif -34 <= lat <= -31 and 18 <= lon <= 23:
            province = 'Western Cape'
        elif -32 <= lat <= -28 and 18 <= lon <= 24:
            province = 'Northern Cape'
        elif -27 <= lat <= -25 and 22 <= lon <= 27:
            province = 'North West'
        elif -30 <= lat <= -26 and 24 <= lon <= 29:
            province = 'Free State'
            
        print(f'Lat: {lat:6.2f}, Lon: {lon:6.2f} -> {province:15} | {row["year"]}-{row["month"]:02d}-{row["day"]:02d} | {row["precipitation"]:6.2f}mm')
        
    # Get coordinate bounds
    query_bounds = '''
    SELECT 
        MIN(latitude) as min_lat,
        MAX(latitude) as max_lat,
        MIN(longitude) as min_lon,
        MAX(longitude) as max_lon,
        COUNT(*) as total_points,
        COUNT(DISTINCT latitude) as unique_lats,
        COUNT(DISTINCT longitude) as unique_lons
    FROM africlimate_climate_db.chirps_data
    '''
    
    df_bounds = wr.athena.read_sql_query(query_bounds, database="africlimate_climate_db")
    print('\n=== Geographic Coverage Summary ===')
    print(f'Latitude Range:  {df_bounds.iloc[0]["min_lat"]:.2f}° to {df_bounds.iloc[0]["max_lat"]:.2f}°')
    print(f'Longitude Range: {df_bounds.iloc[0]["min_lon"]:.2f}° to {df_bounds.iloc[0]["max_lon"]:.2f}°')
    print(f'Total Points: {df_bounds.iloc[0]["total_points"]:,}')
    print(f'Grid Size: {df_bounds.iloc[0]["unique_lats"]:.0f} x {df_bounds.iloc[0]["unique_lons"]:.0f} coordinates')
    
    # Calculate what this covers in South African terms
    min_lat, max_lat = df_bounds.iloc[0]["min_lat"], df_bounds.iloc[0]["max_lat"]
    min_lon, max_lon = df_bounds.iloc[0]["min_lon"], df_bounds.iloc[0]["max_lon"]
    
    print('\n=== South African Province Coverage Analysis ===')
    print('Your data covers these coordinate ranges:')
    print(f'  Latitude: {min_lat:.1f}° to {max_lat:.1f}° (South to North)')
    print(f'  Longitude: {min_lon:.1f}° to {max_lon:.1f}° (West to East)')
    
    print('\nProvinces that should be covered:')
    provinces_covered = []
    if -34 <= min_lat and max_lat <= -25 and 18 <= min_lon and max_lon <= 33:
        if -34 <= max_lat and -31 >= min_lat and 18 <= min_lon and 23 >= max_lon:
            provinces_covered.append('Western Cape (partial)')
        if -32 <= max_lat and -28 >= min_lat and 18 <= min_lon and 24 >= max_lon:
            provinces_covered.append('Northern Cape (partial)')
        if -31 <= max_lat and -28 >= min_lat and 23 <= min_lon and 30 >= max_lon:
            provinces_covered.append('Eastern Cape (partial)')
        if -30 <= max_lat and -26 >= min_lat and 24 <= min_lon and 29 >= max_lon:
            provinces_covered.append('Free State (partial)')
        if -27 <= max_lat and -25 >= min_lat and 22 <= min_lon and 27 >= max_lon:
            provinces_covered.append('North West (partial)')
        if -27 <= max_lat and -25 >= min_lat and 27 <= min_lon and 29 >= max_lon:
            provinces_covered.append('Gauteng (partial)')
        if -26 <= max_lat and -24 >= min_lat and 29 <= min_lon and 32 >= max_lon:
            provinces_covered.append('Mpumalanga (partial)')
        if -24 <= max_lat and -22 >= min_lat and 28 <= min_lon and 32 >= max_lon:
            provinces_covered.append('Limpopo (partial)')
        if -30 <= max_lat and -27 >= min_lat and 29 <= min_lon and 33 >= max_lon:
            provinces_covered.append('KwaZulu-Natal (partial)')
    
    for province in provinces_covered:
        print(f'  ✓ {province}')
        
    print('\nProvinces likely NOT covered:')
    all_provinces = ['Western Cape', 'Northern Cape', 'Eastern Cape', 'Free State', 
                    'North West', 'Gauteng', 'Mpumalanga', 'Limpopo', 'KwaZulu-Natal']
    covered = [p.split(' ')[0] for p in provinces_covered]
    for province in all_provinces:
        if province not in covered:
            print(f'  ✗ {province}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
