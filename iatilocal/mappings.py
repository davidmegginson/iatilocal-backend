""" IATI code list lookup """

# TODO use live code lists instead of hard-coding them here

IATI_CODE_LISTS = {
    
    "organisation-type": {
        "10": "Government", 
        "11": "Local Government",
        "15": "Other Public Sector", 
        "21": "International NGO", 
        "22": "National NGO", 
        "23": "Regional NGO", 
        "24": "Partner Country based NGO",
        "30": "Public Private Partnership", 
        "40": "Multilateral", 
        "60": "Foundation", 
        "70": "Private Sector", 
        "71": "Private Sector in Provider Country",
        "72": "Private Sector in Aid Recipient Country",
        "73": "Private Sector in Third Country",
        "80": "Academic, Training and Research", 
        "90": "Other",
    },
    
    "organisation-role": {
        "1": "Funding",
        "2": "Accountable",
        "3": "Extending",
        "4": "Implementing",
    },
    
    "activity-status": {
        "1": "Pipeline/identification",
        "2": "Implementation",
        "3": "Finalisation",
        "4": "Closed",
        "5": "Cancelled",
        "6": "Suspended",
    },
}

def get_label (type, code):
    """ Look up a text label for an IATI code """
    if not type in IATI_CODE_LISTS:
        raise Exception("Unrecognised code list {}".format(type))
    else:
        return IATI_CODE_LISTS[type].get(code, "Unknown")
