# file: app/bot/utils/agent_loader.py
import os
import yaml
from typing import Dict

AGENTS_DIR = os.path.join("app", "agents")

def load_agent_config(agent_name: str) -> Dict:
    """Завантажує конфігурацію агента з YAML файлу"""
    path = os.path.join(AGENTS_DIR, f"{agent_name}.yml")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Agent config not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    return config

def get_agent_prompt(agent_name: str) -> str:
    """Повертає system prompt для агента"""
    config = load_agent_config(agent_name)
    instructions = config.get("instructions", "")
    print(f"📝 Loaded {agent_name}: {len(instructions)} chars")
    return instructions
