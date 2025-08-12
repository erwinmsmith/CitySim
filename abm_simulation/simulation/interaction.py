"""
Interaction engine for ABM digital governance simulation
"""
import random
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class InteractionEngine:
    """Engine for processing agent interactions based on rules"""
    
    def __init__(self, rules_config: Dict[str, Any]):
        """
        Initialize InteractionEngine
        
        Args:
            rules_config: Interaction rules configuration
        """
        self.rules = rules_config.copy()
        self.interaction_history = []
    
    def process(
        self, 
        government: Any,
        enterprises: List[Any], 
        residents: List[Any],
        gov_decision: Dict[str, Any],
        ent_decisions: List[Dict[str, Any]],
        res_decisions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process all agent interactions for one round
        
        Args:
            government: Government agent
            enterprises: List of enterprise agents
            residents: List of resident agents
            gov_decision: Government decision
            ent_decisions: List of enterprise decisions
            res_decisions: List of resident decisions
            
        Returns:
            List of interaction results
        """
        interactions = []
        
        # Process government-enterprise interactions
        interactions.extend(
            self._process_government_enterprise_interactions(
                government, enterprises, gov_decision, ent_decisions
            )
        )
        
        # Process government-resident interactions
        interactions.extend(
            self._process_government_resident_interactions(
                government, residents, gov_decision, res_decisions
            )
        )
        
        # Process enterprise-resident interactions
        interactions.extend(
            self._process_enterprise_resident_interactions(
                enterprises, residents, ent_decisions, res_decisions
            )
        )
        
        # Process resident-resident interactions (limited)
        interactions.extend(
            self._process_resident_resident_interactions(
                residents, res_decisions
            )
        )
        
        # Store interaction history
        self.interaction_history.extend(interactions)
        
        # Update agent states based on interactions
        self._update_agent_states(government, enterprises, residents, interactions)
        
        return interactions
    
    def _process_government_enterprise_interactions(
        self,
        government: Any,
        enterprises: List[Any],
        gov_decision: Dict[str, Any], 
        ent_decisions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process government-enterprise interactions"""
        interactions = []
        rules = self.rules.get('government_enterprise', {})
        
        # Process government actions targeting enterprises
        if gov_decision.get('target') in ['enterprises', 'enterprise']:
            for i, enterprise in enumerate(enterprises):
                interaction = self._create_gov_ent_interaction(
                    government, enterprise, gov_decision, rules
                )
                if interaction:
                    interactions.append(interaction)
        
        # Process enterprise actions targeting government
        for i, (enterprise, ent_decision) in enumerate(zip(enterprises, ent_decisions)):
            if ent_decision.get('target') in ['government', 'gov']:
                interaction = self._create_ent_gov_interaction(
                    enterprise, government, ent_decision, rules
                )
                if interaction:
                    interactions.append(interaction)
        
        return interactions
    
    def _process_government_resident_interactions(
        self,
        government: Any,
        residents: List[Any],
        gov_decision: Dict[str, Any],
        res_decisions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process government-resident interactions"""
        interactions = []
        rules = self.rules.get('government_resident', {})
        
        # Process government service provision
        if gov_decision.get('action') == 'service_provision':
            # Select random subset of residents for interaction
            num_interactions = min(20, len(residents))  # Limit interactions per round
            selected_residents = random.sample(residents, num_interactions)
            
            for resident in selected_residents:
                interaction = self._create_service_interaction(
                    government, resident, gov_decision, rules['service_provision']
                )
                interactions.append(interaction)
        
        # Process resident feedback to government
        for i, (resident, res_decision) in enumerate(zip(residents, res_decisions)):
            if (res_decision.get('target') == 'government' and 
                res_decision.get('action') in ['provide_feedback', 'request_service']):
                
                interaction = self._create_resident_gov_interaction(
                    resident, government, res_decision, rules
                )
                if interaction:
                    interactions.append(interaction)
        
        return interactions
    
    def _process_enterprise_resident_interactions(
        self,
        enterprises: List[Any],
        residents: List[Any],
        ent_decisions: List[Dict[str, Any]],
        res_decisions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process enterprise-resident interactions"""
        interactions = []
        rules = self.rules.get('enterprise_resident', {})
        
        # Process enterprise service supply
        for enterprise, ent_decision in zip(enterprises, ent_decisions):
            if ent_decision.get('action') in ['service_development', 'service_promotion']:
                # Select random residents for service interaction
                num_interactions = random.randint(5, 15)
                selected_residents = random.sample(
                    residents, min(num_interactions, len(residents))
                )
                
                for resident in selected_residents:
                    interaction = self._create_enterprise_service_interaction(
                        enterprise, resident, ent_decision, rules
                    )
                    interactions.append(interaction)
        
        return interactions
    
    def _process_resident_resident_interactions(
        self,
        residents: List[Any],
        res_decisions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process resident-resident interactions (information sharing)"""
        interactions = []
        
        # Randomly select pairs for information sharing
        num_interactions = min(10, len(residents) // 10)  # 10% of residents interact
        
        for _ in range(num_interactions):
            if len(residents) >= 2:
                resident1, resident2 = random.sample(residents, 2)
                
                # Check if they are in same area (higher probability)
                if (getattr(resident1, 'area', 'core_area') == 
                    getattr(resident2, 'area', 'core_area')):
                    probability = 0.3
                else:
                    probability = 0.1
                
                if random.random() < probability:
                    interaction = {
                        'type': 'information_sharing',
                        'participants': [
                            getattr(resident1, 'agent_id', 'resident_1'),
                            getattr(resident2, 'agent_id', 'resident_2')
                        ],
                        'outcome': 'success',
                        'effect': 'knowledge_transfer'
                    }
                    interactions.append(interaction)
        
        return interactions
    
    def _create_gov_ent_interaction(
        self,
        government: Any,
        enterprise: Any,
        gov_decision: Dict[str, Any],
        rules: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create government-enterprise interaction"""
        action = gov_decision.get('action', 'regulation')
        
        if action == 'procurement_cooperation':
            return self._create_procurement_interaction(government, enterprise, rules)
        elif action == 'regulation':
            return self._create_regulation_interaction(government, enterprise, rules)
        elif action == 'data_sharing':
            return self._create_data_sharing_interaction(government, enterprise, rules)
        
        return None
    
    def _create_ent_gov_interaction(
        self,
        enterprise: Any,
        government: Any,
        ent_decision: Dict[str, Any],
        rules: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create enterprise-government interaction"""
        action = ent_decision.get('action', 'compliance_reporting')
        
        if action == 'project_bidding':
            return self._create_bidding_interaction(enterprise, government, rules)
        elif action == 'data_request':
            return self._create_data_request_interaction(enterprise, government, rules)
        
        return None
    
    def _create_procurement_interaction(
        self,
        government: Any,
        enterprise: Any,
        rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create procurement cooperation interaction"""
        rule = rules.get('procurement_cooperation', {})
        probability = rule.get('probability', 0.7)
        
        # Success based on probability and enterprise capability
        enterprise_capability = enterprise.state.get('innovation_level', 50) / 100
        success_prob = probability * enterprise_capability
        
        outcome = 'success' if random.random() < success_prob else 'failed'
        
        interaction = {
            'type': 'procurement_cooperation',
            'participants': ['government', getattr(enterprise, 'agent_id', 'enterprise')],
            'outcome': outcome,
            'effect': rule.get('effect', ''),
            'service_type': 'digital'
        }
        
        return interaction
    
    def _create_regulation_interaction(
        self,
        government: Any,
        enterprise: Any,
        rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create regulation interaction"""
        rule = rules.get('regulation', {})
        probability = rule.get('probability', 0.9)
        
        # Compliance based on enterprise compliance rate
        compliance_rate = enterprise.attributes.get('data_usage_compliance', 90) / 100
        compliant = random.random() < compliance_rate
        
        outcome = 'success' if compliant else 'violation'
        
        interaction = {
            'type': 'regulation',
            'participants': ['government', getattr(enterprise, 'agent_id', 'enterprise')],
            'outcome': outcome,
            'effect': rule.get('effect', ''),
            'compliance': compliant
        }
        
        return interaction
    
    def _create_data_sharing_interaction(
        self,
        government: Any,
        enterprise: Any,
        rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create data sharing interaction"""
        rule = rules.get('data_sharing', {})
        probability = rule.get('probability', 0.3)
        
        # Data sharing success based on trust and policy
        gov_transparency = government.attributes.get('information_transparency', 70) / 100
        success_prob = probability * gov_transparency
        
        outcome = 'success' if random.random() < success_prob else 'denied'
        
        interaction = {
            'type': 'data_sharing',
            'participants': ['government', getattr(enterprise, 'agent_id', 'enterprise')],
            'outcome': outcome,
            'effect': rule.get('effect', '')
        }
        
        return interaction
    
    def _create_service_interaction(
        self,
        government: Any,
        resident: Any,
        gov_decision: Dict[str, Any],
        rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create service provision interaction"""
        probability = rule.get('probability', 0.8)
        
        # Service success based on infrastructure and government capability
        area = getattr(resident, 'area', 'core_area')
        # Simulate infrastructure quality impact
        infrastructure_quality = {
            'core_area': 0.9,
            'urban_rural_fringe': 0.7,
            'rural': 0.5
        }.get(area, 0.7)
        
        success_prob = probability * infrastructure_quality
        outcome = 'success' if random.random() < success_prob else 'failed'
        
        interaction = {
            'type': 'service_provision',
            'participants': ['government', getattr(resident, 'agent_id', 'resident')],
            'outcome': outcome,
            'effect': rule.get('effect', ''),
            'area': area,
            'service_type': 'digital' if random.random() > 0.3 else 'physical'
        }
        
        return interaction
    
    def _create_resident_gov_interaction(
        self,
        resident: Any,
        government: Any,
        res_decision: Dict[str, Any],
        rules: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create resident-government interaction"""
        action = res_decision.get('action', 'provide_feedback')
        
        if action == 'provide_feedback':
            rule = rules.get('demand_response', {})
            probability = rule.get('probability', 0.7)
            
            # Response success based on government transparency
            gov_transparency = government.attributes.get('information_transparency', 70) / 100
            success_prob = probability * gov_transparency
            
            outcome = 'success' if random.random() < success_prob else 'ignored'
            
            return {
                'type': 'demand_response',
                'participants': [getattr(resident, 'agent_id', 'resident'), 'government'],
                'outcome': outcome,
                'effect': rule.get('effect', ''),
                'area': getattr(resident, 'area', 'core_area')
            }
        
        return None
    
    def _create_enterprise_service_interaction(
        self,
        enterprise: Any,
        resident: Any,
        ent_decision: Dict[str, Any],
        rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create enterprise-resident service interaction"""
        rule = rules.get('service_supply', {})
        probability = rule.get('probability', 0.8)
        
        # Service success based on resident acceptance and enterprise capability
        resident_acceptance = resident.attributes.get('technology_acceptance', 70) / 100
        enterprise_capability = enterprise.state.get('innovation_level', 50) / 100
        
        success_prob = probability * resident_acceptance * enterprise_capability
        outcome = 'success' if random.random() < success_prob else 'rejected'
        
        interaction = {
            'type': 'service_supply',
            'participants': [
                getattr(enterprise, 'agent_id', 'enterprise'),
                getattr(resident, 'agent_id', 'resident')
            ],
            'outcome': outcome,
            'effect': rule.get('effect', ''),
            'area': getattr(resident, 'area', 'core_area')
        }
        
        return interaction
    
    def _create_bidding_interaction(
        self,
        enterprise: Any,
        government: Any,
        rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create project bidding interaction"""
        # Simple bidding success based on enterprise capabilities
        capability = enterprise.state.get('innovation_level', 50)
        compliance = enterprise.attributes.get('data_usage_compliance', 90)
        
        success_score = (capability + compliance) / 200
        outcome = 'success' if random.random() < success_score else 'failed'
        
        return {
            'type': 'project_bidding',
            'participants': [getattr(enterprise, 'agent_id', 'enterprise'), 'government'],
            'outcome': outcome,
            'effect': 'contract_award' if outcome == 'success' else 'bid_rejected'
        }
    
    def _create_data_request_interaction(
        self,
        enterprise: Any,
        government: Any,
        rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create data request interaction"""
        rule = rules.get('data_sharing', {})
        probability = rule.get('probability', 0.3)
        
        # Data request success based on compliance and government policy
        compliance = enterprise.attributes.get('data_usage_compliance', 90) / 100
        success_prob = probability * compliance
        
        outcome = 'approved' if random.random() < success_prob else 'denied'
        
        return {
            'type': 'data_request',
            'participants': [getattr(enterprise, 'agent_id', 'enterprise'), 'government'],
            'outcome': outcome,
            'effect': 'data_access' if outcome == 'approved' else 'access_denied'
        }
    
    def _update_agent_states(
        self,
        government: Any,
        enterprises: List[Any],
        residents: List[Any],
        interactions: List[Dict[str, Any]]
    ):
        """Update agent states based on interaction results"""
        # Group interactions by participant
        agent_interactions = {}
        
        for interaction in interactions:
            participants = interaction.get('participants', [])
            for participant in participants:
                if participant not in agent_interactions:
                    agent_interactions[participant] = []
                agent_interactions[participant].append(interaction)
        
        # Update government state
        if 'government' in agent_interactions:
            gov_interactions = agent_interactions['government']
            self._update_government_state(government, gov_interactions)
        
        # Update enterprise states
        for enterprise in enterprises:
            agent_id = getattr(enterprise, 'agent_id', 'enterprise')
            if agent_id in agent_interactions:
                ent_interactions = agent_interactions[agent_id]
                self._update_enterprise_state(enterprise, ent_interactions)
        
        # Update resident states
        for resident in residents:
            agent_id = getattr(resident, 'agent_id', 'resident')
            if agent_id in agent_interactions:
                res_interactions = agent_interactions[agent_id]
                self._update_resident_state(resident, res_interactions)
    
    def _update_government_state(self, government: Any, interactions: List[Dict[str, Any]]):
        """Update government agent state"""
        for interaction in interactions:
            outcome = interaction.get('outcome', 'neutral')
            
            if outcome == 'success':
                # Increase effectiveness metrics
                government.state['resource_utilization'] = min(1.0,
                    government.state.get('resource_utilization', 0.7) + 0.01)
            elif outcome in ['failed', 'violation']:
                # Decrease effectiveness metrics
                government.state['resource_utilization'] = max(0.0,
                    government.state.get('resource_utilization', 0.7) - 0.01)
    
    def _update_enterprise_state(self, enterprise: Any, interactions: List[Dict[str, Any]]):
        """Update enterprise agent state"""
        for interaction in interactions:
            outcome = interaction.get('outcome', 'neutral')
            interaction_type = interaction.get('type', '')
            
            if outcome == 'success':
                if interaction_type == 'procurement_cooperation':
                    # Increase innovation level
                    enterprise.state['innovation_level'] = min(100,
                        enterprise.state.get('innovation_level', 50) + 2)
                elif interaction_type == 'service_supply':
                    # Increase market share
                    enterprise.state['market_share'] = min(1.0,
                        enterprise.state.get('market_share', 0.1) + 0.01)
    
    def _update_resident_state(self, resident: Any, interactions: List[Dict[str, Any]]):
        """Update resident agent state"""
        for interaction in interactions:
            outcome = interaction.get('outcome', 'neutral')
            interaction_type = interaction.get('type', '')
            
            if outcome == 'success':
                if interaction_type == 'service_provision':
                    # Increase satisfaction
                    resident.state['satisfaction'] = min(5.0,
                        resident.state.get('satisfaction', 3.0) + 0.1)
                elif interaction_type == 'demand_response':
                    # Increase trust
                    resident.attributes['trust_in_government'] = min(100,
                        resident.attributes.get('trust_in_government', 80) + 1)
            elif outcome in ['failed', 'ignored']:
                # Decrease satisfaction and trust
                resident.state['satisfaction'] = max(1.0,
                    resident.state.get('satisfaction', 3.0) - 0.05)
                if interaction_type == 'demand_response':
                    resident.attributes['trust_in_government'] = max(0,
                        resident.attributes.get('trust_in_government', 80) - 2)