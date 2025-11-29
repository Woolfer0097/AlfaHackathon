import json
from pathlib import Path
from sqlalchemy import Column, String, Float, Boolean, Integer, BigInteger, Table, MetaData
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.orm import declarative_base
from app.core.database import Base

# Load model metadata
MODEL_META_PATH = Path(__file__).parent.parent.parent / "ML" / "model_meta.json"
with open(MODEL_META_PATH, 'r', encoding='utf-8') as f:
    MODEL_META = json.load(f)

FEATURE_COLS = MODEL_META["feature_cols"]
CAT_FEATURES = MODEL_META["cat_features"]
ID_COL = MODEL_META["id_col"]


def get_column_type(col_name: str):
    """Determine SQLAlchemy column type based on column name"""
    if col_name == ID_COL:
        return BigInteger
    elif col_name in CAT_FEATURES:
        return String
    elif col_name.endswith('_flag'):
        return Boolean
    elif col_name in ['age', 'loan_cnt', 'other_credits_count', 'mob_cnt_days', 
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
        return Integer
    else:
        return Float  # Default to Float for numeric features


# Build columns list and mapping
# PostgreSQL has a 63-byte limit for identifiers (even quoted ones)
# We need to create short unique names for DB and map them to full feature names
columns_list = []
_db_name_to_full_name = {}  # DB column name -> full feature name
_full_name_to_db_name = {}  # full feature name -> DB column name

# Add id column
columns_list.append(Column(ID_COL, BigInteger, primary_key=True, index=True))
_db_name_to_full_name[ID_COL] = ID_COL
_full_name_to_db_name[ID_COL] = ID_COL

# Track added columns to avoid duplicates
added_col_names = set([ID_COL])
# Track truncated names to detect collisions
truncated_to_count = {}  # truncated_name -> count for suffix generation

# Add all feature columns
for col in FEATURE_COLS:
    if col == ID_COL:
        continue
    
    # Skip if already added (safety check)
    if col in added_col_names:
        print(f"Warning: Skipping duplicate column: {col}")
        continue
    
    added_col_names.add(col)
    col_type = get_column_type(col)
    
    # Generate unique DB name (max 63 bytes for PostgreSQL)
    if len(col) <= 63:
        # Short enough - use as is
        db_col_name = col
    else:
        # Too long - truncate and add suffix if collision
        truncated = col[:63]
        if truncated in truncated_to_count:
            truncated_to_count[truncated] += 1
            # Create unique name with suffix (keep under 63)
            suffix = f"_{truncated_to_count[truncated]:02d}"
            db_col_name = col[:63-len(suffix)] + suffix
        else:
            truncated_to_count[truncated] = 0
            db_col_name = truncated
    
    # Store mapping
    _db_name_to_full_name[db_col_name] = col
    _full_name_to_db_name[col] = db_col_name
    
    # Create column with DB name but use key parameter for Python attribute access
    if col_type == String:
        columns_list.append(Column(db_col_name, String, nullable=True, key=col))
    elif col_type == Boolean:
        columns_list.append(Column(db_col_name, Boolean, nullable=True, key=col))
    elif col_type == Integer:
        columns_list.append(Column(db_col_name, Integer, nullable=True, key=col))
    else:  # Float
        columns_list.append(Column(db_col_name, DOUBLE_PRECISION, nullable=True, key=col))


# Create table using Table constructor
# Remove existing table from metadata if it exists to avoid conflicts
if 'client_features' in Base.metadata.tables:
    Base.metadata.remove(Base.metadata.tables['client_features'])

client_features_table = Table(
    'client_features',
    Base.metadata,
    *columns_list
)


# Create ORM class
class ClientFeatures(Base):
    __table__ = client_features_table
    
    def to_dict(self):
        """Convert to dictionary with all feature columns (using full feature names)"""
        result = {}
        for col in self.__table__.columns:
            # Map DB column name back to full feature name
            db_name = col.name
            full_name = _db_name_to_full_name.get(db_name, db_name)
            # Use key (Python attribute name) to get value
            attr_name = col.key if hasattr(col, 'key') else col.name
            result[full_name] = getattr(self, attr_name, None)
        return result

# Export constants for use in other modules
__all__ = ['ClientFeatures', 'FEATURE_COLS', 'CAT_FEATURES', 'ID_COL']
