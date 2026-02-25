import boto3
import json
import time

def check_glue_crawler_status():
    """Check the status of the Glue crawler"""
    glue_client = boto3.client('glue', region_name='af-south-1')
    
    try:
        response = glue_client.get_crawler(Name='chirps-crawler')
        status = response['Crawler']['State']
        print(f"Crawler Status: {status}")
        
        if 'LastCrawl' in response['Crawler']:
            last_crawl = response['Crawler']['LastCrawl']
            print(f"Last Crawl Status: {last_crawl.get('Status', 'N/A')}")
            print(f"Last Crawl Time: {last_crawl.get('StartTime', 'N/A')}")
            print(f"Log Group: {last_crawl.get('LogGroup', 'N/A')}")
        
        return status
    except Exception as e:
        print(f"Error checking crawler status: {e}")
        return None

def list_glue_tables():
    """List tables in the Glue database"""
    glue_client = boto3.client('glue', region_name='af-south-1')
    
    try:
        response = glue_client.get_tables(DatabaseName='africlimate_climate_db')
        tables = response.get('TableList', [])
        
        print(f"\nFound {len(tables)} tables:")
        for table in tables:
            print(f"- {table['Name']}")
            print(f"  Location: {table['StorageDescriptor']['Location']}")
            print(f"  Columns: {len(table['StorageDescriptor']['Columns'])}")
            if 'PartitionKeys' in table:
                print(f"  Partitions: {len(table['PartitionKeys'])}")
            print()
        
        return tables
    except Exception as e:
        print(f"Error listing tables: {e}")
        return []

if __name__ == "__main__":
    print("Checking Glue Crawler Status...")
    status = check_glue_crawler_status()
    
    if status == "READY":
        print("\nCrawler is ready. Listing tables...")
        tables = list_glue_tables()
    else:
        print(f"\nCrawler is {status}. Please wait for it to complete.")
