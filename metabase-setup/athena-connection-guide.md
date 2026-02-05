# Metabase + Athena Connection Guide

## Step 1: Access Metabase
Open: http://localhost:3000

## Step 2: Create Admin Account
- Email: kutlwano.take@capaciti.org.za
- Name: Kutlwano Take
- Password: [your choice]

## Step 3: Add Athena Database
1. Click "Add Database" 
2. Select "Athena" from the list
3. Configure connection:

### Connection Details:
- **Display name**: Climate Analytics Athena
- **Catalog**: `AwsDataCatalog`
- **Workgroup**: `primary`
- **Database**: `africlimate_climate_db`
- **S3 Staging Directory**: `s3://africlimate-analytics-lake/athena-results/`
- **Region**: `af-south-1`

### Authentication:
- Use your AWS credentials
- Access Key: [your AWS access key]
- Secret Key: [your AWS secret key]

## Step 4: Test Connection
Click "Save" and wait for connection test

## Step 5: Explore Data
Once connected, you'll see your CHIRPS climate tables:
- `chirps_data` - Main precipitation data
- `chirps_processed` - Cleaned data
- Any other tables created by your Glue crawler

## Ready for Dashboard Creation!
After successful connection, you can start creating climate dashboards.
