"""
Script to load CSV data into database
"""
import sys
import pandas as pd
import json
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import Base
from app.models.client_features import ClientFeatures, FEATURE_COLS, ID_COL, CAT_FEATURES
from app.models.feature_descriptions import FeatureDescription

# Database connection
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def normalize_value(value, col_name):
    """Normalize value based on column type"""
    if pd.isna(value) or value == 'nan' or value == 'None' or value == '':
        return None
    
    # String columns - return as is (already decoded from windows-1251 to UTF-8)
    if col_name in CAT_FEATURES:
        return str(value) if value is not None else None
    
    # Boolean flags
    if col_name.endswith('_flag'):
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'да')
        return None
    
    # Integer columns
    if col_name in ['age', 'loan_cnt', 'other_credits_count', 'mob_cnt_days', 
                    'mob_cover_days', 'dp_ils_days_from_last_doc', 
                    'days_to_last_transaction', 'days_after_last_request',
                    'hdb_bki_total_products', 'hdb_bki_total_cnt',
                    'bki_total_auto_cnt', 'bki_total_oth_cnt', 'bki_total_products',
                    'bki_total_active_products', 'hdb_bki_total_active_products',
                    'hdb_bki_total_micro_cnt', 'hdb_bki_active_pil_cnt',
                    'hdb_bki_total_pil_cnt', 'hdb_bki_total_ip_cnt',
                    'winback_cnt', 'mob_total_sessions',
                    'hdb_bki_total_pil_last_days', 'hdb_bki_last_product_days',
                    'dp_ils_total_seniority', 'dp_ils_days_multiple_job_cnt_5y',
                    'dp_ils_employeers_cnt_last_month', 'dp_ils_uniq_companies_1y',
                    'dp_address_unique_regions', 'bki_active_auto_cnt',
                    'dp_ils_cnt_changes_1y', 'dp_ils_avg_simultanious_jobs_5y',
                    'transaction_category_supermarket_percent_cnt_2m',
                    'transaction_category_supermarket_sum_cnt_m2',
                    'transaction_category_supermarket_sum_cnt_m3_4',
                    'transaction_category_supermarket_sum_cnt_d15',
                    'transaction_category_supermarket_inc_cnt_2m',
                    'transaction_category_restaurants_percent_cnt_2m',
                    'transaction_category_restaurants_percent_amt_2m',
                    'transaction_category_fastfood_percent_cnt_2m',
                    'avg_loan_cnt_with_insurance', 'vert_pil_last_credit_step_screen_view_3m',
                    'vert_pil_sms_success_3m', 'vert_pil_loan_application_success_3m',
                    'vert_pil_fee_discount_change_3m', 'vert_ghost_close_dpay3_last_days',
                    'vert_has_app_ru_tinkoff_investing', 'vert_has_app_ru_vtb_invest',
                    'vert_has_app_ru_cian_main', 'vert_has_app_ru_raiffeisennews',
                    'cntOnnRinCallAvg6m', 'cntVoiceOutMob6m', 'cntBlockWavg6m',
                    'cntRegionTripsWavg1m', 'businessTelSubs', 'acard', 'pil',
                    'hdb_bki_total_pil_max_del90']:
        try:
            if isinstance(value, str):
                # Replace comma with dot for decimal numbers
                value = value.replace(',', '.')
            return int(float(value)) if value is not None else None
        except (ValueError, TypeError):
            return None
    
    # Float columns - default
    try:
        if isinstance(value, str):
            # Replace comma with dot for decimal numbers
            value = value.replace(',', '.')
        return float(value) if value is not None else None
    except (ValueError, TypeError):
        return None


