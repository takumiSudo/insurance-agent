from typing import Any, Dict, List, Optional
from datetime import datetime
import json
from .policy_types import Policy, Statement, Effect, Action, Condition

class PolicyEnforcer:
    def __init__(self, policy_file: str = None):
        """Initialize the policy enforcer with a policy file"""
        if isinstance(policy_file, str):
            self.policy = self._load_policy(policy_file)
        else:
            self.policy = policy_file  # Allow passing Policy object directly
        
    def _load_policy(self, policy_file: str) -> Policy:
        """Load and parse policy from a JSON file"""
        with open(policy_file, 'r') as f:
            policy_data = json.load(f)
            
        statements = []
        for stmt_data in policy_data['statements']:
            conditions = []
            if 'conditions' in stmt_data:
                for cond in stmt_data['conditions']:
                    conditions.append(Condition(
                        type=cond['type'],
                        key=cond['key'],
                        value=cond['value']
                    ))
            
            statements.append(Statement(
                sid=stmt_data['sid'],
                effect=Effect(stmt_data['effect']),
                actions=[Action(a) for a in stmt_data['actions']],
                resources=stmt_data['resources'],
                conditions=conditions if conditions else None
            ))
            
        return Policy(
            version=policy_data['version'],
            statements=statements
        )
    
    def evaluate_conditions(self, conditions: List[Condition], context: Dict[str, Any]) -> bool:
        """Evaluate conditions against the current context"""
        if not conditions:
            return True
            
        for condition in conditions:
            if condition.type == "StringEquals":
                if context.get(condition.key) != condition.value:
                    return False
            elif condition.type == "DateGreaterThan":
                context_date = datetime.fromisoformat(context.get(condition.key, ""))
                condition_date = datetime.fromisoformat(condition.value)
                if not context_date > condition_date:
                    return False
            # Add more condition types as needed
            
        return True
    
    def check_permission(self, action: Action, resource: str, context: Dict[str, Any]) -> bool:
        """
        Check if the requested action is allowed on the resource given the context
        
        Args:
            action: The action to perform
            resource: The resource to perform the action on
            context: Additional context for evaluating conditions
            
        Returns:
            bool: True if action is allowed, False otherwise
        """
        # Default to deny if no matching statements
        final_decision = False
        
        for statement in self.policy.statements:
            # Check if action and resource match
            if (action in statement.actions and 
                any(self._match_resource(resource, r) for r in statement.resources)):
                
                # Evaluate conditions
                if statement.conditions:
                    if not self.evaluate_conditions(statement.conditions, context):
                        continue
                
                # Apply effect
                if statement.effect == Effect.ALLOW:
                    final_decision = True
                else:  # DENY
                    return False  # Explicit deny takes precedence
        
        return final_decision
    
    def _match_resource(self, resource: str, pattern: str) -> bool:
        """Check if resource matches the pattern (supports wildcards)"""
        if pattern == "*":
            return True
        
        # Convert pattern to regex-like matching
        pattern_parts = pattern.split("*")
        return all(part in resource for part in pattern_parts if part)
