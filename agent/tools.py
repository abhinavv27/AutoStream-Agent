def mock_lead_capture(name: str, email: str, platform: str):
    """
    Simulates a lead capture API call.
    Must ONLY be called when name, email, and platform are all present.
    """
    print(f"\n[INTERNAL TOOL CALL] Executing mock_lead_capture...")
    print(f"  Name: {name}")
    print(f"  Email: {email}")
    print(f"  Platform: {platform}")
    print(f"[SYSTEM] Lead captured successfully for {name}.\n")
    
    return {
        'status': 'success', 
        'lead_id': 'LEAD_001',
        'message': f"Lead for {name} has been synced to the CRM."
    }
