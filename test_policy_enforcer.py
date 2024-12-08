import pytest
from datetime import datetime
from policy.policy_types import Action, Effect, Statement, Condition, Policy
from policy.policy_enforcer import PolicyEnforcer

def test_basic_allow():
    """Test basic allow policy"""
    policy = Policy(
        version="2023-12-08",
        statements=[
            Statement(
                sid="AllowRead",
                effect=Effect.ALLOW,
                actions=[Action.READ_PAGE],
                resources=["*"],
                conditions=None
            )
        ]
    )
    
    enforcer = PolicyEnforcer(policy)
    context = {
        "browser.url": "https://example.com",
        "time": datetime.now().isoformat()
    }
    
    assert enforcer.check_permission(Action.READ_PAGE, "*", context)
    assert not enforcer.check_permission(Action.FILL_FORM, "*", context)

def test_condition_evaluation():
    """Test condition evaluation"""
    policy = Policy(
        version="2023-12-08",
        statements=[
            Statement(
                sid="AllowWithCondition",
                effect=Effect.ALLOW,
                actions=[Action.FILL_FORM],
                resources=["*"],
                conditions=[
                    Condition(
                        type="StringEquals",
                        key="browser.url",
                        value="https://insurance.example.com"
                    )
                ]
            )
        ]
    )
    
    enforcer = PolicyEnforcer(policy)
    
    # Should allow
    context = {
        "browser.url": "https://insurance.example.com",
        "time": datetime.now().isoformat()
    }
    assert enforcer.check_permission(Action.FILL_FORM, "*", context)
    
    # Should deny
    context["browser.url"] = "https://malicious.com"
    assert not enforcer.check_permission(Action.FILL_FORM, "*", context)

def test_explicit_deny():
    """Test explicit deny takes precedence"""
    policy = Policy(
        version="2023-12-08",
        statements=[
            Statement(
                sid="AllowAll",
                effect=Effect.ALLOW,
                actions=[Action.READ_SENSITIVE_DATA],
                resources=["*"]
            ),
            Statement(
                sid="DenySpecific",
                effect=Effect.DENY,
                actions=[Action.READ_SENSITIVE_DATA],
                resources=["sensitive/*"]
            )
        ]
    )
    
    enforcer = PolicyEnforcer(policy)
    context = {
        "browser.url": "https://example.com",
        "time": datetime.now().isoformat()
    }
    
    assert enforcer.check_permission(Action.READ_SENSITIVE_DATA, "public/data", context)
    assert not enforcer.check_permission(Action.READ_SENSITIVE_DATA, "sensitive/data", context)

def test_resource_matching():
    """Test resource pattern matching"""
    policy = Policy(
        version="2023-12-08",
        statements=[
            Statement(
                sid="AllowSpecificForm",
                effect=Effect.ALLOW,
                actions=[Action.FILL_FORM],
                resources=["form_field:policy-*"]
            )
        ]
    )
    
    enforcer = PolicyEnforcer(policy)
    context = {
        "browser.url": "https://example.com",
        "time": datetime.now().isoformat()
    }
    
    assert enforcer.check_permission(Action.FILL_FORM, "form_field:policy-number", context)
    assert not enforcer.check_permission(Action.FILL_FORM, "form_field:credit-card", context)
