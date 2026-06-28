from services.apollo_service import find_contacts
from services.hunter_service import find_emails

def enrich_contacts(domain: str) -> list:
    try:
        apollo_contacts = find_contacts(domain)
    except Exception:
        apollo_contacts = []
        
    try:
        hunter_emails = find_emails(domain)
    except Exception:
        hunter_emails = []
        
    # Merge Logic
    # Priority: Apollo role data + Hunter email data
    merged = {}
    
    for contact in apollo_contacts:
        name = contact.get("name")
        if name:
            merged[name] = {
                "name": name,
                "role": contact.get("role"),
                "email": contact.get("email"),
                "linkedin": contact.get("linkedin"),
                "phone": contact.get("phone"),
                "source": contact.get("source") or "Apollo"
            }
            
    for h_contact in hunter_emails:
        name = h_contact.get("name")
        email = h_contact.get("email")
        
        if name in merged:
            if not merged[name].get("email") and email:
                merged[name]["email"] = email
            if not merged[name].get("role") and h_contact.get("role"):
                merged[name]["role"] = h_contact.get("role")
            if not merged[name].get("linkedin") and h_contact.get("linkedin"):
                merged[name]["linkedin"] = h_contact.get("linkedin")
        else:
            if name:
                merged[name] = {
                    "name": name,
                    "role": h_contact.get("role"),
                    "email": email,
                    "linkedin": h_contact.get("linkedin"),
                    "phone": h_contact.get("phone"),
                    "source": h_contact.get("source") or "Hunter"
                }
            
    return list(merged.values())
