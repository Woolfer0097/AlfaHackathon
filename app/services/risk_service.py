"""
Service for calculating risk scores and client segmentation
"""
from typing import Optional, Dict, Any, List, Tuple
from app.core.logging import get_logger

logger = get_logger(__name__)


def calculate_risk_score(client_data: Dict[str, Any]) -> float:
    """
    Calculate comprehensive risk score based on multiple factors
    
    Factors considered:
    - Income level
    - Age
    - Credit history (overdue payments, number of loans)
    - BKI data (total products, overdue amounts)
    
    Args:
        client_data: Dictionary with client features
        
    Returns:
        Risk score from 0.0 (low risk) to 1.0 (high risk)
    """
    risk_factors = []
    
    # 1. Income factor (30% weight)
    income_value = client_data.get("incomeValue")
    income_risk = 0.5  # Default medium risk
    if income_value is not None and isinstance(income_value, (int, float)):
        if income_value < 30000:
            income_risk = 0.8  # Very high risk
        elif income_value < 50000:
            income_risk = 0.7  # High risk
        elif income_value < 100000:
            income_risk = 0.5  # Medium risk
        elif income_value < 200000:
            income_risk = 0.3  # Low risk
        else:
            income_risk = 0.2  # Very low risk
    risk_factors.append(("income", income_risk, 0.3))
    
    # 2. Age factor (10% weight)
    age = client_data.get("age")
    age_risk = 0.5  # Default
    if age is not None and isinstance(age, (int, float)):
        age = int(age)
        if age < 22:
            age_risk = 0.6  # Higher risk for very young
        elif age < 30:
            age_risk = 0.5  # Medium risk
        elif age < 60:
            age_risk = 0.4  # Lower risk for middle age
        else:
            age_risk = 0.5  # Medium risk for older
    risk_factors.append(("age", age_risk, 0.1))
    
    # 3. Overdue payments factor (25% weight)
    overdue_sum = client_data.get("hdb_bki_total_max_overdue_sum") or client_data.get("ovrd_sum") or client_data.get("hdb_ovrd_sum")
    overdue_risk = 0.3  # Default low risk
    if overdue_sum is not None and isinstance(overdue_sum, (int, float)) and overdue_sum > 0:
        if overdue_sum > 100000:
            overdue_risk = 0.9  # Very high risk
        elif overdue_sum > 50000:
            overdue_risk = 0.8  # High risk
        elif overdue_sum > 20000:
            overdue_risk = 0.6  # Medium-high risk
        elif overdue_sum > 5000:
            overdue_risk = 0.5  # Medium risk
        else:
            overdue_risk = 0.4  # Low-medium risk
    risk_factors.append(("overdue", overdue_risk, 0.25))
    
    # 4. Number of loans factor (15% weight)
    loan_cnt = client_data.get("loan_cnt") or 0
    other_credits = client_data.get("other_credits_count") or 0
    total_loans = (loan_cnt if isinstance(loan_cnt, (int, float)) else 0) + (other_credits if isinstance(other_credits, (int, float)) else 0)
    
    loan_risk = 0.4  # Default
    if total_loans == 0:
        loan_risk = 0.5  # Medium risk (no credit history)
    elif total_loans == 1:
        loan_risk = 0.4  # Lower risk (good credit history)
    elif total_loans <= 3:
        loan_risk = 0.5  # Medium risk
    elif total_loans <= 5:
        loan_risk = 0.6  # Medium-high risk
    else:
        loan_risk = 0.7  # High risk (too many loans)
    risk_factors.append(("loans", loan_risk, 0.15))
    
    # 5. BKI products and credit limits factor (10% weight)
    bki_products = client_data.get("bki_total_products") or client_data.get("hdb_bki_total_products") or 0
    bki_products = bki_products if isinstance(bki_products, (int, float)) else 0
    
    bki_risk = 0.5  # Default
    if bki_products == 0:
        bki_risk = 0.5  # Medium risk (no credit history)
    elif bki_products <= 2:
        bki_risk = 0.4  # Lower risk
    elif bki_products <= 5:
        bki_risk = 0.5  # Medium risk
    else:
        bki_risk = 0.6  # Higher risk (many products)
    risk_factors.append(("bki", bki_risk, 0.1))
    
    # 6. Credit card overdue factor (10% weight)
    cc_overdue = client_data.get("hdb_bki_total_cc_max_overdue") or client_data.get("hdb_bki_active_cc_max_overdue")
    cc_risk = 0.3  # Default low risk
    if cc_overdue is not None and isinstance(cc_overdue, (int, float)) and cc_overdue > 0:
        if cc_overdue > 50000:
            cc_risk = 0.8  # High risk
        elif cc_overdue > 20000:
            cc_risk = 0.7  # Medium-high risk
        elif cc_overdue > 5000:
            cc_risk = 0.6  # Medium risk
        else:
            cc_risk = 0.5  # Medium risk
    risk_factors.append(("cc_overdue", cc_risk, 0.1))
    
    # Calculate weighted average
    total_weight = sum(weight for _, _, weight in risk_factors)
    if total_weight == 0:
        return 0.5  # Default risk
    
    weighted_sum = sum(risk * weight for _, risk, weight in risk_factors)
    final_risk = weighted_sum / total_weight
    
    # Ensure risk is between 0 and 1
    final_risk = max(0.0, min(1.0, final_risk))
    
    logger.debug(f"Risk score calculated: {final_risk:.3f} (factors: {[(name, f'{r:.2f}', f'{w:.2f}') for name, r, w in risk_factors]})")
    
    return round(final_risk, 3)


def get_income_segment(income_value: Optional[float], income_category: Optional[str] = None) -> str:
    """
    Get human-readable income segment name
    
    Args:
        income_value: Current income value
        income_category: Income category from database
        
    Returns:
        Human-readable segment name in Russian
    """
    # First try to use income category if available
    if income_category:
        category_str = str(income_category).lower()
        
        # Map known categories to readable names
        if "below_50k" in category_str or "50k" in category_str:
            return "Низкий доход (до 50 тыс.)"
        elif "50k_to_100k" in category_str or "50_100" in category_str:
            return "Ниже среднего (50-100 тыс.)"
        elif "100k_to_200k" in category_str or "100_200" in category_str:
            return "Средний доход (100-200 тыс.)"
        elif "200k_to_500k" in category_str or "200_500" in category_str:
            return "Выше среднего (200-500 тыс.)"
        elif "500k_to_1m" in category_str or "500_1m" in category_str or "500k" in category_str:
            return "Высокий доход (500 тыс. - 1 млн.)"
        elif "above_1m" in category_str or "1m" in category_str or "above" in category_str:
            return "Очень высокий доход (свыше 1 млн.)"
    
    # Fallback to income value if category not available
    if income_value is None:
        return "Неизвестно"
    
    if income_value < 30000:
        return "Очень низкий доход (до 30 тыс.)"
    elif income_value < 50000:
        return "Низкий доход (30-50 тыс.)"
    elif income_value < 100000:
        return "Ниже среднего (50-100 тыс.)"
    elif income_value < 200000:
        return "Средний доход (100-200 тыс.)"
    elif income_value < 500000:
        return "Выше среднего (200-500 тыс.)"
    elif income_value < 1000000:
        return "Высокий доход (500 тыс. - 1 млн.)"
    else:
        return "Очень высокий доход (свыше 1 млн.)"

