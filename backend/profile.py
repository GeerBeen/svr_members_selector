from backend import dbfuncs

class Profile:

    def __init__(self, orcid, specialty_id, keywords):
        self.orcid = orcid
        self.specialty_id = specialty_id
        self.keywords = keywords
        self.suitability = 0
        self.weights = {}

    def __eq__(self, other):
        if not isinstance(other, Profile):
            return NotImplemented
        return self.orcid == other.orcid

    def __hash__(self):
        return hash(self.orcid)

    def __repr__(self):
        kw_str = ", ".join(self.keywords)

        return (f"Profile('{self.orcid}'\n"
                f"'{self.specialty_id}'\n"
                f"'{kw_str}'\n"
                f"'{self.suitability})")
       
    def display(self):
        print(self.__repr__())

    def set_weights(self):
        self.weights = dbfuncs.get_weights(self.keywords)

    #usage: application.compare(candidate)
    def compare(self, candidate):
        candidate.suitability = 0

        for keyword_app in self.keywords:
            if keyword_app in candidate.keywords:
                weight_value = self.weights.get(keyword_app, 0.0)
                candidate.suitability += weight_value