def load_feature_descriptions(descriptions_path: str, drop_table: bool = False):
    """Load feature descriptions from CSV into database"""
    print(f"Loading feature descriptions from {descriptions_path}...")
    
    # Read CSV with semicolon separator
    print("Reading feature descriptions CSV file...")
    try:
        # Try windows-1251 first (common for Russian CSVs)
        df = pd.read_csv(descriptions_path, sep=';', encoding='windows-1251', header=0)
    except (UnicodeDecodeError, UnicodeError):
        # Fallback to UTF-8 if windows-1251 fails
        print("windows-1251 failed, trying UTF-8...")
        df = pd.read_csv(descriptions_path, sep=';', encoding='utf-8', header=0)
    
    print(f"Loaded {len(df)} rows from CSV")
    
    # Get column names (first row should be header)
    if len(df.columns) < 2:
        print("Error: CSV should have at least 2 columns (feature_name, description)")
        return
    
    # Assume first column is feature name, second is description
    feature_col = df.columns[0]
    desc_col = df.columns[1]
    
    print(f"Using columns: {feature_col} -> {desc_col}")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Drop existing table if requested
        if drop_table:
            try:
                with engine.connect() as conn:
                    conn.execute(text('DROP TABLE IF EXISTS feature_descriptions CASCADE'))
                    conn.commit()
                print("Dropped existing feature_descriptions table")
            except Exception as e:
                print(f"Note: Could not drop existing table (may not exist): {e}")
        
        # Ensure table exists
        Base.metadata.create_all(bind=engine)
        print("Created feature_descriptions table if needed")
        
        # Clear existing descriptions
        db.query(FeatureDescription).delete()
        db.commit()
        print("Cleared existing feature descriptions")
        
        # Load descriptions
        descriptions = []
        skipped_header = False
        for _, row in df.iterrows():
            feature_name = str(row[feature_col]).strip()
            description = str(row[desc_col]).strip() if pd.notna(row[desc_col]) else None
            
            # Skip empty feature names
            if not feature_name or feature_name == 'nan' or feature_name.lower() == 'none':
                continue
            
            # Skip header row (first row with column names in Russian or English)
            # Check if this looks like a header row
            if (not skipped_header and 
                (feature_name in [feature_col, desc_col] or 
                 feature_name.lower() in ['признак', 'описание', 'название', 'feature_name', 'description', 'name'] or
                 (description and description.lower() in ['описание', 'description']))):
                skipped_header = True
                print(f"Skipping header row: {feature_name} -> {description}")
                continue
            
            # Clean description - ensure we have a valid Russian description
            if description and description != 'nan' and description.lower() not in ['none', 'описание', 'description']:
                clean_description = description.strip()
            else:
                clean_description = None
            
            # Only add if we have both feature name and description
            if feature_name and clean_description:
                descriptions.append(FeatureDescription(
                    feature_name=feature_name,
                    description=clean_description
                ))
            else:
                print(f"Warning: Skipping row with missing description: {feature_name}")
        
        # Bulk insert using add_all (more reliable than bulk_save_objects)
        if descriptions:
            db.add_all(descriptions)
            db.commit()
            print(f"Successfully loaded {len(descriptions)} feature descriptions")
        else:
            print("Warning: No descriptions to load")
        
    except Exception as e:
        db.rollback()
        print(f"Error loading feature descriptions: {e}")
        raise
    finally:
        db.close()


