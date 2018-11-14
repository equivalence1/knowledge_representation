import ner
import annotation


class NerDetector:
    def __init__(self):
        self.extractor = ner.Extractor()

    def get_restrictions(self, annot_text):
        restrs = []
        for match in self.detect_entities(annot_text.text):
            lpos = match.span[0]
            rpos = match.span[1]
            if match.type == "LOC":
                type = "Place"
            elif match.type == "PER":
                type = "Person"
            else:
                type = "Organization"
            restr = annotation.Restriction(lpos, rpos, type)
            restrs.append(restr)
        return restrs

    def detect_entities(self, text):
        return self.extractor(text)
