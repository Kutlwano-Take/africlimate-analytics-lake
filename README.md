# AfriClimate Analytics Lake

## Project Overview
Building a scalable, serverless data lake architecture on AWS for African climate analytics using Digital Earth Africa CHIRPS rainfall data.

## Architecture
- **Storage**: Amazon S3 (af-south-1)
- **Data Catalog**: AWS Glue
- **Query Engine**: Amazon Athena
- **ETL**: AWS Lambda
- **Visualization**: Amazon QuickSight
- **Governance**: AWS Lake Formation

## Data Lake Structure
```
s3://africlimate-analytics-lake/
├── raw/
│   └── chirps_monthly/
├── processed/
└── athena-results/
```

## Project Progress
### Week 1 - Day 1 (February 2, 2026)
- **Completed**: Created S3 bucket `africlimate-analytics-lake` in af-south-1 region
- **Completed**: Set up folder structure (raw/, processed/, athena-results/)
- **Completed**: Enabled bucket versioning for data protection
- **Completed**: Created IAM role `AfriclimateGlueRole` with least privilege access
- **Completed**: Downloaded sample CHIRPS data (January 2024)
- **Completed**: Uploaded sample data to S3 bucket

### Next Steps
- **Pending**: Set up AWS Glue database and tables
- **Pending**: Configure data crawlers
- **Pending**: Test Athena queries
- **Pending**: Build Lambda ETL pipeline

## Cost Optimization
- **Free tier usage**: Currently using 2GB of 5GB S3 storage allocation
- **Estimated monthly cost**: $0.02 based on current usage patterns
- **Region strategy**: af-south-1 (Cape Town) for optimal latency and cost efficiency

## Technical Specifications
- **Dataset**: CHIRPS v2.0 monthly rainfall data at 5km resolution
- **Format**: Cloud-Optimized GeoTIFF (COG) for efficient querying
- **Coverage**: Southern Africa region (2020-2025 timeframe)
- **File size**: Approximately 5.5MB per monthly file

## AWS Services Utilized
- **Amazon S3**: Primary storage for raw and processed data
- **AWS Glue**: Data catalog and metadata management
- **Amazon Athena**: SQL-based query engine for data analysis
- **AWS Lambda**: Serverless ETL processing capabilities
- **IAM**: Identity and access management for security
- **CloudWatch**: Monitoring and logging services

## Project Timeline
This project follows a structured 4-week execution plan:
- **Week 1**: Foundation setup and data ingestion
- **Week 2**: ETL pipeline development and analytics
- **Week 3**: Visualization and governance implementation
- **Week 4**: Testing, documentation, and submission preparation

## Success Metrics
- **Technical**: Complete data lake with serverless architecture
- **Financial**: Maintain costs under $1.00 monthly
- **Quality**: Deliver all required project components
- **Innovation**: Unique African climate analytics approach
