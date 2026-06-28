import re

def normalize_employee_count(count_str: str) -> int:
    if not count_str:
        return 0
    
    # "50-100" -> 75
    match = re.search(r'(\d+)\s*-\s*(\d+)', count_str)
    if match:
        return (int(match.group(1)) + int(match.group(2))) // 2
        
    # "100+" -> 100
    match = re.search(r'(\d+)', count_str)
    if match:
        return int(match.group(1))
        
    return 0

def normalize_trigger_type(trigger: str) -> str:
    if not trigger:
        return "unknown"
        
    trigger_lower = trigger.strip().lower()
    
    # Check standard ones
    valid_triggers = ["hiring", "funding", "m&a", "product launch", "layoffs", "expansion", "partnership", "leadership change", "ipo", "none"]
    for vt in valid_triggers:
        if vt in trigger_lower:
            return vt
            
    # Fallback mappings
    if "raise" in trigger_lower or "series" in trigger_lower:
        return "funding"
    elif "hir" in trigger_lower:
        return "hiring"
    elif "acquir" in trigger_lower or "merg" in trigger_lower:
        return "m&a"
    elif "launch" in trigger_lower:
        return "product launch"
    elif "layoff" in trigger_lower:
        return "layoffs"
    elif "expansion" in trigger_lower:
        return "expansion"
    elif "partnership" in trigger_lower or "partner" in trigger_lower:
        return "partnership"
    elif "leadership" in trigger_lower or "management" in trigger_lower:
        return "leadership change"
    elif "ipo" in trigger_lower:
        return "ipo"
        
    return trigger.strip().lower()

def normalize_role(role: str) -> str:
    if not role:
        return "Role unavailable"
        
    role_lower = role.lower().strip()
    if not role_lower or "unknown" in role_lower or "role unavailable" in role_lower:
        return "Role unavailable"
        
    if "chief revenue officer" in role_lower or "cro" in role_lower or "vp sales" in role_lower or "head of sales" in role_lower:
        return "Sales Leader"
    elif "founder" in role_lower or "ceo" in role_lower:
        return "Founder/CEO"
    elif "marketing" in role_lower:
        return "Marketing Leader"
        
    return role.strip().title()

