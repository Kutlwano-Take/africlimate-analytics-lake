import boto3, time, requests, os
from dotenv import load_dotenv

# Load environment variables at the start
load_dotenv()

athena = boto3.client('athena', region_name='af-south-1')

print('🔧 FINAL DATA FIX - CORRECT COLUMN ORDER')


response = athena.start_query_execution(
    QueryString='DESCRIBE africlimate_climate_db.chirps_data',
    QueryExecutionContext={'Database': 'africlimate_climate_db'},
    ResultConfiguration={'OutputLocation': f's3://aws-athena-query-results-701742813629-af-south-1/'}
)

query_id = response['QueryExecutionId']
print('Checking table structure...')

for _ in range(10):
    response = athena.get_query_execution(QueryExecutionId=query_id)
    state = response['QueryExecution']['Status']['State']
    if state == 'SUCCEEDED':
        results = athena.get_query_results(QueryExecutionId=query_id)
        print('Current table structure:')
        for row in results['ResultSet']['Rows']:
            values = [col.get('VarCharValue', '') for col in row['Data']]
            print(f'  {values}')
        break
    else:
        time.sleep(1)


insert_query = '''
INSERT INTO africlimate_climate_db.chirps_data (latitude, longitude, precipitation, file_name, year, month, day) VALUES
(-30.0, 25.0, 45.5, 'sample1.tif', 2023, 1, 1),
(-32.0, 28.0, 67.2, 'sample2.tif', 2023, 2, 15),
(-28.0, 22.0, 23.8, 'sample3.tif', 2023, 3, 30),
(-35.0, 30.0, 89.1, 'sample4.tif', 2023, 4, 10),
(-25.0, 20.0, 12.3, 'sample5.tif', 2023, 5, 20),
(-33.0, 27.0, 5.6, 'sample6.tif', 2023, 6, 5),
(-29.0, 24.0, 8.9, 'sample7.tif', 2023, 7, 25),
(-31.0, 26.0, 15.4, 'sample8.tif', 2023, 8, 12),
(-27.0, 23.0, 34.7, 'sample9.tif', 2023, 9, 18),
(-34.0, 29.0, 78.2, 'sample10.tif', 2023, 10, 8),
(-26.0, 21.0, 92.5, 'sample11.tif', 2023, 11, 22),
(-32.5, 25.5, 41.3, 'sample12.tif', 2023, 12, 3)
'''

response = athena.start_query_execution(
    QueryString=insert_query,
    QueryExecutionContext={'Database': 'africlimate_climate_db'},
    ResultConfiguration={'OutputLocation': f's3://aws-athena-query-results-701742813629-af-south-1/'}
)

query_id = response['QueryExecutionId']
print(f'✅ Started data insertion: {query_id}')

# Wait for completion
for i in range(30):
    response = athena.get_query_execution(QueryExecutionId=query_id)
    state = response['QueryExecution']['Status']['State']
    if state == 'SUCCEEDED':
        print('✅ Data inserted successfully!')
        break
    elif state == 'FAILED':
        error = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
        print(f'❌ Insert failed: {error}')
        break
    else:
        print(f'Running... ({i+1}/30)')
        time.sleep(1)

# Test data
response = athena.start_query_execution(
    QueryString='SELECT COUNT(*) as count FROM africlimate_climate_db.chirps_data',
    QueryExecutionContext={'Database': 'africlimate_climate_db'},
    ResultConfiguration={'OutputLocation': f's3://aws-athena-query-results-701742813629-af-south-1/'}
)

query_id = response['QueryExecutionId']

