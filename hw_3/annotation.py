import utils


class Annotation:
    def __init__(self, lpos, rpos, uri, type):
        self.lpos = lpos
        self.rpos = rpos
        self.uri = uri
        self.type = type

    def to_string(self):
        return str(self.lpos) + " " + str(self.rpos) + " " + str(self.uri) + " " + str(self.type)


class Restriction:
    def __init__(self, lpos, rpos, type):
        self.lpos = lpos
        self.rpos = rpos
        self.type = type


class AnnotatedText:
    def __init__(self, text_id, text):
        self.text_id = text_id
        self.text = text
        self.annotations = []
        self.restrictions = []

    def add_annotation(self, annot):
        for restr in self.restrictions:
            if utils.segments_intersect((restr.lpos, restr.rpos),
                                        (annot.lpos, annot.rpos)) and \
                    restr.type != annot.type:
                return
        for annot1 in self.annotations:
            if utils.segments_intersect((annot.lpos, annot.rpos),
                                        (annot1.lpos, annot1.rpos)):
                return
        self.annotations.append(annot)

    def add_restriction(self, restriction):
        self.restrictions.append(restriction)

    def to_string(self):
        def annot_text(annot):
            return self.text[annot.lpos:annot.rpos] + "\t" + annot.uri
        annot_texts = map(annot_text, self.annotations)
        return self.text_id + "\t" + "\t".join(annot_texts)
