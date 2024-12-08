from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

class Effect(Enum):
    ALLOW = "Allow"
    DENY = "Deny"

class Action(Enum):
    # Browser Actions
    NAVIGATE = "browser:Navigate"
    READ_PAGE = "browser:ReadPage"
    FILL_FORM = "browser:FillForm"
    CLICK_ELEMENT = "browser:ClickElement"
    
    # AI Actions
    ANALYZE_CONTENT = "ai:AnalyzeContent"
    GENERATE_RESPONSE = "ai:GenerateResponse"
    
    # Data Actions
    READ_SENSITIVE_DATA = "data:ReadSensitive"
    WRITE_SENSITIVE_DATA = "data:WriteSensitive"
    
    # System Actions
    EXECUTE_SCRIPT = "system:ExecuteScript"
    ACCESS_NETWORK = "system:AccessNetwork"

@dataclass
class Condition:
    """Represents a condition that must be met for a policy statement to apply"""
    type: str  # e.g., "StringEquals", "DateGreaterThan"
    key: str   # e.g., "browser.url", "time"
    value: Any

@dataclass
class Statement:
    """Represents a single policy statement"""
    sid: str
    effect: Effect
    actions: List[Action]
    resources: List[str]
    conditions: Optional[List[Condition]] = None

@dataclass
class Policy:
    """Represents a complete policy document"""
    version: str
    statements: List[Statement]
