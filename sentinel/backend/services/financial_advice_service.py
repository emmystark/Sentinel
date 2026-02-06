import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from supabase import Client
from services.qwen_service import analyze_transaction_with_qwen

logger = logging.getLogger(__name__)


async def analyze_spending_patterns(
    user_id: str,
    supabase: Client,
    months: int = 1
) -> Dict[str, Any]:
    """
    Analyze user's spending patterns over the specified period.
    
    Args:
        user_id: User identifier
        supabase: Supabase client
        months: Number of months to analyze
        
    Returns:
        Dictionary with spending analysis
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=30 * months)
        
        # Fetch transactions in date range
        response = supabase.table("transactions").select(
            "merchant, amount, category, date, description"
        ).eq("user_id", user_id).gte(
            "date", start_date.isoformat()
        ).lte(
            "date", end_date.isoformat()
        ).order("date", desc=True).execute()
        
        transactions = response.data or []
        
        # Analyze patterns
        analysis = {
            "total_transactions": len(transactions),
            "total_spent": 0,
            "category_breakdown": {},
            "daily_average": 0,
            "largest_transaction": None,
            "category_averages": {},
            "trends": {},
            "high_risk_categories": []
        }
        
        if not transactions:
            return analysis
        
        # Calculate totals and breakdowns
        category_totals = {}
        category_counts = {}
        max_transaction = None
        max_amount = 0
        
        for transaction in transactions:
            amount = float(transaction.get("amount", 0))
            category = transaction.get("category", "Other")
            
            analysis["total_spent"] += amount
            
            # Track categories
            if category not in category_totals:
                category_totals[category] = 0
                category_counts[category] = 0
            
            category_totals[category] += amount
            category_counts[category] += 1
            
            # Track largest transaction
            if amount > max_amount:
                max_amount = amount
                max_transaction = transaction
        
        # Build category breakdown
        analysis["category_breakdown"] = category_totals
        
        # Calculate averages
        if len(transactions) > 0:
            analysis["daily_average"] = analysis["total_spent"] / len(transactions)
        
        # Calculate category averages
        for category, total in category_totals.items():
            count = category_counts.get(category, 1)
            analysis["category_averages"][category] = total / count if count > 0 else 0
        
        # Set largest transaction
        analysis["largest_transaction"] = max_transaction
        
        # Identify categories with high spending
        if category_totals:
            avg_category_spend = analysis["total_spent"] / len(category_totals)
            for category, total in category_totals.items():
                if total > avg_category_spend * 1.5:
                    analysis["high_risk_categories"].append({
                        "category": category,
                        "spent": total,
                        "percentage": (total / analysis["total_spent"] * 100) if analysis["total_spent"] > 0 else 0
                    })
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing spending patterns: {e}")
        return {
            "total_transactions": 0,
            "total_spent": 0,
            "category_breakdown": {},
            "daily_average": 0,
            "error": str(e)
        }


async def generate_financial_advice(
    user_id: str,
    supabase: Client,
    monthly_income: float,
    fixed_bills: float,
    savings_goal: float
) -> Dict[str, Any]:
    """
    Generate personalized financial advice based on spending patterns.
    
    Args:
        user_id: User identifier
        supabase: Supabase client
        monthly_income: Monthly income
        fixed_bills: Monthly fixed bills
        savings_goal: Desired monthly savings
        
    Returns:
        Dictionary with advice and recommendations
    """
    try:
        # Analyze spending
        analysis = await analyze_spending_patterns(user_id, supabase, months=1)
        
        advice = {
            "summary": "",
            "recommendations": [],
            "savings_opportunity": 0,
            "budget_status": "",
            "warnings": [],
            "positive_notes": []
        }
        
        total_spent = analysis.get("total_spent", 0)
        available_for_discretionary = monthly_income - fixed_bills - savings_goal
        
        # Analyze budget status
        budget_percentage = (total_spent / (monthly_income - fixed_bills) * 100) if (monthly_income - fixed_bills) > 0 else 0
        
        if budget_percentage > 100:
            advice["budget_status"] = "CRITICAL: Over budget"
            advice["warnings"].append("You're spending more than your available budget.")
        elif budget_percentage > 80:
            advice["budget_status"] = "WARNING: Approaching budget limit"
            advice["warnings"].append("You're approaching your budget limit. Reduce discretionary spending.")
        elif budget_percentage > 50:
            advice["budget_status"] = "GOOD: Within budget"
            advice["positive_notes"].append("You're maintaining good spending control.")
        else:
            advice["budget_status"] = "EXCELLENT: Well within budget"
            advice["positive_notes"].append("Excellent spending discipline!")
        
        # Calculate savings opportunity
        if total_spent < available_for_discretionary:
            advice["savings_opportunity"] = available_for_discretionary - total_spent
        
        # Analyze high-risk categories
        high_risk = analysis.get("high_risk_categories", [])
        if high_risk:
            for category_data in high_risk:
                category = category_data.get("category")
                spent = category_data.get("spent", 0)
                percentage = category_data.get("percentage", 0)
                advice["recommendations"].append(
                    f"Consider reducing {category} spending (currently {percentage:.1f}% of total)."
                )
        
        # Generate summary
        if advice["savings_opportunity"] > 0:
            advice["summary"] = f"You have an opportunity to save ${advice['savings_opportunity']:.2f}/month by adjusting your discretionary spending."
        else:
            advice["summary"] = "Focus on building better spending habits in high-risk categories."
        
        # Add category-specific advice
        category_breakdown = analysis.get("category_breakdown", {})
        for category, total in category_breakdown.items():
            if total > 0:
                advice["recommendations"].append(
                    f"{category}: ${total:.2f}/month - Set a limit and track carefully."
                )
        
        return advice
        
    except Exception as e:
        logger.error(f"Error generating financial advice: {e}")
        return {
            "summary": "Unable to generate advice at this time",
            "recommendations": [],
            "savings_opportunity": 0,
            "budget_status": "UNKNOWN",
            "warnings": [str(e)],
            "positive_notes": []
        }


async def get_health_score(
    user_id: str,
    supabase: Client,
    monthly_income: float,
    fixed_bills: float,
    savings_goal: float
) -> Dict[str, Any]:
    """
    Calculate financial health score for a user.
    
    Args:
        user_id: User identifier
        supabase: Supabase client
        monthly_income: Monthly income
        fixed_bills: Monthly fixed bills
        savings_goal: Desired monthly savings
        
    Returns:
        Health score and detailed breakdown
    """
    try:
        analysis = await analyze_spending_patterns(user_id, supabase, months=1)
        
        total_spent = analysis.get("total_spent", 0)
        score = 100
        details = {}
        
        # Budget adherence score (40 points)
        available_for_discretionary = monthly_income - fixed_bills - savings_goal
        if available_for_discretionary > 0:
            budget_ratio = (total_spent / available_for_discretionary) * 100
            if budget_ratio <= 70:
                details["budget_adherence"] = 40
            elif budget_ratio <= 85:
                details["budget_adherence"] = 30
            elif budget_ratio <= 100:
                details["budget_adherence"] = 20
            else:
                details["budget_adherence"] = 0
        else:
            details["budget_adherence"] = 0
        
        score -= (40 - details["budget_adherence"])
        
        # Category diversity score (30 points)
        category_count = len(analysis.get("category_breakdown", {}))
        if category_count >= 4:
            details["diversity"] = 30
        elif category_count >= 2:
            details["diversity"] = 20
        else:
            details["diversity"] = 10
        
        score -= (30 - details["diversity"])
        
        # Spending consistency score (20 points)
        transactions = analysis.get("total_transactions", 0)
        if transactions > 10:
            details["consistency"] = 20
        elif transactions > 5:
            details["consistency"] = 15
        else:
            details["consistency"] = 10
        
        score -= (20 - details["consistency"])
        
        # Savings ratio score (10 points)
        if monthly_income > 0:
            potential_savings = monthly_income - fixed_bills - total_spent
            savings_ratio = (potential_savings / monthly_income) * 100
            if savings_ratio >= savings_goal / monthly_income * 100:
                details["savings"] = 10
            elif savings_ratio >= 5:
                details["savings"] = 7
            else:
                details["savings"] = 0
        else:
            details["savings"] = 0
        
        score -= (10 - details["savings"])
        
        # Ensure score is between 0 and 100
        score = max(0, min(100, score))
        
        return {
            "score": score,
            "grade": _get_grade(score),
            "details": details,
            "total_spent": total_spent,
            "available_for_discretionary": available_for_discretionary,
            "recommendations": _get_recommendations(score)
        }
        
    except Exception as e:
        logger.error(f"Error calculating health score: {e}")
        return {
            "score": 50,
            "grade": "C",
            "details": {},
            "error": str(e)
        }


def _get_grade(score: float) -> str:
    """Convert score to letter grade."""
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"


def _get_recommendations(score: float) -> List[str]:
    """Get recommendations based on health score."""
    recommendations = []
    
    if score >= 90:
        recommendations.append("Excellent financial health! Keep maintaining your current habits.")
    elif score >= 80:
        recommendations.append("Good financial health. Look for small optimizations.")
    elif score >= 70:
        recommendations.append("Fair financial health. Consider reviewing your budget categories.")
    elif score >= 60:
        recommendations.append("Needs improvement. Focus on tracking and reducing discretionary spending.")
    else:
        recommendations.append("Critical: Review your spending immediately and create a strict budget.")
    
    return recommendations


async def get_transaction_advice(
    merchant: str,
    amount: float,
    category: str,
    description: str
) -> Dict[str, Any]:
    """
    Get AI-powered advice for a specific transaction.
    
    Args:
        merchant: Merchant name
        amount: Transaction amount
        category: Transaction category
        description: Transaction description
        
    Returns:
        Transaction-specific advice
    """
    try:
        analysis = await analyze_transaction_with_qwen(merchant, amount, category, description)
        
        return {
            "merchant": merchant,
            "amount": amount,
            "category": category,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Error getting transaction advice: {e}")
        return {
            "merchant": merchant,
            "amount": amount,
            "category": category,
            "analysis": {
                "insight": "Transaction recorded",
                "risk_level": "medium",
                "recommendation": "Monitor this category",
                "is_unusual": False
            }
        }
