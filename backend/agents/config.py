DEFAULT_CONFIG = {
    "icp_criteria": {
        "industry": "Supply Chain, Logistics",
        "min_employees": 10,
        "qualification_threshold": 60,
    },
    "scoring": {
        "high_intent_triggers": ["funding", "hiring", "expansion", "partnership", "acquisition", "tech_stack", "product_launch"],
        "trigger_weight": 50,
        "employee_weight": 20,
        "industry_weight": 30,
        "max_score": 100,
        "qualification_threshold": 60,
    },
    "env_vars": {
        "GROQ_API_KEY": "Required — LLM calls",
        "FIRECRAWL_API_KEY": "Optional — live website scraping",
        "HUNTER_API_KEY": "Optional — real contact lookup",
    },
    "personas": {
        "default": ["Founder", "VP Sales", "Head of Growth"],
        "options": [
            "Founder",
            "VP Sales",
            "Head of Growth",
            "CEO",
            "CTO",
            "VP Engineering",
        ],
    },
}
