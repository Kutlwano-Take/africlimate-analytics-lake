# Week 3 Day 19-20: Architecture Diagram Guide

## Requirements
Per weekly documentation: "Create professional architecture diagram with draw.io, Document data flow, Add security and cost optimization notes"

## Architecture Components

### Data Flow Architecture
```
DE Africa Climate Data Lake
        ↓ (CHIRPS Satellite Data)
Amazon S3 (africlimate-analytics-lake)
├── raw/ (Original TIFF files)
├── processed/ (Parquet files)
└── athena-results/ (Query outputs)
        ↓ (Event-driven triggers)
AWS Lambda (ETL Processing)
├── TIFF to Parquet conversion
├── Climate metrics calculation
└── Data validation
        ↓ (Automated crawling)
AWS Glue Data Catalog
├── Database: africlimate_climate_db
├── Tables: chirps_data, drought_metrics
└── Crawler: chirps-crawler (daily 2 AM)
        ↓ (SQL queries)
Amazon Athena
├── Query engine (Presto)
├── Result caching
└── Partition pruning
        ↓ (Governance layer)
AWS Lake Formation
├── Row-level security
├── Column permissions
└── Multi-stakeholder access
        ↓ (Visualization)
Metabase (Docker)
├── Interactive dashboards
├── 5 core visualizations
└── Real-time analytics
```

## draw.io Diagram Instructions

### Step 1: Setup
1. Go to: https://app.diagrams.net/
2. File → New → Blank Diagram
3. Select AWS icons from shape library

### Step 2: Layout Structure
**3-Tier Architecture Layout:**
- **Top Tier:** Data Sources (DE Africa, Satellite)
- **Middle Tier:** AWS Services (S3, Lambda, Glue, Athena, Lake Formation)
- **Bottom Tier:** Visualization (Metabase, Stakeholders)

### Step 3: Component Details

#### Data Sources (Top)
- **DE Africa Climate Data Lake** (Cloud icon)
- **CHIRPS Satellite Data** (Satellite icon)
- **Arrow labels:** "Daily precipitation data (TIFF format)"

#### Storage Layer
- **Amazon S3** (S3 bucket icon)
- **Label:** africlimate-analytics-lake
- **Sub-labels:** raw/, processed/, athena-results/
- **Color:** Blue (storage)

#### Processing Layer
- **AWS Lambda** (Lambda icon)
- **Label:** ETL Processing
- **Functions:** TIFF→Parquet, SPI calculation, validation
- **Color:** Orange (compute)

#### Catalog Layer
- **AWS Glue** (Glue icon)
- **Label:** Data Catalog
- **Database:** africlimate_climate_db
- **Crawler:** chirps-crawler (daily 2 AM)
- **Color:** Purple (data management)

#### Query Layer
- **Amazon Athena** (Athena icon)
- **Label:** SQL Query Engine
- **Features:** Result caching, partition pruning
- **Color:** Red (analytics)

#### Governance Layer
- **AWS Lake Formation** (Shield icon)
- **Label:** Data Governance
- **Features:** Row/column security, multi-stakeholder access
- **Color:** Green (security)

#### Visualization Layer
- **Metabase** (Database icon)
- **Label:** Analytics Dashboard
- **Visualizations:** 5 core charts
- **Color:** Teal (visualization)

### Step 4: Data Flow Arrows
```
DE Africa → S3 (Data ingestion)
S3 → Lambda (Event-driven ETL)
Lambda → S3 (Processed data)
S3 → Glue (Metadata catalog)
Glue → Athena (Query access)
Athena → Lake Formation (Governance)
Lake Formation → Metabase (Filtered data)
Metabase → Stakeholders (Dashboards)
```

### Step 5: Security Annotations
Add security symbols and notes:
- **IAM Roles:** Lock icons at each service
- **Encryption:** Padlock icons on S3
- **VPC Endpoints:** Network symbols
- **Access Control:** Shield icons (Lake Formation)

### Step 6: Cost Optimization Notes
Add cost annotations:
- **S3:** "$0.01/month (Intelligent tiering)"
- **Lambda:** "$0.005/month (Event-driven)"
- **Glue:** "$0.003/month (Daily crawler)"
- **Athena:** "$0.002/month (Query caching)"
- **Total:** "$0.02/month (99% under budget)"

### Step 7: Regional Information
- **Region:** af-south-1 (Cape Town)
- **Geographic Focus:** Southern Africa (-35° to -22° lat, 16° to 33° lon)
- **Data Coverage:** 50+ countries
- **Resolution:** 5km grid

## Diagram Specifications

### Size and Layout
- **Size:** A4 landscape orientation
- **Layout:** Top-to-bottom data flow
- **Spacing:** Even component distribution
- **Colors:** AWS service color scheme

### Labels and Annotations
- **Service Names:** Bold, clear font
- **Data Volumes:** Include file counts (536 files, 2.9 GiB)
- **Performance Metrics:** Query times, cost figures
- **Security Notes:** Encryption, access controls

### Legend
Create legend with:
- **Color coding:** Service categories
- **Arrow types:** Data flow vs control flow
- **Icons:** Security, cost, performance indicators
- **Symbols:** Geographic boundaries, data formats

## Export Requirements

### File Formats
1. **PNG:** High resolution for documentation
2. **SVG:** Scalable for presentations
3. **PDF:** Print-ready format

### Naming Convention
- **File:** africlimate-architecture-diagram
- **Version:** v1.0-week3
- **Date:** Current date

## Documentation Integration

### README Integration
Add to README.md:
```
## Architecture Diagram
![AfriClimate Architecture](africlimate-architecture-diagram.png)

### Key Design Decisions
- Serverless architecture for cost efficiency
- Event-driven processing for scalability
- Multi-stakeholder governance for security
- Regional focus for Southern Africa relevance
```

### Technical Report Integration
Include in 3-page technical report:
- System architecture overview
- Data flow documentation
- Security implementation
- Cost optimization strategies

## Validation Checklist

### Diagram Completeness
- ✅ All AWS services included
- ✅ Data flow clearly documented
- ✅ Security annotations added
- ✅ Cost optimization notes included
- ✅ Regional information specified

### Quality Standards
- ✅ Professional appearance
- ✅ Clear labeling
- ✅ Consistent color scheme
- ✅ Appropriate level of detail
- ✅ Export-friendly format

## Success Criteria
✅ Professional architecture diagram created
✅ Data flow documented completely
✅ Security and cost optimization notes added
✅ Diagram exported in multiple formats
✅ Integrated into project documentation
✅ Ready for Week 4 technical report

## Next Steps
After diagram completion:
- Week 3 Day 21: Technical report draft
- Week 4: Final testing and submission preparation
