"""
Agent classes for ABM digital governance simulation
"""
import os
import json
import random
import logging
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Agent:
    """Base Agent class for ABM simulation"""
    
    def __init__(self, agent_type: str, config: Dict[str, Any], city: str):
        """
        Initialize Agent
        
        Args:
            agent_type: Type of agent (government/enterprise/resident)
            config: Agent configuration from JSON
            city: City context (beijing/shenzhen)
        """
        self.type = agent_type
        self.config = config
        self.city = city
        self.state = config.get('initial_state', {}).copy()
        self.attributes = config.get('attributes', {}).copy()
        self.interaction_history = []
        
        # Initialize LLM with GLM-4
        api_config = self._load_api_config()
        self.llm = ChatOpenAI(
            model=api_config.get("model", "glm-4"),
            openai_api_key=api_config.get("api_key", "your-zhipuai-api-key"),
            openai_api_base=api_config.get("openai_api_base", "https://open.bigmodel.cn/api/paas/v4/"),
            temperature=0.6
        )
        
        # Load prompt template
        self.prompt_template = self._load_prompt_template()
    
    def _load_api_config(self) -> Dict[str, str]:
        """Load API configuration from env file"""
        config = {}
        try:
            # Try to read from ../env file (relative to project root)
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'env')
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            # Remove quotes if present
                            value = value.strip('"\'')
                            config[key.strip()] = value
                logger.info(f"Loaded API config from {env_path}")
            else:
                # Fallback to environment variables
                config = {
                    "model": os.getenv("MODEL", "glm-4"),
                    "api_key": os.getenv("ZAI_API_KEY", "your-zhipuai-api-key"),
                    "openai_api_base": os.getenv("OPENAI_API_BASE", "https://open.bigmodel.cn/api/paas/v4/")
                }
                logger.info("Using environment variables for API config")
        except Exception as e:
            logger.warning(f"Failed to load API config: {e}, using defaults")
            config = {
                "model": "glm-4",
                "api_key": "your-zhipuai-api-key", 
                "openai_api_base": "https://open.bigmodel.cn/api/paas/v4/"
            }
        
        return config
    
    def _load_prompt_template(self) -> str:
        """Load prompt template from file"""
        try:
            template_path = f'prompts/{self.type}_prompt.txt'
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt template not found for {self.type}, using default")
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Get default prompt if template file not found"""
        return f"""You are a {self.type} agent in {self.city}. 
        Please make decisions based on the current context.
        Output your decision in JSON format."""
    
    def _add_missing_variables(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Add missing variables with default values for prompt formatting"""
        # Common variables for all agents
        defaults = {
            'environment_context': context.get('environment_context', 'Normal operating conditions'),
            'recent_interactions': context.get('recent_interactions', 'No recent interactions'),
            'service_quality': context.get('service_quality', 3.5),
            'privacy_level': context.get('privacy_level', 'Medium'),
            'infrastructure_level': context.get('infrastructure_level', 70),
            'available_services': context.get('available_services', 'Basic digital services'),
            'usage_frequency': context.get('usage_frequency', 5),
            'regulation_intensity': context.get('regulation_intensity', 'Medium'),
            'available_data': context.get('available_data', 'Limited public data'),
            'market_conditions': context.get('market_conditions', 'Stable'),
            'competition_level': context.get('competition_level', 'Medium'),
            'area_type': getattr(self, 'area_type', getattr(self, 'area', 'core_area'))
        }
        
        # Update context with defaults for missing keys
        for key, value in defaults.items():
            if key not in context:
                context[key] = value
        
        return context
    
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make decision using LLM
        
        Args:
            context: Current simulation context
            
        Returns:
            Decision dictionary
        """
        try:
            # Prepare context data with all required variables
            prompt_context = {
                'city': self.city,
                **self.attributes,
                **self.state,
                **context
            }
            
            # Add missing variables with default values
            prompt_context = self._add_missing_variables(prompt_context)
            
            # Format prompt
            formatted_prompt = self.prompt_template.format(**prompt_context)
            
            # Create messages
            messages = [
                SystemMessage(content=f"You are a {self.type} agent in digital governance simulation."),
                HumanMessage(content=formatted_prompt)
            ]
            
            # Call LLM
            response = self.llm(messages)
            
            # Log the LLM response for debugging
            logger.info(f"{self.type} agent LLM response: {response.content[:200]}...")
            
            # Parse JSON response
            decision = self._parse_response(response.content)
            
            # Store interaction
            self.interaction_history.append({
                'context': context,
                'decision': decision,
                'timestamp': len(self.interaction_history)
            })
            
            return decision
            
        except Exception as e:
            error_msg = str(e)
            if "500 Internal Server Error" in error_msg:
                logger.warning(f"{self.type} agent: API server error, using fallback decision")
            elif "timeout" in error_msg.lower():
                logger.warning(f"{self.type} agent: API timeout, using fallback decision")
            else:
                logger.warning(f"LLM call failed for {self.type} agent, using fallback decision: {e}")
            
            decision = self._get_default_decision()
            
            # Store fallback interaction with error info
            self.interaction_history.append({
                'context': context,
                'decision': decision,
                'timestamp': len(self.interaction_history),
                'fallback': True,
                'error': error_msg
            })
            
            return decision
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to JSON"""
        try:
            # Try to extract JSON from response
            response = response.strip()
            
            # Find JSON block
            if '```json' in response:
                start = response.find('```json') + 7
                end = response.find('```', start)
                json_str = response[start:end].strip()
            elif '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
            else:
                raise ValueError("No JSON found in response")
            
            return json.loads(json_str)
            
        except Exception as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            return self._get_default_decision()
    
    def _get_default_decision(self) -> Dict[str, Any]:
        """Get default decision when LLM fails"""
        return {
            "action": "no_action",
            "target": "none",
            "reason": "System fallback due to parsing error"
        }
    
    def update_state(self, action_result: Dict[str, Any]):
        """
        Update agent state based on action result
        
        Args:
            action_result: Result of the action taken
        """
        # Update state based on action type and result
        if action_result.get('type') == 'learning':
            self.attributes['information_literacy'] = min(100, 
                self.attributes.get('information_literacy', 60) + 5)
        
        elif action_result.get('type') == 'service_use':
            self.state['service_usage_frequency'] = min(10,
                self.state.get('service_usage_frequency', 5) + 1)
        
        elif action_result.get('type') == 'innovation':
            self.state['innovation_level'] = min(100,
                self.state.get('innovation_level', 50) + 10)
        
        # Update based on outcome
        outcome = action_result.get('outcome', 'neutral')
        if outcome == 'success':
            self.state['satisfaction'] = min(5.0,
                self.state.get('satisfaction', 3.0) + 0.2)
        elif outcome == 'failure':
            self.state['satisfaction'] = max(1.0,
                self.state.get('satisfaction', 3.0) - 0.2)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state"""
        return {
            'type': self.type,
            'attributes': self.attributes.copy(),
            'state': self.state.copy(),
            'interaction_count': len(self.interaction_history)
        }


class GovernmentAgent(Agent):
    """Government agent with specific governance behaviors"""
    
    def __init__(self, config: Dict[str, Any], city: str):
        super().__init__('government', config, city)
        
        # City-specific adjustments
        if city == 'beijing':
            self.attributes['governance_preference'] = 'fairness'
            self.attributes['platform_regulation'] = 95
        elif city == 'shenzhen':
            self.attributes['governance_preference'] = 'efficiency'  
            self.attributes['information_transparency'] = 85
    
    def _get_default_decision(self) -> Dict[str, Any]:
        """Government-specific default decision"""
        actions = ['service_provision', 'policy_adjustment', 'regulation']
        return {
            "action": random.choice(actions),
            "target": "residents",
            "reason": "Government default action",
            "expected_outcome": "maintain_stability"
        }


class EnterpriseAgent(Agent):
    """Enterprise agent with business-oriented behaviors"""
    
    def __init__(self, config: Dict[str, Any], city: str):
        super().__init__('enterprise', config, city)
        
        # City-specific adjustments
        if city == 'beijing':
            self.attributes['technology_type'] = 'government_project'
            self.attributes['data_collection_strategy'] = 'compliant'
        elif city == 'shenzhen':
            self.attributes['technology_type'] = 'market_driven'
            self.attributes['data_collection_strategy'] = 'flexible'
    
    def _get_default_decision(self) -> Dict[str, Any]:
        """Enterprise-specific default decision"""
        actions = ['service_development', 'market_expansion', 'innovation']
        return {
            "action": random.choice(actions),
            "target": "residents",
            "data_usage": "compliant",
            "innovation_focus": "user_experience"
        }


class ResidentAgent(Agent):
    """Resident agent with citizen behaviors"""
    
    def __init__(self, config: Dict[str, Any], city: str, area_type: str = 'core_area'):
        super().__init__('resident', config, city)
        self.area_type = area_type
        self.area = area_type  # Ensure both attributes exist
        
        # Area-specific adjustments
        if area_type == 'urban_rural_fringe':
            self.attributes['information_literacy'] = max(30,
                self.attributes.get('information_literacy', 60) - 20)
            self.attributes['income_level'] = max(3000,
                self.attributes.get('income_level', 5000) - 1500)
        elif area_type == 'rural':
            self.attributes['information_literacy'] = max(20,
                self.attributes.get('information_literacy', 60) - 30)
            self.attributes['income_level'] = max(2000,
                self.attributes.get('income_level', 5000) - 2500)
    
    def _get_default_decision(self) -> Dict[str, Any]:
        """Resident-specific default decision"""
        actions = ['use_service', 'provide_feedback', 'seek_information']
        return {
            "action": random.choice(actions),
            "target": "government",
            "satisfaction": random.uniform(2.0, 4.0),
            "concern": "service_quality"
        }


def create_agents(agents_config: Dict[str, Any], city: str, num_enterprises: int = 10, num_residents: int = 100) -> Dict[str, Any]:
    """
    Create agent instances based on configuration
    
    Args:
        agents_config: Configuration for all agent types
        city: City context
        num_enterprises: Number of enterprise agents to create
        num_residents: Number of resident agents to create
        
    Returns:
        Dictionary containing created agents
    """
    # Create government agent
    government = GovernmentAgent(agents_config['government'], city)
    
    # Create enterprise agents (configurable number)
    enterprises = []
    for i in range(num_enterprises):
        enterprise = EnterpriseAgent(agents_config['enterprise'], city)
        enterprise.agent_id = f"enterprise_{i}"
        enterprises.append(enterprise)
    
    # Create resident agents (configurable number)
    residents = []
    area_types = ['core_area', 'urban_rural_fringe', 'rural']
    area_weights = [0.5, 0.3, 0.2]  # Distribution weights
    
    for i in range(num_residents):
        # Randomly assign area type based on weights
        area_type = random.choices(area_types, weights=area_weights)[0]
        resident = ResidentAgent(agents_config['resident'], city, area_type)
        resident.agent_id = f"resident_{i}"
        resident.area = area_type
        residents.append(resident)
    
    return {
        'government': government,
        'enterprises': enterprises,
        'residents': residents
    }