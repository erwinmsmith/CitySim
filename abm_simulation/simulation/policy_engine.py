"""
Policy intervention engine for ABM digital governance simulation
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class PolicyEngine:
    """Engine for applying policy interventions to the simulation"""
    
    def __init__(self, policies_config: Dict[str, Any]):
        """
        Initialize PolicyEngine
        
        Args:
            policies_config: Policy configuration from JSON
        """
        self.policies = policies_config.copy()
        self.applied_policies = []
        self.policy_history = []
    
    def apply(
        self,
        government: Any,
        enterprises: List[Any],
        residents: List[Any],
        environment: Any,
        policy_interventions: List[str]
    ):
        """
        Apply policy interventions to agents and environment
        
        Args:
            government: Government agent
            enterprises: List of enterprise agents
            residents: List of resident agents
            environment: Environment instance
            policy_interventions: List of policy names to apply
        """
        for policy_name in policy_interventions:
            if policy_name in self.policies:
                policy_config = self.policies[policy_name]
                self._apply_single_policy(
                    policy_name, policy_config, 
                    government, enterprises, residents, environment
                )
                
                # Track applied policies
                if policy_name not in self.applied_policies:
                    self.applied_policies.append(policy_name)
                    logger.info(f"Applied policy intervention: {policy_name}")
            else:
                logger.warning(f"Unknown policy intervention: {policy_name}")
    
    def _apply_single_policy(
        self,
        policy_name: str,
        policy_config: Dict[str, Any],
        government: Any,
        enterprises: List[Any], 
        residents: List[Any],
        environment: Any
    ):
        """Apply a single policy intervention"""
        target = policy_config.get('target', '')
        
        if target == 'resident':
            self._apply_resident_policy(policy_name, policy_config, residents)
        elif target == 'government_enterprise':
            self._apply_government_enterprise_policy(
                policy_name, policy_config, government, enterprises
            )
        elif target == 'environment':
            self._apply_environment_policy(policy_name, policy_config, environment)
        elif target == 'government':
            self._apply_government_policy(policy_name, policy_config, government)
        elif target == 'enterprise':
            self._apply_enterprise_policy(policy_name, policy_config, enterprises)
        
        # Record policy application
        self.policy_history.append({
            'policy_name': policy_name,
            'target': target,
            'config': policy_config.copy()
        })
    
    def _apply_resident_policy(
        self,
        policy_name: str,
        policy_config: Dict[str, Any],
        residents: List[Any]
    ):
        """Apply policy targeting residents"""
        attribute_changes = policy_config.get('attribute_change', {})
        behavior_changes = policy_config.get('behavior_change', {})
        
        # Apply to all residents or subset based on policy
        target_residents = residents
        
        # For digital literacy training, focus on lower literacy residents
        if policy_name == 'digital_literacy_training':
            target_residents = [
                r for r in residents 
                if r.attributes.get('information_literacy', 60) < 70
            ]
        
        for resident in target_residents:
            # Apply attribute changes
            for attr_name, change_str in attribute_changes.items():
                if hasattr(resident, 'attributes') and attr_name in resident.attributes:
                    change = self._parse_change_value(change_str)
                    old_value = resident.attributes[attr_name]
                    new_value = min(100, max(0, old_value + change))
                    resident.attributes[attr_name] = new_value
                    logger.debug(f"Updated {attr_name}: {old_value} -> {new_value}")
            
            # Apply behavior changes (modify probabilities for future decisions)
            for behavior_name, change_str in behavior_changes.items():
                change = self._parse_change_value(change_str)
                if not hasattr(resident, 'behavior_modifiers'):
                    resident.behavior_modifiers = {}
                resident.behavior_modifiers[behavior_name] = change
    
    def _apply_government_enterprise_policy(
        self,
        policy_name: str,
        policy_config: Dict[str, Any],
        government: Any,
        enterprises: List[Any]
    ):
        """Apply policy affecting government-enterprise relationships"""
        rule_changes = policy_config.get('rule_change', {})
        
        # Store rule modifications for interaction engine
        if not hasattr(government, 'policy_modifiers'):
            government.policy_modifiers = {}
        
        for rule_name, rule_change in rule_changes.items():
            if rule_name not in government.policy_modifiers:
                government.policy_modifiers[rule_name] = {}
            
            for param, change_str in rule_change.items():
                change = self._parse_change_value(change_str)
                government.policy_modifiers[rule_name][param] = change
                logger.debug(f"Modified rule {rule_name}.{param} by {change}")
        
        # Apply specific policy effects
        if policy_name == 'data_open_sharing':
            # Increase data sharing willingness for enterprises
            for enterprise in enterprises:
                if hasattr(enterprise, 'attributes'):
                    current_strategy = enterprise.attributes.get('data_collection_strategy', 'compliant')
                    if current_strategy == 'compliant':
                        enterprise.attributes['data_sharing_willingness'] = 0.8
        
        elif policy_name == 'algorithm_regulation':
            # Increase compliance requirements
            for enterprise in enterprises:
                if hasattr(enterprise, 'attributes'):
                    current_compliance = enterprise.attributes.get('data_usage_compliance', 90)
                    enterprise.attributes['data_usage_compliance'] = min(100, current_compliance + 5)
    
    def _apply_environment_policy(
        self,
        policy_name: str,
        policy_config: Dict[str, Any],
        environment: Any
    ):
        """Apply policy targeting environment"""
        # Delegate to environment's policy application method
        environment.apply_policy_intervention(policy_name, policy_config)
    
    def _apply_government_policy(
        self,
        policy_name: str,
        policy_config: Dict[str, Any],
        government: Any
    ):
        """Apply policy targeting government specifically"""
        attribute_changes = policy_config.get('attribute_change', {})
        
        for attr_name, change_str in attribute_changes.items():
            if hasattr(government, 'attributes') and attr_name in government.attributes:
                change = self._parse_change_value(change_str)
                old_value = government.attributes[attr_name]
                new_value = min(100, max(0, old_value + change))
                government.attributes[attr_name] = new_value
                logger.debug(f"Government {attr_name}: {old_value} -> {new_value}")
    
    def _apply_enterprise_policy(
        self,
        policy_name: str,
        policy_config: Dict[str, Any],
        enterprises: List[Any]
    ):
        """Apply policy targeting enterprises specifically"""
        attribute_changes = policy_config.get('attribute_change', {})
        
        for enterprise in enterprises:
            for attr_name, change_str in attribute_changes.items():
                if hasattr(enterprise, 'attributes') and attr_name in enterprise.attributes:
                    change = self._parse_change_value(change_str)
                    old_value = enterprise.attributes[attr_name]
                    new_value = min(100, max(0, old_value + change))
                    enterprise.attributes[attr_name] = new_value
    
    def _parse_change_value(self, change_str: str) -> float:
        """
        Parse change value from string format
        
        Args:
            change_str: Change value as string (e.g., "+20", "-10", "+0.3")
            
        Returns:
            Numeric change value
        """
        try:
            if isinstance(change_str, (int, float)):
                return float(change_str)
            
            change_str = str(change_str).strip()
            if change_str.startswith(('+', '-')):
                return float(change_str)
            else:
                return float(change_str)
        except ValueError:
            logger.warning(f"Could not parse change value: {change_str}")
            return 0.0
    
    def get_policy_effects(self) -> Dict[str, Any]:
        """
        Get summary of applied policy effects
        
        Returns:
            Dictionary summarizing policy effects
        """
        return {
            'applied_policies': self.applied_policies.copy(),
            'policy_count': len(self.applied_policies),
            'policy_history': self.policy_history.copy()
        }
    
    def simulate_policy_impact(
        self,
        policy_name: str,
        agents: Dict[str, Any],
        environment: Any
    ) -> Dict[str, Any]:
        """
        Simulate the potential impact of a policy without applying it
        
        Args:
            policy_name: Name of policy to simulate
            agents: Dictionary containing all agent types
            environment: Environment instance
            
        Returns:
            Dictionary with simulated impact assessment
        """
        if policy_name not in self.policies:
            return {'error': f'Unknown policy: {policy_name}'}
        
        policy_config = self.policies[policy_name]
        target = policy_config.get('target', '')
        
        impact_assessment = {
            'policy_name': policy_name,
            'target': target,
            'estimated_effects': {}
        }
        
        # Estimate effects based on policy type
        if target == 'resident':
            affected_residents = len(agents.get('residents', []))
            attribute_changes = policy_config.get('attribute_change', {})
            
            impact_assessment['estimated_effects'] = {
                'affected_residents': affected_residents,
                'attribute_improvements': list(attribute_changes.keys())
            }
        
        elif target == 'environment':
            attribute_changes = policy_config.get('attribute_change', {})
            impact_assessment['estimated_effects'] = {
                'infrastructure_improvements': attribute_changes
            }
        
        elif target == 'government_enterprise':
            rule_changes = policy_config.get('rule_change', {})
            impact_assessment['estimated_effects'] = {
                'interaction_rule_changes': list(rule_changes.keys())
            }
        
        return impact_assessment
    
    def recommend_policies(
        self,
        current_metrics: Dict[str, Any],
        target_improvements: List[str]
    ) -> List[str]:
        """
        Recommend policies based on current metrics and desired improvements
        
        Args:
            current_metrics: Current simulation metrics
            target_improvements: List of areas to improve
            
        Returns:
            List of recommended policy names
        """
        recommendations = []
        
        # Analyze current metrics and recommend appropriate policies
        fairness_metrics = current_metrics.get('fairness', {})
        efficiency_metrics = current_metrics.get('efficiency', {})
        
        # Recommend digital literacy training if digital divide is high
        if (fairness_metrics.get('digital_divide_index', 0) > 0.3 or
            'digital_equity' in target_improvements):
            recommendations.append('digital_literacy_training')
        
        # Recommend infrastructure investment if service access gaps are high
        if (fairness_metrics.get('service_access_gini', 0) > 0.4 or
            'infrastructure' in target_improvements):
            recommendations.append('inclusive_infrastructure')
        
        # Recommend data sharing if efficiency is low
        if (efficiency_metrics.get('resource_utilization', 0) < 0.6 or
            'efficiency' in target_improvements):
            recommendations.append('data_open_sharing')
        
        # Recommend algorithm regulation if compliance issues
        collaboration_metrics = current_metrics.get('collaboration', {})
        if (collaboration_metrics.get('conflict_rate', 0) > 0.2 or
            'regulation' in target_improvements):
            recommendations.append('algorithm_regulation')
        
        # Remove already applied policies from recommendations
        recommendations = [p for p in recommendations if p not in self.applied_policies]
        
        return recommendations