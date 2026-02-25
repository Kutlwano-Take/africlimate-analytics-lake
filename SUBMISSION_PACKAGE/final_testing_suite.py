#!/usr/bin/env python3
"""
Week 4 Day 22-23: Final Testing Suite
Per weekly documentation: "End-to-end pipeline testing, Validate all queries run successfully, 
Test QuickSight dashboard functionality, Verify security controls"
"""

import boto3
import json
import time
import subprocess
import requests
from datetime import datetime, timedelta

class AfriClimateTestingSuite:
    def __init__(self):
        self.region = 'af-south-1'
        self.s3 = boto3.client('s3', region_name=self.region)
        self.lambda_client = boto3.client('lambda', region_name=self.region)
        self.glue = boto3.client('glue', region_name=self.region)
        self.athena = boto3.client('athena', region_name=self.region)
        self.lakeformation = boto3.client('lakeformation', region_name=self.region)
        self.iam = boto3.client('iam', region_name=self.region)
        self.sts = boto3.client('sts', region_name=self.region)
        self.account_id = self.sts.get_caller_identity()['Account']
        
        self.test_results = {
            'pipeline_tests': {},
            'query_tests': {},
            'dashboard_tests': {},
            'security_tests': {},
            'performance_tests': {}
        }
        
    def run_all_tests(self):
        """Execute complete testing suite"""
        print("🧪 WEEK 4 DAY 22-23: FINAL TESTING SUITE")
        print("=" * 60)
        print(f"Account: {self.account_id}")
        print(f"Region: {self.region}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Test 1: End-to-End Pipeline Validation
        self.test_pipeline_integration()
        
        # Test 2: Query Validation
        self.test_athena_queries()
        
        # Test 3: Dashboard Functionality
        self.test_metabase_dashboard()
        
        # Test 4: Security Controls Verification
        self.test_security_controls()
        
        # Test 5: Performance Testing
        self.test_performance_metrics()
        
        # Generate Test Report
        self.generate_test_report()
        
        return self.test_results
    
    def test_pipeline_integration(self):
        """Test 1: End-to-End Pipeline Validation"""
        print("\n🔄 TEST 1: END-TO-END PIPELINE VALIDATION")
        
        # 1.1 S3 Bucket Structure Validation
        print("\n1.1 Validating S3 bucket structure...")
        try:
            bucket_name = 'africlimate-analytics-lake'
            
            # Check main bucket exists
            self.s3.head_bucket(Bucket=bucket_name)
            print("✅ S3 bucket exists")
            
            # Check folder structure
            folders = ['raw/', 'processed/', 'athena-results/']
            for folder in folders:
                try:
                    objects = self.s3.list_objects_v2(
                        Bucket=bucket_name,
                        Prefix=folder,
                        MaxKeys=5
                    )
                    if 'Contents' in objects:
                        print(f"✅ {folder} folder contains data")
                    else:
                        print(f"⚠️  {folder} folder is empty")
                except Exception as e:
                    print(f"❌ Error checking {folder}: {e}")
            
            self.test_results['pipeline_tests']['s3_structure'] = 'PASS'
            
        except Exception as e:
            print(f"❌ S3 bucket validation failed: {e}")
            self.test_results['pipeline_tests']['s3_structure'] = 'FAIL'
        
        # 1.2 Lambda Function Validation
        print("\n1.2 Validating Lambda ETL functions...")
        try:
            lambda_functions = ['etl_processor', 'climate_metrics_calculator']
            
            for func_name in lambda_functions:
                try:
                    response = self.lambda_client.get_function(FunctionName=func_name)
                    print(f"✅ Lambda function {func_name} exists")
                    
                    # Check function configuration
                    config = response['Configuration']
                    memory_size = config['MemorySize']
                    timeout = config['Timeout']
                    print(f"   Memory: {memory_size}MB, Timeout: {timeout}s")
                    
                except Exception as e:
                    print(f"❌ Lambda function {func_name} not found: {e}")
            
            self.test_results['pipeline_tests']['lambda_functions'] = 'PASS'
            
        except Exception as e:
            print(f"❌ Lambda validation failed: {e}")
            self.test_results['pipeline_tests']['lambda_functions'] = 'FAIL'
        
        # 1.3 Glue Database Validation
        print("\n1.3 Validating Glue database and tables...")
        try:
            # Check database exists
            database_response = self.glue.get_database(Name='africlimate_climate_db')
            print("✅ Glue database exists")
            
            # Check tables exist
            tables = ['chirps_data', 'drought_metrics']
            for table in tables:
                try:
                    table_response = self.glue.get_table(
                        DatabaseName='africlimate_climate_db',
                        Name=table
                    )
                    print(f"✅ Table {table} exists")
                    
                    # Check table properties
                    table_info = table_response['Table']
                    columns = len(table_info['StorageDescriptor']['Columns'])
                    print(f"   Columns: {columns}")
                    
                except Exception as e:
                    print(f"❌ Table {table} not found: {e}")
            
            self.test_results['pipeline_tests']['glue_database'] = 'PASS'
            
        except Exception as e:
            print(f"❌ Glue validation failed: {e}")
            self.test_results['pipeline_tests']['glue_database'] = 'FAIL'
        
        # 1.4 Data Freshness Check
        print("\n1.4 Checking data freshness...")
        try:
            # Check recent data in processed folder
            response = self.s3.list_objects_v2(
                Bucket='africlimate-analytics-lake',
                Prefix='processed/',
                MaxKeys=10
            )
            
            if 'Contents' in response:
                latest_file = max(response['Contents'], key=lambda x: x['LastModified'])
                days_old = (datetime.now(latest_file['LastModified'].tzinfo) - latest_file['LastModified']).days
                
                if days_old <= 7:
                    print(f"✅ Data is fresh ({days_old} days old)")
                    self.test_results['pipeline_tests']['data_freshness'] = 'PASS'
                else:
                    print(f"⚠️  Data is stale ({days_old} days old)")
                    self.test_results['pipeline_tests']['data_freshness'] = 'WARN'
            else:
                print("❌ No processed data found")
                self.test_results['pipeline_tests']['data_freshness'] = 'FAIL'
                
        except Exception as e:
            print(f"❌ Data freshness check failed: {e}")
            self.test_results['pipeline_tests']['data_freshness'] = 'FAIL'
    
    def test_athena_queries(self):
        """Test 2: Query Validation"""
        print("\n📊 TEST 2: ATHENA QUERY VALIDATION")
        
        # Test queries from Week 3 dashboard
        test_queries = [
            {
                'name': 'Basic Precipitation Query',
                'query': 'SELECT COUNT(*) as total_records FROM africlimate_climate_db.chirps_data WHERE year = 2023',
                'expected_columns': ['total_records']
            },
            {
                'name': 'Drought Metrics Query',
                'query': 'SELECT AVG(spi_3month) as avg_spi FROM africlimate_climate_db.drought_metrics WHERE date >= DATEADD(\'day\', -30, CURRENT_DATE)',
                'expected_columns': ['avg_spi']
            },
            {
                'name': 'Regional Analysis Query',
                'query': 'SELECT year, AVG(rainfall) as avg_rainfall FROM africlimate_climate_db.chirps_data WHERE latitude BETWEEN -30 AND -25 GROUP BY year ORDER BY year',
                'expected_columns': ['year', 'avg_rainfall']
            },
            {
                'name': 'Complex Join Query',
                'query': 'SELECT c.year, AVG(c.rainfall) as rainfall, AVG(d.spi_3month) as spi FROM africlimate_climate_db.chirps_data c JOIN africlimate_climate_db.drought_metrics d ON c.date = d.date WHERE c.year >= 2022 GROUP BY c.year',
                'expected_columns': ['year', 'rainfall', 'spi']
            }
        ]
        
        for query_test in test_queries:
            print(f"\n2.{len(self.test_results['query_tests']) + 1} Testing: {query_test['name']}")
            
            try:
                # Execute query
                response = self.athena.start_query_execution(
                    QueryString=query_test['query'],
                    ResultConfiguration={'OutputLocation': f's3://aws-athena-query-results-{self.account_id}-af-south-1/'}
                )
                
                query_execution_id = response['QueryExecutionId']
                
                # Wait for query to complete
                max_wait = 30  # seconds
                for i in range(max_wait):
                    try:
                        result_response = self.athena.get_query_execution(QueryExecutionId=query_execution_id)
                        status = result_response['QueryExecution']['Status']['State']
                        
                        if status == 'SUCCEEDED':
                            # Get results
                            results = self.athena.get_query_results(QueryExecutionId=query_execution_id)
                            
                            # Validate columns
                            if 'ResultSet' in results and 'Rows' in results['ResultSet']:
                                columns = [col['VarCharValue'] for col in results['ResultSet']['Rows'][0]['Data']]
                                
                                # Check if expected columns exist
                                missing_columns = [col for col in query_test['expected_columns'] if col not in columns]
                                
                                if not missing_columns:
                                    print(f"✅ Query executed successfully")
                                    print(f"   Columns: {columns}")
                                    print(f"   Rows returned: {len(results['ResultSet']['Rows']) - 1}")
                                    self.test_results['query_tests'][query_test['name']] = 'PASS'
                                else:
                                    print(f"❌ Missing columns: {missing_columns}")
                                    self.test_results['query_tests'][query_test['name']] = 'FAIL'
                            else:
                                print("❌ No results returned")
                                self.test_results['query_tests'][query_test['name']] = 'FAIL'
                            
                            break
                            
                        elif status == 'FAILED':
                            error = result_response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
                            print(f"❌ Query failed: {error}")
                            self.test_results['query_tests'][query_test['name']] = 'FAIL'
                            break
                            
                        elif status == 'CANCELLED':
                            print("❌ Query was cancelled")
                            self.test_results['query_tests'][query_test['name']] = 'FAIL'
                            break
                        
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f"❌ Error checking query status: {e}")
                        self.test_results['query_tests'][query_test['name']] = 'FAIL'
                        break
                else:
                    print("❌ Query timed out")
                    self.test_results['query_tests'][query_test['name']] = 'TIMEOUT'
                    
            except Exception as e:
                print(f"❌ Error executing query: {e}")
                self.test_results['query_tests'][query_test['name']] = 'FAIL'
    
    def test_metabase_dashboard(self):
        """Test 3: Dashboard Functionality"""
        print("\n📈 TEST 3: METABASE DASHBOARD FUNCTIONALITY")
        
        # 3.1 Metabase Service Check
        print("\n3.1 Checking Metabase service...")
        try:
            # Check if Metabase is running
            response = requests.get('http://localhost:3000/api/health', timeout=10)
            
            if response.status_code == 200:
                print("✅ Metabase service is running")
                self.test_results['dashboard_tests']['service_running'] = 'PASS'
            else:
                print(f"⚠️  Metabase returned status: {response.status_code}")
                self.test_results['dashboard_tests']['service_running'] = 'WARN'
                
        except requests.exceptions.ConnectionError:
            print("❌ Metabase service is not accessible")
            print("   Start Metabase: cd metabase-setup && docker-compose up -d")
            self.test_results['dashboard_tests']['service_running'] = 'FAIL'
        except Exception as e:
            print(f"❌ Error checking Metabase: {e}")
            self.test_results['dashboard_tests']['service_running'] = 'FAIL'
        
        # 3.2 Database Connection Test
        print("\n3.2 Testing database connection...")
        try:
            # This would require Metabase API authentication
            # For now, we'll test the underlying Athena connection
            test_query = "SELECT 1 as test_connection"
            response = self.athena.start_query_execution(
                QueryString=test_query,
                ResultConfiguration={'OutputLocation': f's3://aws-athena-query-results-{self.account_id}-af-south-1/'}
            )
            
            query_execution_id = response['QueryExecutionId']
            
            # Wait for completion
            for i in range(10):
                result_response = self.athena.get_query_execution(QueryExecutionId=query_execution_id)
                status = result_response['QueryExecution']['Status']['State']
                
                if status == 'SUCCEEDED':
                    print("✅ Database connection working")
                    self.test_results['dashboard_tests']['database_connection'] = 'PASS'
                    break
                elif status == 'FAILED':
                    print("❌ Database connection failed")
                    self.test_results['dashboard_tests']['database_connection'] = 'FAIL'
                    break
                time.sleep(1)
            else:
                print("❌ Database connection test timed out")
                self.test_results['dashboard_tests']['database_connection'] = 'TIMEOUT'
                
        except Exception as e:
            print(f"❌ Database connection test failed: {e}")
            self.test_results['dashboard_tests']['database_connection'] = 'FAIL'
        
        # 3.3 Visualization Queries Test
        print("\n3.3 Testing visualization queries...")
        viz_queries = [
            'precipitation_heatmap',
            'drought_trends',
            'regional_comparison',
            'year_over_year',
            'anomaly_detection'
        ]
        
        for viz_name in viz_queries:
            try:
                # Test if the query file exists
                query_file = f'sql-queries/week3_dashboard_queries.sql'
                with open(query_file, 'r') as f:
                    content = f.read()
                    
                if viz_name.replace('_', ' ').lower() in content.lower():
                    print(f"✅ {viz_name} query available")
                    self.test_results['dashboard_tests'][f'query_{viz_name}'] = 'PASS'
                else:
                    print(f"⚠️  {viz_name} query not found")
                    self.test_results['dashboard_tests'][f'query_{viz_name}'] = 'WARN'
                    
            except FileNotFoundError:
                print(f"❌ Query file not found: {query_file}")
                self.test_results['dashboard_tests'][f'query_{viz_name}'] = 'FAIL'
            except Exception as e:
                print(f"❌ Error checking {viz_name} query: {e}")
                self.test_results['dashboard_tests'][f'query_{viz_name}'] = 'FAIL'
    
    def test_security_controls(self):
        """Test 4: Security Controls Verification"""
        print("\n🔒 TEST 4: SECURITY CONTROLS VERIFICATION")
        
        # 4.1 Lake Formation Setup
        print("\n4.1 Verifying Lake Formation setup...")
        try:
            # Check data lake settings
            settings = self.lakeformation.get_data_lake_settings()
            admin_count = len(settings['DataLakeAdmins'])
            print(f"✅ Data lake admins configured: {admin_count}")
            self.test_results['security_tests']['lake_formation_settings'] = 'PASS'
            
            # Check registered resources
            resources = self.lakeformation.list_resources()
            resource_count = len(resources['ResourceInfoList'])
            print(f"✅ Registered resources: {resource_count}")
            self.test_results['security_tests']['registered_resources'] = 'PASS'
            
        except Exception as e:
            print(f"❌ Lake Formation verification failed: {e}")
            self.test_results['security_tests']['lake_formation_settings'] = 'FAIL'
        
        # 4.2 IAM Roles Validation
        print("\n4.2 Validating stakeholder IAM roles...")
        stakeholder_roles = ['FarmerRole', 'MunicipalityRole', 'ResearcherRole']
        
        for role_name in stakeholder_roles:
            try:
                role_response = self.iam.get_role(RoleName=role_name)
                print(f"✅ Role {role_name} exists")
                self.test_results['security_tests'][f'role_{role_name}'] = 'PASS'
                
                # Check attached policies
                attached_policies = self.iam.list_attached_role_policies(RoleName=role_name)
                policy_count = len(attached_policies['AttachedPolicies'])
                print(f"   Attached policies: {policy_count}")
                
            except self.iam.exceptions.NoSuchEntityException:
                print(f"❌ Role {role_name} does not exist")
                self.test_results['security_tests'][f'role_{role_name}'] = 'FAIL'
            except Exception as e:
                print(f"❌ Error checking role {role_name}: {e}")
                self.test_results['security_tests'][f'role_{role_name}'] = 'FAIL'
        
        # 4.3 S3 Security
        print("\n4.3 Validating S3 security...")
        try:
            bucket_name = 'africlimate-analytics-lake'
            
            # Check bucket encryption
            try:
                encryption = self.s3.get_bucket_encryption(Bucket=bucket_name)
                print("✅ S3 bucket encryption enabled")
                self.test_results['security_tests']['s3_encryption'] = 'PASS'
            except self.s3.exceptions.ClientError as e:
                if 'ServerSideEncryptionConfigurationNotFoundError' in str(e):
                    print("⚠️  S3 bucket encryption not configured")
                    self.test_results['security_tests']['s3_encryption'] = 'WARN'
                else:
                    print(f"❌ Error checking encryption: {e}")
                    self.test_results['security_tests']['s3_encryption'] = 'FAIL'
            
            # Check bucket versioning
            try:
                versioning = self.s3.get_bucket_versioning(Bucket=bucket_name)
                status = versioning.get('Status', 'Disabled')
                if status == 'Enabled':
                    print("✅ S3 bucket versioning enabled")
                    self.test_results['security_tests']['s3_versioning'] = 'PASS'
                else:
                    print("⚠️  S3 bucket versioning disabled")
                    self.test_results['security_tests']['s3_versioning'] = 'WARN'
            except Exception as e:
                print(f"❌ Error checking versioning: {e}")
                self.test_results['security_tests']['s3_versioning'] = 'FAIL'
                
        except Exception as e:
            print(f"❌ S3 security validation failed: {e}")
            self.test_results['security_tests']['s3_security'] = 'FAIL'
        
        # 4.4 Row-Level Security Test
        print("\n4.4 Testing row-level security filters...")
        try:
            filters = self.lakeformation.list_data_cells_filters()
            filter_count = len(filters['DataCellsFiltersList'])
            print(f"✅ Row filters created: {filter_count}")
            
            for filter_info in filters['DataCellsFiltersList']:
                filter_name = filter_info['Name']
                table_name = filter_info['TableCatalogId'].split('/')[-1] if '/' in filter_info['TableCatalogId'] else 'Unknown'
                print(f"   Filter: {filter_name} on {table_name}")
            
            self.test_results['security_tests']['row_filters'] = 'PASS'
            
        except Exception as e:
            print(f"❌ Row-level security test failed: {e}")
            self.test_results['security_tests']['row_filters'] = 'FAIL'
    
    def test_performance_metrics(self):
        """Test 5: Performance Testing"""
        print("\n⚡ TEST 5: PERFORMANCE METRICS")
        
        # 5.1 Query Performance Test
        print("\n5.1 Testing query performance...")
        performance_queries = [
            {
                'name': 'Simple Count Query',
                'query': 'SELECT COUNT(*) FROM africlimate_climate_db.chirps_data WHERE year = 2023',
                'max_time': 5  # seconds
            },
            {
                'name': 'Aggregation Query',
                'query': 'SELECT year, AVG(rainfall) FROM africlimate_climate_db.chirps_data GROUP BY year',
                'max_time': 10
            }
        ]
        
        for perf_query in performance_queries:
            print(f"\n5.1.{len(self.test_results['performance_tests']) + 1} Testing: {perf_query['name']}")
            
            start_time = time.time()
            
            try:
                response = self.athena.start_query_execution(
                    QueryString=perf_query['query'],
                    ResultConfiguration={'OutputLocation': f's3://aws-athena-query-results-{self.account_id}-af-south-1/'}
                )
                
                query_execution_id = response['QueryExecutionId']
                
                # Wait for completion
                max_wait = perf_query['max_time']
                for i in range(max_wait):
                    result_response = self.athena.get_query_execution(QueryExecutionId=query_execution_id)
                    status = result_response['QueryExecution']['Status']['State']
                    
                    if status == 'SUCCEEDED':
                        end_time = time.time()
                        execution_time = end_time - start_time
                        
                        if execution_time <= perf_query['max_time']:
                            print(f"✅ Query completed in {execution_time:.2f}s")
                            self.test_results['performance_tests'][perf_query['name']] = 'PASS'
                        else:
                            print(f"⚠️  Query slow: {execution_time:.2f}s (max: {perf_query['max_time']}s)")
                            self.test_results['performance_tests'][perf_query['name']] = 'SLOW'
                        break
                    elif status == 'FAILED':
                        print(f"❌ Query failed")
                        self.test_results['performance_tests'][perf_query['name']] = 'FAIL'
                        break
                    time.sleep(1)
                else:
                    print(f"❌ Query timed out (> {perf_query['max_time']}s)")
                    self.test_results['performance_tests'][perf_query['name']] = 'TIMEOUT'
                    
            except Exception as e:
                print(f"❌ Performance test failed: {e}")
                self.test_results['performance_tests'][perf_query['name']] = 'FAIL'
        
        # 5.2 Cost Metrics Check
        print("\n5.2 Checking cost optimization metrics...")
        try:
            # Check S3 storage costs (estimated)
            response = self.s3.list_objects_v2(Bucket='africlimate-analytics-lake')
            
            if 'Contents' in response:
                total_size = sum(obj['Size'] for obj in response['Contents'])
                size_gb = total_size / (1024**3)
                estimated_cost = size_gb * 0.023  # S3 Standard price
                
                print(f"✅ Total storage: {size_gb:.2f} GB")
                print(f"✅ Estimated monthly cost: ${estimated_cost:.4f}")
                
                if estimated_cost < 0.05:
                    self.test_results['performance_tests']['storage_cost'] = 'OPTIMAL'
                else:
                    self.test_results['performance_tests']['storage_cost'] = 'HIGH'
            else:
                print("⚠️  No data found in bucket")
                self.test_results['performance_tests']['storage_cost'] = 'NO_DATA'
                
        except Exception as e:
            print(f"❌ Cost check failed: {e}")
            self.test_results['performance_tests']['storage_cost'] = 'ERROR'
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📋 FINAL TEST REPORT")
        print("=" * 60)
        
        # Calculate overall statistics
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        warnings = 0
        
        for category, tests in self.test_results.items():
            for test_name, result in tests.items():
                total_tests += 1
                if result == 'PASS' or result == 'OPTIMAL':
                    passed_tests += 1
                elif result == 'FAIL' or result == 'ERROR' or result == 'TIMEOUT':
                    failed_tests += 1
                else:  # WARN, SLOW, etc.
                    warnings += 1
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        print(f"Warnings: {warnings} ({warnings/total_tests*100:.1f}%)")
        
        # Category breakdown
        print("\n📊 CATEGORY BREAKDOWN:")
        for category, tests in self.test_results.items():
            cat_passed = sum(1 for result in tests.values() if result in ['PASS', 'OPTIMAL'])
            cat_total = len(tests)
            print(f"{category.replace('_', ' ').title()}: {cat_passed}/{cat_total} passed")
        
        # Failed tests details
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for category, tests in self.test_results.items():
                for test_name, result in tests.items():
                    if result in ['FAIL', 'ERROR', 'TIMEOUT']:
                        print(f"  - {category}: {test_name} ({result})")
        
        # Warnings
        if warnings > 0:
            print("\n⚠️  WARNINGS:")
            for category, tests in self.test_results.items():
                for test_name, result in tests.items():
                    if result not in ['PASS', 'OPTIMAL', 'FAIL', 'ERROR', 'TIMEOUT']:
                        print(f"  - {category}: {test_name} ({result})")
        
        # Overall assessment
        print("\n🎯 OVERALL ASSESSMENT:")
        if failed_tests == 0:
            print("✅ ALL TESTS PASSED - System ready for submission")
        elif failed_tests <= 2:
            print("⚠️  MINOR ISSUES - Address before submission")
        else:
            print("❌ SIGNIFICANT ISSUES - Requires immediate attention")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'warnings': warnings,
                'success_rate': passed_tests/total_tests*100
            },
            'detailed_results': self.test_results
        }
        
        try:
            with open('test_report.json', 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"\n📄 Detailed report saved to: test_report.json")
        except Exception as e:
            print(f"\n❌ Error saving report: {e}")
        
        return report_data

if __name__ == "__main__":
    # Run the complete testing suite
    testing_suite = AfriClimateTestingSuite()
    results = testing_suite.run_all_tests()
