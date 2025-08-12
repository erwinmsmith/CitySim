"""
Governance fairness metrics calculation
"""
import numpy as np
from typing import List, Dict, Any


def calculate_fairness(residents: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate governance fairness indicators
    
    Args:
        residents: List of resident agents with their attributes
        
    Returns:
        Dictionary containing fairness metrics
    """
    if not residents:
        return {
            'service_access_gini': 0.0,
            'usage_depth_gini': 0.0,
            'satisfaction_gini': 0.0,
            'digital_divide_index': 0.0
        }
    
    # Group residents by area
    area_groups = {}
    for resident in residents:
        area = resident.get('area', 'core_area')
        if area not in area_groups:
            area_groups[area] = []
        area_groups[area].append(resident)
    
    # Calculate access and usage metrics by area
    access_gaps = []
    usage_gaps = []
    satisfaction_scores = []
    
    areas = ['core_area', 'urban_rural_fringe', 'rural']
    
    for area in areas:
        area_residents = area_groups.get(area, [])
        
        if area_residents:
            # Digital access rate
            access_rate = np.mean([
                1.0 if r.get('digital_access', False) else 0.0 
                for r in area_residents
            ])
            
            # Service usage depth
            usage_depth = np.mean([
                r.get('service_usage_frequency', 0) 
                for r in area_residents
            ])
            
            # Satisfaction scores
            satisfaction = np.mean([
                r.get('satisfaction', 3.0) 
                for r in area_residents
            ])
            
            access_gaps.append(access_rate)
            usage_gaps.append(usage_depth)
            satisfaction_scores.append(satisfaction)
        else:
            # Default values for areas with no residents
            access_gaps.append(0.0)
            usage_gaps.append(0.0)
            satisfaction_scores.append(0.0)
    
    # Calculate Gini coefficients
    service_access_gini = calculate_gini(access_gaps)
    usage_depth_gini = calculate_gini(usage_gaps)
    satisfaction_gini = calculate_gini(satisfaction_scores)
    
    # Calculate digital divide index
    digital_divide_index = calculate_digital_divide(residents)
    
    return {
        'service_access_gini': float(service_access_gini),
        'usage_depth_gini': float(usage_depth_gini),
        'satisfaction_gini': float(satisfaction_gini),
        'digital_divide_index': float(digital_divide_index)
    }


def calculate_gini(values: List[float]) -> float:
    """
    Calculate Gini coefficient
    
    Args:
        values: List of values to calculate Gini coefficient for
        
    Returns:
        Gini coefficient (0 = perfect equality, 1 = perfect inequality)
    """
    if not values or len(values) < 2:
        return 0.0
    
    # Remove negative values and sort
    values = sorted([max(0, v) for v in values])
    n = len(values)
    
    if all(v == values[0] for v in values):
        return 0.0  # Perfect equality
    
    # Calculate Gini coefficient
    cumsum = np.cumsum(values)
    total = cumsum[-1]
    
    if total == 0:
        return 0.0
    
    gini = (n + 1 - 2 * np.sum(cumsum) / total) / n
    return max(0.0, min(1.0, gini))


def calculate_digital_divide(residents: List[Dict[str, Any]]) -> float:
    """
    Calculate digital divide index
    
    Args:
        residents: List of resident agents
        
    Returns:
        Digital divide index (higher = more divided)
    """
    if not residents:
        return 0.0
    
    # Group by income level
    high_income = [r for r in residents if r.get('income_level', 0) > 6000]
    low_income = [r for r in residents if r.get('income_level', 0) <= 6000]
    
    if not high_income or not low_income:
        return 0.0
    
    # Calculate digital access rates
    high_income_access = np.mean([
        1.0 if r.get('digital_access', False) else 0.0 
        for r in high_income
    ])
    
    low_income_access = np.mean([
        1.0 if r.get('digital_access', False) else 0.0 
        for r in low_income
    ])
    
    # Digital divide is the difference in access rates
    divide = abs(high_income_access - low_income_access)
    return float(divide)