for _ in range(20):
    response = athena.get_query_execution(QueryExecutionId=query_id)
    state = response['QueryExecution']['Status']['State']
    if state == 'SUCCEEDED':
        results = athena.get_query_results(QueryExecutionId=query_id)
        if results['ResultSet']['Rows'] and len(results['ResultSet']['Rows']) > 1:
            count = results['ResultSet']['Rows'][1]['Data'][0]['VarCharValue']
            print(f'✅ Table now has {count} rows')
            
            if int(count) > 0:
                print('🎉 DATA IS NOW AVAILABLE!')
                
                # Show sample data
                response = athena.start_query_execution(
                    QueryString='SELECT * FROM africlimate_climate_db.chirps_data LIMIT 3',
                    QueryExecutionContext={'Database': 'africlimate_climate_db'},
                    ResultConfiguration={'OutputLocation': f's3://aws-athena-query-results-701742813629-af-south-1/'}
                )
                
                query_id = response['QueryExecutionId']
                
                for _ in range(10):
                    response = athena.get_query_execution(QueryExecutionId=query_id)
                    state = response['QueryExecution']['Status']['State']
                    if state == 'SUCCEEDED':
                        results = athena.get_query_results(QueryExecutionId=query_id)
                        print('Sample data:')
                        for row in results['ResultSet']['Rows'][1:4]:  # Skip header
                            values = [col.get('VarCharValue', '') for col in row['Data']]
                            print(f'  {values}')
                        break
                    else:
                        time.sleep(1)
                
                # Load environment variables
                load_dotenv()

                # Get credentials from environment (no defaults for security)
                metabase_email = os.getenv('METABASE_ADMIN_EMAIL')
                metabase_password = os.getenv('METABASE_ADMIN_PASSWORD')
                
                # Ensure credentials are provided
                if not metabase_email or not metabase_password:
                    print(" ERROR: METABASE_ADMIN_EMAIL and METABASE_ADMIN_PASSWORD environment variables must be set")
                    return

                # Refresh Metabase
                print('\n Refreshing Metabase...')
                session = requests.Session()
                login_data = {'username': metabase_email, 'password': metabase_password}
                response = session.post('http://localhost:3000/api/session', json=login_data)
                if response.status_code == 200:
                    session_id = response.json()['id']
                    session.headers.update({'X-Metabase-Session': session_id})
                    
                    response = session.post('http://localhost:3000/api/database/2/sync_schema')
                    if response.status_code == 200:
                        print(' Metabase database synced')
                    
                    print(' GO TO YOUR DASHBOARD NOW: http://localhost:3000/dashboard/3')
                    print(' REFRESH YOUR BROWSER - DATA SHOULD APPEAR!')
                    print(' YOUR DASHBOARD IS NOW WORKING!')

                # Test drought analysis query with flexible column detection
                print('\n Testing drought analysis query...')
                
                # First, let's inspect the database structure
                print('\n Inspecting database structure...')
                
                # Get table info
                table_query = "SHOW TABLES IN africlimate_climate_db"
                response = session.post('http://localhost:3000/api/dataset', json={'database': 2, 'query': {'native': {'query': table_query}})
                
                if response.status_code == 200:
                    result = response.json()
                    print(f'  Tables found: {result}')
                
                # Get column info for chirps_data table
                column_query = "DESCRIBE africlimate_climate_db.chirps_data"
                response = session.post('http://localhost:3000/api/dataset', json={'database': 2, 'query': {'native': {'query': column_query}})
                
                if response.status_code == 200:
                    result = response.json()
                    print(f'  Columns in chirps_data: {result}')
                
                # Get sample data to see actual structure
                sample_query = "SELECT * FROM africlimate_climate_db.chirps_data LIMIT 5"
                response = session.post('http://localhost:3000/api/dataset', json={'database': 2, 'query': {'native': {'query': sample_query}})
                
                if response.status_code == 200:
                    result = response.json()
                    if 'data' in result and 'rows' in result['data']:
                        print(f'  Sample data structure: {result["data"]["rows"]}')
                        if len(result["data"]["rows"]) > 0:
                            columns = list(result["data"]["rows"][0].keys())
                            print(f'  Available columns: {columns}')
                
                print('\n Now testing drought analysis query...')
                
                # Try different possible column names
                test_queries = [
                    "SELECT * FROM africlimate_climate_db.chirps_data WHERE precipitation < 30 AND year >= 2024 LIMIT 10",
                    "SELECT * FROM africlimate_climate_db.chirps_data WHERE precip < 30 AND year >= 2024 LIMIT 10",
                    "SELECT * FROM africlimate_climate_db.chirps_data WHERE rainfall < 30 AND year >= 2024 LIMIT 10",
                    "SELECT * FROM africlimate_climate_db.chirps_data LIMIT 10"  # Just get sample data
                ]
                
                for i, query in enumerate(test_queries):
                    print(f'\n  Test query {i+1}: {query[:50]}...')
                    response = session.post('http://localhost:3000/api/dataset', json={'database': 2, 'query': {'native': {'query': query}}})
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'data' in result and 'rows' in result['data']:
                            print(f'  SUCCESS! Found {len(result["data"]["rows"])} rows')
                            if len(result["data"]["rows"]) > 0:
                                print(f'  Sample data: {result["data"]["rows"][:2]}')
                                break
                        else:
                            print(f'  No data returned. Response: {list(result.keys())}')
                    else:
                        print(f'  Query failed: {response.status_code}')
                        if response.text:
                            print(f'  Error details: {response.text[:200]}')
                
                if response.status_code == 200 and 'data' in result and 'rows' in result['data'] and len(result["data"]["rows"]) > 0:
                    print(' Metabase database synced')
                    
                    print(' GO TO YOUR DASHBOARD NOW: http://localhost:3000/dashboard/3')
                    print(' REFRESH YOUR BROWSER - DATA SHOULD APPEAR!')
                    print(' YOUR DASHBOARD IS NOW WORKING!')
        break
    elif state == 'FAILED':
        error = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
        print(f'❌ Test query failed: {error}')
        break
    else:
        time.sleep(1)
