import uuid


def validate_uuid(uuid_string: str) -> uuid.UUID:
    """
    Validate and convert a UUID string to a UUID object.
    
    Args:
        uuid_string: The UUID string to validate
        
    Returns:
        uuid.UUID: The parsed UUID object
        
    Raises:
        ValueError: If the UUID string is empty or invalid
    """
    if not uuid_string:
        raise ValueError('UUID required')
    
    try:
        parsed_uuid = uuid.UUID(uuid_string)
    except ValueError:
        raise ValueError('Invalid UUID')
    
    return parsed_uuid
