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
    - Debt-to-Income ratio (DTI)
    - Monthly payment to income ratio (should not exceed 50%)
    - Age
    - Credit history (overdue payments, number of loans)
    - BKI data (total products, overdue amounts)
    - Credit history requests frequency
    - Recent loan application rejections
    - Dependents (per capita income)
    - Job stability (seniority)
    
    Args:
        client_data: Dictionary with client features
        
    Returns:
        Risk score from 0.0 (low risk) to 1.0 (high risk)
    """
    risk_factors = []
    
    # 1. Income factor (15% weight) - reduced from 30% as DTI is more important
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
    risk_factors.append(("income", income_risk, 0.15))
    
    # 2. Debt-to-Income ratio (DTI) factor (20% weight) - NEW
    income_value = client_data.get("incomeValue")
    total_debt = (
        client_data.get("hdb_outstand_sum") or 0
    ) + (
        client_data.get("hdb_relend_outstand_sum") or 0
    ) + (
        client_data.get("loan_cur_amt") or 0
    )
    
    dti_risk = 0.3  # Default low risk
    if income_value is not None and isinstance(income_value, (int, float)) and income_value > 0:
        dti_ratio = total_debt / income_value if isinstance(total_debt, (int, float)) else 0
        if dti_ratio > 0.8:  # DTI > 80%
            dti_risk = 0.9  # Very high risk
        elif dti_ratio > 0.6:  # DTI > 60%
            dti_risk = 0.8  # High risk
        elif dti_ratio > 0.4:  # DTI > 40%
            dti_risk = 0.6  # Medium-high risk
        elif dti_ratio > 0.2:  # DTI > 20%
            dti_risk = 0.4  # Low-medium risk
        else:
            dti_risk = 0.2  # Low risk
    risk_factors.append(("dti", dti_risk, 0.20))
    
    # 3. Monthly payment to income ratio factor (15% weight) - NEW
    # Rule: monthly payment should not exceed 50% of income
    monthly_payment = (
        client_data.get("dp_ils_paymentssum_avg_12m") or 0
    ) / 12 if client_data.get("dp_ils_paymentssum_avg_12m") else 0
    
    payment_ratio_risk = 0.3  # Default low risk
    if income_value is not None and isinstance(income_value, (int, float)) and income_value > 0:
        monthly_income = income_value / 12
        if monthly_income > 0:
            payment_ratio = monthly_payment / monthly_income if isinstance(monthly_payment, (int, float)) else 0
            if payment_ratio > 0.5:  # Payment > 50% of income
                payment_ratio_risk = 0.9  # Very high risk
            elif payment_ratio > 0.4:  # Payment > 40%
                payment_ratio_risk = 0.7  # High risk
            elif payment_ratio > 0.3:  # Payment > 30%
                payment_ratio_risk = 0.5  # Medium risk
            elif payment_ratio > 0.2:  # Payment > 20%
                payment_ratio_risk = 0.4  # Low-medium risk
            else:
                payment_ratio_risk = 0.2  # Low risk
    risk_factors.append(("payment_ratio", payment_ratio_risk, 0.15))
    
    # 4. Age factor (5% weight) - reduced
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
    risk_factors.append(("age", age_risk, 0.05))
    
    # 5. Overdue payments factor (20% weight) - includes utility, fines, alimony, taxes
    overdue_sum = (
        client_data.get("hdb_bki_total_max_overdue_sum") or 0
    ) + (
        client_data.get("ovrd_sum") or 0
    ) + (
        client_data.get("hdb_ovrd_sum") or 0
    )
    
    overdue_risk = 0.3  # Default low risk
    if isinstance(overdue_sum, (int, float)) and overdue_sum > 0:
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
    risk_factors.append(("overdue", overdue_risk, 0.20))
    
    # 6. Number of loans factor (8% weight) - reduced
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
    risk_factors.append(("loans", loan_risk, 0.08))
    
    # 7. Credit history requests frequency factor (5% weight) - NEW
    # Frequent requests indicate financial stress
    days_after_last_request = client_data.get("days_after_last_request")
    request_risk = 0.3  # Default low risk
    if days_after_last_request is not None and isinstance(days_after_last_request, (int, float)):
        if days_after_last_request < 30:  # Request in last month
            request_risk = 0.7  # High risk (frequent requests)
        elif days_after_last_request < 90:  # Request in last 3 months
            request_risk = 0.5  # Medium risk
        elif days_after_last_request < 180:  # Request in last 6 months
            request_risk = 0.4  # Low-medium risk
        else:
            request_risk = 0.3  # Low risk (infrequent requests)
    risk_factors.append(("credit_requests", request_risk, 0.05))
    
    # 8. Recent loan application rejections factor (5% weight) - NEW
    # Low success rate indicates rejections
    loan_success = client_data.get("vert_pil_loan_application_success_3m")
    rejection_risk = 0.3  # Default low risk
    if loan_success is not None and isinstance(loan_success, (int, float)):
        # Assuming this is a ratio or count - lower means more rejections
        if loan_success == 0:  # No successful applications
            rejection_risk = 0.8  # High risk (all rejected)
        elif loan_success < 0.3:  # Less than 30% success
            rejection_risk = 0.7  # High risk
        elif loan_success < 0.5:  # Less than 50% success
            rejection_risk = 0.5  # Medium risk
        else:
            rejection_risk = 0.3  # Low risk (good success rate)
    risk_factors.append(("rejections", rejection_risk, 0.05))
    
    # 9. Dependents factor (5% weight) - NEW
    # Low per capita income with high total income suggests dependents
    per_capita_income = client_data.get("per_capita_income_rur_amt")
    dependents_risk = 0.4  # Default medium risk
    if income_value is not None and per_capita_income is not None:
        if isinstance(income_value, (int, float)) and isinstance(per_capita_income, (int, float)) and income_value > 0:
            if per_capita_income < income_value * 0.5:  # Per capita < 50% of total
                dependents_risk = 0.6  # Higher risk (likely has dependents)
            elif per_capita_income < income_value * 0.7:  # Per capita < 70% of total
                dependents_risk = 0.5  # Medium risk
            else:
                dependents_risk = 0.3  # Lower risk (few or no dependents)
    risk_factors.append(("dependents", dependents_risk, 0.05))
    
    # 10. Job stability factor (2% weight) - NEW
    # Higher seniority = lower risk
    seniority = client_data.get("dp_ils_total_seniority")
    stability_risk = 0.5  # Default medium risk
    if seniority is not None and isinstance(seniority, (int, float)):
        # Assuming seniority is in days or months
        if seniority > 1825:  # > 5 years
            stability_risk = 0.2  # Very low risk
        elif seniority > 1095:  # > 3 years
            stability_risk = 0.3  # Low risk
        elif seniority > 365:  # > 1 year
            stability_risk = 0.4  # Low-medium risk
        elif seniority > 180:  # > 6 months
            stability_risk = 0.5  # Medium risk
        else:
            stability_risk = 0.6  # Higher risk (short tenure)
    risk_factors.append(("job_stability", stability_risk, 0.02))
    
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

