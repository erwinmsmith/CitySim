"""
Governance efficiency metrics calculation
"""
import numpy as np
from typing import List, Dict, Any


def calculate_efficiency(interaction_records: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate governance efficiency indicators
    
    Args:
        interaction_records: List of interaction records from simulation
        
    Returns:
        Dictionary containing efficiency metrics
    """
    if not interaction_records:
        return {
            'avg_response_time': 0.0,
            'resolution_rate': 0.0,
            'resource_utilization': 0.0,
            'policy_cost': 0.0
        }
    
    # Filter service request interactions
    service_requests = [
        r for r in interaction_records 
        if r.get('type') == 'service_request'
    ]
    
    if not service_requests:
        response_times = [1.0]  # Default value
        resolution_rates = [0.5]  # Default value
    else:
        response_times = [
            r.get('response_time', 1.0) 
            for r in service_requests
        ]
        resolution_rates = [
            1.0 if r.get('resolved', False) else 0.0 
            for r in service_requests
        ]
    
    # Calculate metrics
    avg_response_time = np.mean(response_times)
    resolution_rate = np.mean(resolution_rates)
    resource_utilization = calculate_resource_usage(interaction_records)
    policy_cost = calculate_policy_implementation_cost(interaction_records)
    
    return {
        'avg_response_time': float(avg_response_time),
        'resolution_rate': float(resolution_rate),
        'resource_utilization': float(resource_utilization),
        'policy_cost': float(policy_cost)
    }


def calculate_resource_usage(interaction_records: List[Dict[str, Any]]) -> float:
    """
    Calculate resource utilization rate
    
    Args:
        interaction_records: List of interaction records
        
    Returns:
        Resource utilization rate (0-1)
    """
    if not interaction_records:
        return 0.0
    
    # Calculate based on number of active interactions
    active_interactions = len([
        r for r in interaction_records 
        if r.get('status') == 'active'
    ])
    
    total_capacity = len(interaction_records)
    if total_capacity == 0:
        return 0.0
    
    utilization = min(active_interactions / total_capacity, 1.0)
    return utilization


def calculate_policy_implementation_cost(interaction_records: List[Dict[str, Any]]) -> float:
    """
    Calculate policy implementation cost
    
    Args:
        interaction_records: List of interaction records
        
    Returns:
        Average policy implementation cost
    """
    if not interaction_records:
        return 0.0
    
    policy_interactions = [
        r for r in interaction_records 
        if r.get('type') == 'policy_implementation'
    ]
    
    if not policy_interactions:
        return 0.0
    
    costs = [
        r.get('cost', 0.0) 
        for r in policy_interactions
    ]
    
    return float(np.mean(costs)) if costs else 0.0