def validate_contact_data(data, update=False):
    required_fields = ['email'] if not update else []
    
    if not update and not all(field in data for field in required_fields):
        return False
    
    allowed_fields = {
        'email', 'firstname', 'lastname', 'phone', 
        'company', 'website', 'lifecyclestage'
    }
    
    return all(key in allowed_fields for key in data.keys())

def validate_pagination_params(page, per_page):
    return page > 0 and 1 <= per_page <= 100
