from . import dbfuncs

class Profile:

    def __init__(self, orcid, specialty_id, keywords):
        self.orcid = orcid
        self.specialty_id = specialty_id
        self.keywords = keywords
        self.suitability = 0

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

    #usage: application.compare(candidate)
    def compare(self, candidate):
        candidate.suitability = 0

        for keyword_app in self.keywords: 
            for keyword_cand in candidate.keywords: 
                if keyword_cand == keyword_app:
                    candidate.suitability += dbfuncs.weight(keyword_cand)
                    break # переходимо до наступного keyword_app

