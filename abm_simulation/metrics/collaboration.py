"""
Governance collaboration metrics calculation
"""
import numpy as np
from typing import List, Dict, Any


def calculate_collaboration(simulation_records: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate governance collaboration indicators
    
    Args:
        simulation_records: List of simulation round records
        
    Returns:
        Dictionary containing collaboration metrics
    """
    if not simulation_records:
        return {
            'cross_department_sharing_frequency': 0.0,
            'joint_action_rate': 0.0,
            'conflict_rate': 0.0,
            'cooperation_index': 0.0,
            'trust_network_density': 0.0
        }
    
    sharing_frequency = calculate_information_sharing_frequency(simulation_records)
    joint_action_rate = calculate_joint_action_rate(simulation_records)
    conflict_rate = calculate_conflict_rate(simulation_records)
    cooperation_index = calculate_cooperation_index(simulation_records)
    trust_density = calculate_trust_network_density(simulation_records)
    
    return {
        'cross_department_sharing_frequency': float(sharing_frequency),
        'joint_action_rate': float(joint_action_rate),
        'conflict_rate': float(conflict_rate),
        'cooperation_index': float(cooperation_index),
        'trust_network_density': float(trust_density)
    }


def calculate_information_sharing_frequency(simulation_records: List[Dict[str, Any]]) -> float:
    """
    Calculate cross-department information sharing frequency
    
    Args:
        simulation_records: List of simulation records
        
    Returns:
        Information sharing frequency (interactions per round)
    """
    if not simulation_records:
        return 0.0
    
    total_sharing_events = 0
    total_rounds = len(simulation_records)
    
    for record in simulation_records:
        interactions = record.get('interactions', [])
        
        # Count information sharing interactions
        sharing_events = [
            i for i in interactions 
            if i.get('type') in ['data_sharing', 'information_exchange', 'coordination']
        ]
        
        total_sharing_events += len(sharing_events)
    
    # Average sharing events per round
    sharing_frequency = total_sharing_events / total_rounds if total_rounds > 0 else 0.0
    
    return sharing_frequency


def calculate_joint_action_rate(simulation_records: List[Dict[str, Any]]) -> float:
    """
    Calculate joint action occurrence rate
    
    Args:
        simulation_records: List of simulation records
        
    Returns:
        Joint action rate (0-1)
    """
    if not simulation_records:
        return 0.0
    
    total_interactions = 0
    joint_actions = 0
    
    for record in simulation_records:
        interactions = record.get('interactions', [])
        total_interactions += len(interactions)
        
        # Count multi-agent collaborative actions
        for interaction in interactions:
            participants = interaction.get('participants', [])
            if len(participants) > 1:
                # Check if it's a collaborative action
                action_type = interaction.get('type', '')
                if action_type in [
                    'joint_project', 'collaborative_service', 
                    'multi_agency_response', 'partnership'
                ]:
                    joint_actions += 1
    
    joint_action_rate = joint_actions / total_interactions if total_interactions > 0 else 0.0
    
    return joint_action_rate


def calculate_conflict_rate(simulation_records: List[Dict[str, Any]]) -> float:
    """
    Calculate inter-agent conflict rate
    
    Args:
        simulation_records: List of simulation records
        
    Returns:
        Conflict rate (0-1, lower is better)
    """
    if not simulation_records:
        return 0.0
    
    total_interactions = 0
    conflicts = 0
    
    for record in simulation_records:
        interactions = record.get('interactions', [])
        total_interactions += len(interactions)
        
        # Count conflictual interactions
        for interaction in interactions:
            outcome = interaction.get('outcome', 'neutral')
            if outcome in ['conflict', 'disagreement', 'failed_negotiation']:
                conflicts += 1
            
            # Also check for regulatory conflicts
            if (interaction.get('type') == 'regulation' and 
                interaction.get('compliance', True) == False):
                conflicts += 1
    
    conflict_rate = conflicts / total_interactions if total_interactions > 0 else 0.0
    
    return conflict_rate


def calculate_cooperation_index(simulation_records: List[Dict[str, Any]]) -> float:
    """
    Calculate overall cooperation index
    
    Args:
        simulation_records: List of simulation records
        
    Returns:
        Cooperation index (0-1, higher is better)
    """
    if not simulation_records:
        return 0.0
    
    cooperation_scores = []
    
    for record in simulation_records:
        interactions = record.get('interactions', [])
        
        if not interactions:
            cooperation_scores.append(0.5)  # Neutral score
            continue
        
        # Score each interaction for cooperation level
        interaction_scores = []
        
        for interaction in interactions:
            outcome = interaction.get('outcome', 'neutral')
            interaction_type = interaction.get('type', '')
            
            # Score based on outcome
            if outcome in ['success', 'mutual_benefit', 'win_win']:
                score = 1.0
            elif outcome in ['partial_success', 'compromise']:
                score = 0.7
            elif outcome in ['neutral', 'no_change']:
                score = 0.5
            elif outcome in ['conflict', 'failed']:
                score = 0.1
            else:
                score = 0.5
            
            # Bonus for cooperative interaction types
            if interaction_type in [
                'data_sharing', 'joint_project', 'collaboration',
                'partnership', 'mutual_support'
            ]:
                score = min(1.0, score + 0.2)
            
            interaction_scores.append(score)
        
        # Average cooperation score for this round
        round_cooperation = np.mean(interaction_scores)
        cooperation_scores.append(round_cooperation)
    
    # Overall cooperation index
    cooperation_index = np.mean(cooperation_scores)
    
    return cooperation_index


def calculate_trust_network_density(simulation_records: List[Dict[str, Any]]) -> float:
    """
    Calculate trust network density
    
    Args:
        simulation_records: List of simulation records
        
    Returns:
        Trust network density (0-1)
    """
    if not simulation_records:
        return 0.0
    
    # Build trust network from interactions
    trust_relationships = set()
    all_agents = set()
    
    for record in simulation_records:
        interactions = record.get('interactions', [])
        
        for interaction in interactions:
            participants = interaction.get('participants', [])
            outcome = interaction.get('outcome', 'neutral')
            
            # Add agents to the set
            for agent in participants:
                all_agents.add(agent)
            
            # Add trust relationships for positive outcomes
            if (len(participants) == 2 and 
                outcome in ['success', 'mutual_benefit', 'win_win']):
                
                agent1, agent2 = participants[0], participants[1]
                # Add bidirectional trust relationship
                trust_relationships.add((agent1, agent2))
                trust_relationships.add((agent2, agent1))
    
    # Calculate network density
    num_agents = len(all_agents)
    if num_agents < 2:
        return 0.0
    
    # Maximum possible relationships (directed graph)
    max_relationships = num_agents * (num_agents - 1)
    
    # Actual trust relationships
    actual_relationships = len(trust_relationships)
    
    # Network density
    density = actual_relationships / max_relationships if max_relationships > 0 else 0.0
    
    return density


def calculate_stakeholder_engagement(simulation_records: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate stakeholder engagement metrics
    
    Args:
        simulation_records: List of simulation records
        
    Returns:
        Engagement metrics by stakeholder type
    """
    if not simulation_records:
        return {
            'government_engagement': 0.0,
            'enterprise_engagement': 0.0,
            'resident_engagement': 0.0
        }
    
    engagement_by_type = {
        'government': [],
        'enterprise': [],
        'resident': []
    }
    
    for record in simulation_records:
        interactions = record.get('interactions', [])
        
        # Count active participation by agent type
        type_counts = {'government': 0, 'enterprise': 0, 'resident': 0}
        
        for interaction in interactions:
            participants = interaction.get('participants', [])
            for participant in participants:
                agent_type = participant.split('_')[0]  # Assume naming convention
                if agent_type in type_counts:
                    type_counts[agent_type] += 1
        
        # Calculate engagement rates for this round
        total_interactions = len(interactions)
        if total_interactions > 0:
            for agent_type in type_counts:
                engagement_rate = type_counts[agent_type] / total_interactions
                engagement_by_type[agent_type].append(engagement_rate)
        else:
            for agent_type in type_counts:
                engagement_by_type[agent_type].append(0.0)
    
    # Calculate average engagement rates
    return {
        f'{agent_type}_engagement': float(np.mean(scores)) if scores else 0.0
        for agent_type, scores in engagement_by_type.items()
    }