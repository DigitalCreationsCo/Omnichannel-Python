class Contact:
    def __init__(self, name=None, organization=None, phone=None, date_contacted=None, website=None, location=None, date_replied=None, email=None, linkedin=None, meeting=None, next_step=None, amount_funded=None, shares=None, follow_up_24_hours = None):
        self.name = name
        self.organization = organization
        self.date_contacted = date_contacted
        self.website = website
        self.location = location
        self.date_replied = date_replied
        self.phone = phone
        self.email = email
        self.linkedin = linkedin
        self.meeting = meeting
        self.amount_funded = amount_funded
        self.shares = shares
        self.follow_up_24_hours = follow_up_24_hours

    def to_dict(self):
        return {
            'organization': self.organization,
            'name': self.name,
            'dateContacted': self.date_contacted,
            'followUp24Hours': self.follow_up_24_hours,
            'dateReplied': self.date_replied,
            'Meeting': self.meeting,
            'Funding': self.amount_funded,
            'shares': self.shares,
            'phone': self.phone,
            'website': self.website,
            'location': self.location,
            'email': self.email,
            'Linkedin': self.linkedin,
            'message': '',
        }
