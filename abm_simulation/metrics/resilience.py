"""
Governance resilience metrics calculation
"""
import numpy as np
from typing import List, Dict, Any


def calculate_resilience(simulation_records: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate governance resilience indicators
    
    Args:
        simulation_records: List of simulation round records
        
    Returns:
        Dictionary containing resilience metrics
    """
    if not simulation_records:
        return {
            'system_recovery_speed': 0.0,
            'service_disruption_rate': 0.0,
            'adaptive_capacity': 0.0,
            'stability_index': 0.0
        }
    
    recovery_speed = calculate_system_recovery_speed(simulation_records)
    disruption_rate = calculate_service_disruption_rate(simulation_records)
    adaptive_capacity = calculate_adaptive_capacity(simulation_records)
    stability_index = calculate_stability_index(simulation_records)
    
    return {
        'system_recovery_speed': float(recovery_speed),
        'service_disruption_rate': float(disruption_rate),
        'adaptive_capacity': float(adaptive_capacity),
        'stability_index': float(stability_index)
    }


def calculate_system_recovery_speed(simulation_records: List[Dict[str, Any]]) -> float:
    """
    Calculate system recovery speed during emergencies
    
    Args:
        simulation_records: List of simulation records
        
    Returns:
        Average recovery speed (higher = faster recovery)
    """
    if not simulation_records:
        return 0.0
    
    emergency_events = []
    
    for i, record in enumerate(simulation_records):
        interactions = record.get('interactions', [])
        
        # Look for emergency-related interactions
        for interaction in interactions:
            if interaction.get('type') == 'emergency_response':
                emergency_events.append({
                    'round': i,
                    'response_time': interaction.get('response_time', 1.0),
                    'recovery_time': interaction.get('recovery_time', 5.0)
                })
    
    if not emergency_events:
        # No emergencies occurred, assume good resilience
        return 0.8
    
    # Calculate average recovery speed (inverse of recovery time)
    recovery_times = [event['recovery_time'] for event in emergency_events]
    avg_recovery_time = np.mean(recovery_times)
    
    # Convert to speed metric (0-1 scale)
    max_recovery_time = 10.0  # Assume max recovery time is 10 rounds
    recovery_speed = max(0.0, 1.0 - (avg_recovery_time / max_recovery_time))
    
    return recovery_speed


def calculate_service_disruption_rate(simulation_records: List[Dict[str, Any]]) -> float:
    """
    Calculate service disruption rate
    
    Args:
        simulation_records: List of simulation records
        
    Returns:
        Service disruption rate (lower = more resilient)
    """
    if not simulation_records:
        return 0.0
    
    total_rounds = len(simulation_records)
    disrupted_rounds = 0
    
    for record in simulation_records:
        environment = record.get('environment', {})
        service_level = environment.get('service_availability', 1.0)
        
        # Consider service disrupted if availability < 0.8
        if service_level < 0.8:
            disrupted_rounds += 1
    
    disruption_rate = disrupted_rounds / total_rounds if total_rounds > 0 else 0.0
    return disruption_rate


def calculate_adaptive_capacity(simulation_records: List[Dict[str, Any]]) -> float:
    """
    Calculate system adaptive capacity
    
    Args:
        simulation_records: List of simulation records
        
    Returns:
        Adaptive capacity score (0-1)
    """
    if len(simulation_records) < 10:
        return 0.5  # Default value for short simulations
    
    # Measure system's ability to improve over time
    early_records = simulation_records[:len(simulation_records)//3]
    late_records = simulation_records[-len(simulation_records)//3:]
    
    # Calculate average efficiency in early vs late periods
    early_efficiency = calculate_period_efficiency(early_records)
    late_efficiency = calculate_period_efficiency(late_records)
    
    # Adaptive capacity is the improvement over time
    improvement = late_efficiency - early_efficiency
    
    # Normalize to 0-1 scale
    adaptive_capacity = max(0.0, min(1.0, 0.5 + improvement))
    
    return adaptive_capacity


def calculate_period_efficiency(records: List[Dict[str, Any]]) -> float:
    """
    Calculate efficiency for a period of records
    
    Args:
        records: List of simulation records for a specific period
        
    Returns:
        Average efficiency score for the period
    """
    if not records:
        return 0.0
    
    efficiency_scores = []
    
    for record in records:
        interactions = record.get('interactions', [])
        
        # Calculate efficiency based on successful interactions
        total_interactions = len(interactions)
        successful_interactions = len([
            i for i in interactions 
            if i.get('outcome') == 'success'
        ])
        
        if total_interactions > 0:
            efficiency = successful_interactions / total_interactions
            efficiency_scores.append(efficiency)
    
    return np.mean(efficiency_scores) if efficiency_scores else 0.0


def calculate_stability_index(simulation_records: List[Dict[str, Any]]) -> float:
    """
    Calculate system stability index
    
    Args:
        simulation_records: List of simulation records
        
    Returns:
        Stability index (higher = more stable)
    """
    if len(simulation_records) < 2:
        return 1.0
    
    # Calculate variance in key system metrics over time
    service_levels = []
    satisfaction_levels = []
    
    for record in simulation_records:
        environment = record.get('environment', {})
        agents = record.get('agents', {})
        
        service_level = environment.get('service_availability', 1.0)
        service_levels.append(service_level)
        
        # Calculate average resident satisfaction
        residents = agents.get('residents', [])
        if residents:
            avg_satisfaction = np.mean([
                r.get('satisfaction', 3.0) for r in residents
            ])
            satisfaction_levels.append(avg_satisfaction / 5.0)  # Normalize to 0-1
        else:
            satisfaction_levels.append(0.6)  # Default
    
    # Stability is inverse of variance (lower variance = higher stability)
    service_variance = np.var(service_levels) if len(service_levels) > 1 else 0.0
    satisfaction_variance = np.var(satisfaction_levels) if len(satisfaction_levels) > 1 else 0.0
    
    # Combine variances and convert to stability index
    total_variance = (service_variance + satisfaction_variance) / 2
    stability_index = max(0.0, 1.0 - total_variance * 10)  # Scale factor
    
    return min(1.0, stability_index)