def load_csv_to_db(csv_path: str, batch_size: int = 1000, drop_table: bool = False):
    """Load CSV file into database"""
    print(f"Loading CSV from {csv_path}...")
    
    # Read CSV with UTF-8 encoding
    print("Reading CSV file with UTF-8 encoding...")
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8', low_memory=False,
                    on_bad_lines='skip' if hasattr(pd.read_csv, '__defaults__') else 'warn')
    print("Successfully read CSV")
    
    print(f"Loaded {len(df)} rows from CSV")
    print(f"Columns in CSV: {len(df.columns)}")
    print(f"Required feature columns: {len(FEATURE_COLS)}")
    
    # Check that all required columns are present
    required_cols = set(FEATURE_COLS) | {ID_COL}
    csv_cols = set(df.columns)
    missing_cols = required_cols - csv_cols
    if missing_cols:
        print(f"WARNING: Missing columns in CSV: {missing_cols}")
    
    # Filter to only required columns
    cols_to_load = [col for col in df.columns if col in required_cols]
    df = df[cols_to_load]
    
    # Create tables
    print("Creating database tables...")
    # Drop existing table if requested
    if drop_table:
        try:
            # Drop table with CASCADE to remove dependencies
            with engine.connect() as conn:
                conn.execute(text('DROP TABLE IF EXISTS client_features CASCADE'))
                conn.commit()
            print("Dropped existing client_features table")
            
            # Clear metadata cache to ensure fresh table creation
            if 'client_features' in Base.metadata.tables:
                del Base.metadata.tables['client_features']
            print("Cleared metadata cache")
        except Exception as e:
            print(f"Note: Could not drop existing table (may not exist): {e}")
    
    # Ensure database uses UTF-8 encoding
    with engine.connect() as conn:
        conn.execute(text("SET client_encoding TO 'UTF8'"))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Created database tables")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Process in batches
        total_rows = len(df)
        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1} ({i+1}-{min(i+batch_size, total_rows)}/{total_rows})...")
            
            batch_records = []
            for _, row in batch.iterrows():
                record_data = {}
                for col in cols_to_load:
                    value = normalize_value(row[col], col)
                    record_data[col] = value
                
                batch_records.append(ClientFeatures(**record_data))
            
            # Bulk insert with error handling for duplicates
            try:
                db.bulk_save_objects(batch_records)
                db.commit()
                print(f"  Inserted {len(batch_records)} records")
            except Exception as e:
                db.rollback()
                # If it's a unique constraint violation, try inserting one by one to skip duplicates
                if "UniqueViolation" in str(e) or "duplicate key" in str(e).lower():
                    print(f"  Warning: Duplicate key detected, inserting records individually to skip duplicates...")
                    inserted_count = 0
                    skipped_count = 0
                    for record in batch_records:
                        try:
                            db.add(record)
                            db.commit()
                            inserted_count += 1
                        except Exception as inner_e:
                            db.rollback()
                            if "UniqueViolation" in str(inner_e) or "duplicate key" in str(inner_e).lower():
                                skipped_count += 1
                            else:
                                # Re-raise if it's a different error
                                raise
                    print(f"  Inserted {inserted_count} records, skipped {skipped_count} duplicates")
                else:
                    # Re-raise if it's a different error
                    raise
        
        print(f"\nSuccessfully loaded {total_rows} records into database")
        
    except Exception as e:
        db.rollback()
        print(f"Error loading data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load CSV data into database")
    parser.add_argument(
        "--csv",
        type=str,
        default="ML/hackathon_income_test.csv",
        help="Path to CSV file"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Batch size for loading"
    )
    parser.add_argument(
        "--drop-table",
        action="store_true",
        help="Drop existing table before creating (use with caution!)"
    )
    parser.add_argument(
        "--descriptions",
        type=str,
        default="ML/features_description.csv",
        help="Path to feature descriptions CSV file"
    )
    parser.add_argument(
        "--load-descriptions",
        action="store_true",
        help="Load feature descriptions from CSV"
    )
    parser.add_argument(
        "--skip-client-data",
        action="store_true",
        help="Skip loading client data (useful when only loading descriptions)"
    )
    
    args = parser.parse_args()
    
    # Load feature descriptions if requested
    if args.load_descriptions:
        desc_path = Path(__file__).parent.parent / args.descriptions
        if not desc_path.exists():
            print(f"Error: Feature descriptions file not found at {desc_path}")
            sys.exit(1)
        load_feature_descriptions(str(desc_path), args.drop_table)
    
    # Load client data unless skipped
    if not args.skip_client_data:
        csv_path = Path(__file__).parent.parent / args.csv
        if not csv_path.exists():
            if args.load_descriptions:
                # If we loaded descriptions, it's OK if CSV doesn't exist
                print(f"Note: CSV file not found at {csv_path}, skipping client data load")
            else:
                print(f"Error: CSV file not found at {csv_path}")
                sys.exit(1)
        else:
            load_csv_to_db(str(csv_path), args.batch_size, args.drop_table)

