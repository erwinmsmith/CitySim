"""
Agent status metrics calculation
"""
import numpy as np
from typing import List, Dict, Any, Union


def calculate_agent_status(
    government: Dict[str, Any], 
    enterprises: List[Dict[str, Any]], 
    residents: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate agent status indicators
    
    Args:
        government: Government agent state
        enterprises: List of enterprise agents
        residents: List of resident agents
        
    Returns:
        Dictionary containing agent status metrics
    """
    resident_metrics = calculate_resident_metrics(residents)
    enterprise_metrics = calculate_enterprise_metrics(enterprises)
    government_metrics = calculate_government_metrics(government)
    
    return {
        'resident_metrics': resident_metrics,
        'enterprise_metrics': enterprise_metrics,
        'government_metrics': government_metrics,
        'overall_status': calculate_overall_status(
            resident_metrics, enterprise_metrics, government_metrics
        )
    }


def calculate_resident_metrics(residents: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate resident-related metrics
    
    Args:
        residents: List of resident agents
        
    Returns:
        Dictionary containing resident metrics
    """
    if not residents:
        return {
            'avg_satisfaction': 0.0,
            'avg_trust': 0.0,
            'satisfaction_std': 0.0,
            'trust_std': 0.0,
            'digital_adoption_rate': 0.0
        }
    
    # Extract satisfaction and trust scores
    satisfaction_scores = [
        r.get('satisfaction', 3.0) for r in residents
    ]
    trust_scores = [
        r.get('trust_in_government', 50.0) for r in residents
    ]
    
    # Calculate digital adoption
    digital_users = [
        r for r in residents 
        if r.get('digital_access', False) and r.get('service_usage_frequency', 0) > 2
    ]
    digital_adoption_rate = len(digital_users) / len(residents)
    
    return {
        'avg_satisfaction': float(np.mean(satisfaction_scores)),
        'avg_trust': float(np.mean(trust_scores)),
        'satisfaction_std': float(np.std(satisfaction_scores)),
        'trust_std': float(np.std(trust_scores)),
        'digital_adoption_rate': float(digital_adoption_rate)
    }


def calculate_enterprise_metrics(enterprises: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate enterprise-related metrics
    
    Args:
        enterprises: List of enterprise agents
        
    Returns:
        Dictionary containing enterprise metrics
    """
    if not enterprises:
        return {
            'avg_market_share': 0.0,
            'avg_innovation_level': 0.0,
            'avg_compliance_rate': 0.0,
            'market_concentration': 0.0
        }
    
    # Extract enterprise metrics
    market_shares = [
        e.get('market_share', 0.1) for e in enterprises
    ]
    innovation_levels = [
        e.get('innovation_level', 50.0) for e in enterprises
    ]
    compliance_rates = [
        e.get('data_usage_compliance', 90.0) for e in enterprises
    ]
    
    # Calculate market concentration (Herfindahl index)
    market_concentration = calculate_herfindahl_index(market_shares)
    
    return {
        'avg_market_share': float(np.mean(market_shares)),
        'avg_innovation_level': float(np.mean(innovation_levels)),
        'avg_compliance_rate': float(np.mean(compliance_rates)),
        'market_concentration': float(market_concentration)
    }


def calculate_government_metrics(government: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate government-related metrics
    
    Args:
        government: Government agent state
        
    Returns:
        Dictionary containing government metrics
    """
    # Extract government attributes and state
    attributes = government.get('attributes', {})
    state = government.get('state', {})
    
    # Goal achievement rate (simulated based on performance)
    goal_achievement = calculate_goal_achievement(government)
    
    # Policy effectiveness (based on recent actions)
    policy_effectiveness = calculate_policy_effectiveness(government)
    
    # Resource utilization
    resource_utilization = state.get('resource_utilization', 0.7)
    
    return {
        'goal_achievement_rate': float(goal_achievement),
        'policy_effectiveness': float(policy_effectiveness),
        'resource_utilization': float(resource_utilization),
        'financial_efficiency': float(attributes.get('financial_resources', 100) / 100),
        'transparency_level': float(attributes.get('information_transparency', 70) / 100)
    }


def calculate_herfindahl_index(market_shares: List[float]) -> float:
    """
    Calculate Herfindahl-Hirschman Index for market concentration
    
    Args:
        market_shares: List of market shares (as decimals)
        
    Returns:
        HHI value (0-1, higher = more concentrated)
    """
    if not market_shares:
        return 0.0
    
    # Normalize market shares to sum to 1
    total_share = sum(market_shares)
    if total_share == 0:
        return 0.0
    
    normalized_shares = [share / total_share for share in market_shares]
    
    # Calculate HHI
    hhi = sum(share ** 2 for share in normalized_shares)
    return hhi


def calculate_goal_achievement(government: Dict[str, Any]) -> float:
    """
    Calculate government goal achievement rate
    
    Args:
        government: Government agent state
        
    Returns:
        Goal achievement rate (0-1)
    """
    state = government.get('state', {})
    attributes = government.get('attributes', {})
    
    # Simulate goal achievement based on governance preference and resources
    governance_preference = attributes.get('governance_preference', 'fairness')
    financial_resources = attributes.get('financial_resources', 100)
    technical_capability = attributes.get('technical_capability', 80)
    
    # Base achievement rate depends on resources and capabilities
    base_rate = (financial_resources + technical_capability) / 200
    
    # Adjust based on governance preference alignment
    # This is a simplified calculation
    policy_alignment = 0.8  # Assume good policy alignment
    
    goal_achievement = min(1.0, base_rate * policy_alignment)
    
    return goal_achievement


def calculate_policy_effectiveness(government: Dict[str, Any]) -> float:
    """
    Calculate policy effectiveness
    
    Args:
        government: Government agent state
        
    Returns:
        Policy effectiveness score (0-1)
    """
    attributes = government.get('attributes', {})
    state = government.get('state', {})
    
    # Policy effectiveness based on multiple factors
    policy_toolkit_size = len(attributes.get('policy_toolkit', []))
    information_transparency = attributes.get('information_transparency', 70)
    platform_regulation = attributes.get('platform_regulation', 90)
    
    # Normalize and combine factors
    toolkit_score = min(1.0, policy_toolkit_size / 5)  # Assume max 5 tools
    transparency_score = information_transparency / 100
    regulation_score = platform_regulation / 100
    
    # Weighted average
    effectiveness = (
        toolkit_score * 0.3 + 
        transparency_score * 0.3 + 
        regulation_score * 0.4
    )
    
    return effectiveness


def calculate_overall_status(
    resident_metrics: Dict[str, float],
    enterprise_metrics: Dict[str, float], 
    government_metrics: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate overall system status
    
    Args:
        resident_metrics: Resident metrics
        enterprise_metrics: Enterprise metrics
        government_metrics: Government metrics
        
    Returns:
        Overall status indicators
    """
    # System health score (weighted average of key metrics)
    system_health = (
        resident_metrics.get('avg_satisfaction', 0.0) / 5 * 0.3 +  # Normalize to 0-1
        enterprise_metrics.get('avg_innovation_level', 0.0) / 100 * 0.3 +
        government_metrics.get('goal_achievement_rate', 0.0) * 0.4
    )
    
    # Stakeholder balance (low variance = better balance)
    stakeholder_scores = [
        resident_metrics.get('avg_satisfaction', 0.0) / 5,
        enterprise_metrics.get('avg_innovation_level', 0.0) / 100,
        government_metrics.get('goal_achievement_rate', 0.0)
    ]
    
    stakeholder_balance = 1.0 - min(1.0, np.std(stakeholder_scores))
    
    # Sustainability indicator
    sustainability = (
        government_metrics.get('resource_utilization', 0.0) * 0.4 +
        enterprise_metrics.get('avg_compliance_rate', 0.0) / 100 * 0.3 +
        resident_metrics.get('digital_adoption_rate', 0.0) * 0.3
    )
    
    return {
        'system_health': float(system_health),
        'stakeholder_balance': float(stakeholder_balance),
        'sustainability': float(sustainability)
    }