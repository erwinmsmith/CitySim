"""
Environment class for ABM digital governance simulation
"""
import random
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class Environment:
    """Environment class managing infrastructure and policy context"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Environment
        
        Args:
            config: Environment configuration from JSON
        """
        self.config = config.copy()
        self.digital_infrastructure = config.get('digital_infrastructure', {}).copy()
        self.physical_infrastructure = config.get('physical_infrastructure', {}).copy()
        self.policy_environment = config.get('policy_environment', {}).copy()
        
        # Dynamic state variables
        self.service_availability = 1.0
        self.system_load = 0.5
        self.emergency_status = False
        self.update_count = 0
        
        # Service quality by area
        self.service_quality = {
            'core_area': 0.9,
            'urban_rural_fringe': 0.7,
            'rural': 0.6
        }
        
        # Infrastructure utilization
        self.infrastructure_utilization = {
            'digital': 0.6,
            'physical': 0.7
        }
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get current environment context for agents
        
        Returns:
            Environment context dictionary
        """
        # Calculate average infrastructure level
        avg_digital = sum(self.digital_infrastructure.values()) / len(self.digital_infrastructure)
        avg_physical = sum(self.physical_infrastructure.values()) / len(self.physical_infrastructure)
        
        return {
            'digital_infrastructure': self.digital_infrastructure,
            'physical_infrastructure': self.physical_infrastructure,
            'policy_environment': self.policy_environment,
            'service_availability': self.service_availability,
            'system_load': self.system_load,
            'emergency_status': self.emergency_status,
            'service_quality': self.service_quality,
            'infrastructure_utilization': self.infrastructure_utilization,
            # Additional context for prompt variables
            'environment_context': f"Service availability: {self.service_availability:.2f}, System load: {self.system_load:.2f}",
            'infrastructure_level': (avg_digital + avg_physical) / 2,
            'available_services': "Digital governance services, Public services, Enterprise services",
            'regulation_intensity': "Medium to High" if self.system_load > 0.7 else "Medium",
            'available_data': "Government open data, Enterprise reports, Public feedback",
            'market_conditions': "Stable" if not self.emergency_status else "Challenging",
            'competition_level': "Medium",
            'recent_interactions': "Regular service requests and responses"
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get current environment state"""
        return {
            'digital_infrastructure': self.digital_infrastructure.copy(),
            'physical_infrastructure': self.physical_infrastructure.copy(),
            'policy_environment': self.policy_environment.copy(),
            'service_availability': self.service_availability,
            'system_load': self.system_load,
            'emergency_status': self.emergency_status,
            'service_quality': self.service_quality.copy(),
            'infrastructure_utilization': self.infrastructure_utilization.copy(),
            'update_count': self.update_count
        }
    
    def update(self, interactions: List[Dict[str, Any]]):
        """
        Update environment based on agent interactions
        
        Args:
            interactions: List of interactions from this round
        """
        self.update_count += 1
        
        # Update system load based on interactions
        self._update_system_load(interactions)
        
        # Update service availability
        self._update_service_availability(interactions)
        
        # Check for emergency events
        self._check_emergency_events()
        
        # Update infrastructure utilization
        self._update_infrastructure_utilization(interactions)
        
        # Update service quality by area
        self._update_service_quality(interactions)
        
        # Random environmental changes
        self._apply_random_changes()
    
    def _update_system_load(self, interactions: List[Dict[str, Any]]):
        """Update system load based on interactions"""
        # Count service requests
        service_requests = len([
            i for i in interactions 
            if i.get('type') in ['service_request', 'data_request', 'service_use']
        ])
        
        # Calculate load factor
        load_factor = min(1.0, service_requests / 50)  # Assume capacity of 50 requests
        
        # Smooth load changes
        self.system_load = 0.7 * self.system_load + 0.3 * load_factor
        self.system_load = max(0.0, min(1.0, self.system_load))
    
    def _update_service_availability(self, interactions: List[Dict[str, Any]]):
        """Update service availability based on system load"""
        # Service availability decreases with high load
        if self.system_load > 0.8:
            availability_change = -0.05
        elif self.system_load < 0.3:
            availability_change = 0.02
        else:
            availability_change = 0.0
        
        # Check for system failures in interactions
        failures = [
            i for i in interactions 
            if i.get('outcome') == 'system_failure'
        ]
        
        if failures:
            availability_change -= 0.1 * len(failures)
        
        # Update availability
        self.service_availability += availability_change
        self.service_availability = max(0.0, min(1.0, self.service_availability))
    
    def _check_emergency_events(self):
        """Check for random emergency events"""
        # 2% chance of emergency event per round
        if random.random() < 0.02:
            self.emergency_status = True
            self.service_availability *= 0.7  # Reduce service availability
            logger.info(f"Emergency event triggered at round {self.update_count}")
        elif self.emergency_status:
            # 30% chance to resolve emergency each round
            if random.random() < 0.3:
                self.emergency_status = False
                logger.info(f"Emergency resolved at round {self.update_count}")
    
    def _update_infrastructure_utilization(self, interactions: List[Dict[str, Any]]):
        """Update infrastructure utilization"""
        # Count digital vs physical service usage
        digital_usage = len([
            i for i in interactions 
            if i.get('service_type') == 'digital'
        ])
        
        physical_usage = len([
            i for i in interactions 
            if i.get('service_type') == 'physical'
        ])
        
        total_interactions = len(interactions)
        if total_interactions > 0:
            digital_ratio = digital_usage / total_interactions
            physical_ratio = physical_usage / total_interactions
            
            # Update utilization (smooth changes)
            self.infrastructure_utilization['digital'] = (
                0.8 * self.infrastructure_utilization['digital'] + 
                0.2 * digital_ratio
            )
            self.infrastructure_utilization['physical'] = (
                0.8 * self.infrastructure_utilization['physical'] + 
                0.2 * physical_ratio
            )
    
    def _update_service_quality(self, interactions: List[Dict[str, Any]]):
        """Update service quality by area"""
        # Group interactions by area
        area_interactions = {
            'core_area': [],
            'urban_rural_fringe': [],
            'rural': []
        }
        
        for interaction in interactions:
            area = interaction.get('area', 'core_area')
            if area in area_interactions:
                area_interactions[area].append(interaction)
        
        # Update quality based on successful interactions
        for area, area_interactions_list in area_interactions.items():
            if area_interactions_list:
                success_rate = len([
                    i for i in area_interactions_list 
                    if i.get('outcome') == 'success'
                ]) / len(area_interactions_list)
                
                # Update service quality (smooth changes)
                quality_change = (success_rate - 0.7) * 0.05  # Target 70% success rate
                self.service_quality[area] += quality_change
                self.service_quality[area] = max(0.0, min(1.0, self.service_quality[area]))
    
    def _apply_random_changes(self):
        """Apply small random changes to environment"""
        # Small random changes to infrastructure (±1%)
        for area in self.digital_infrastructure:
            change = random.uniform(-1, 1)
            self.digital_infrastructure[area] = max(0, min(100, 
                self.digital_infrastructure[area] + change))
        
        # Emergency events can degrade infrastructure
        if self.emergency_status:
            for area in self.digital_infrastructure:
                self.digital_infrastructure[area] *= 0.98  # 2% degradation
    
    def apply_policy_intervention(self, policy_name: str, policy_config: Dict[str, Any]):
        """
        Apply policy intervention to environment
        
        Args:
            policy_name: Name of the policy
            policy_config: Policy configuration
        """
        target = policy_config.get('target', '')
        
        if target == 'environment':
            attribute_changes = policy_config.get('attribute_change', {})
            
            # Apply infrastructure improvements
            if 'digital_infrastructure' in attribute_changes:
                infra_changes = attribute_changes['digital_infrastructure']
                for area, change_str in infra_changes.items():
                    if area in self.digital_infrastructure:
                        change = float(change_str.replace('+', ''))
                        self.digital_infrastructure[area] = min(100,
                            self.digital_infrastructure[area] + change)
                        logger.info(f"Applied policy {policy_name}: {area} +{change}")
            
            # Apply physical infrastructure improvements
            if 'physical_infrastructure' in attribute_changes:
                infra_changes = attribute_changes['physical_infrastructure']
                for area, change_str in infra_changes.items():
                    if area in self.physical_infrastructure:
                        change = float(change_str.replace('+', ''))
                        self.physical_infrastructure[area] = min(100,
                            self.physical_infrastructure[area] + change)
    
    def get_infrastructure_level(self, area: str) -> float:
        """
        Get combined infrastructure level for an area
        
        Args:
            area: Area type (core_area/urban_rural_fringe/rural)
            
        Returns:
            Combined infrastructure level (0-100)
        """
        digital_level = self.digital_infrastructure.get(area, 50)
        physical_level = self.physical_infrastructure.get(area, 50)
        
        # Weighted average (digital infrastructure weighted more heavily)
        combined_level = 0.6 * digital_level + 0.4 * physical_level
        return combined_level
    
    def get_area_context(self, area: str) -> Dict[str, Any]:
        """
        Get area-specific context
        
        Args:
            area: Area type
            
        Returns:
            Area context dictionary
        """
        return {
            'digital_infrastructure_level': self.digital_infrastructure.get(area, 50),
            'physical_infrastructure_level': self.physical_infrastructure.get(area, 50),
            'service_quality': self.service_quality.get(area, 0.6),
            'combined_infrastructure': self.get_infrastructure_level(area)
        }