class Annotation:
    def __init__(self, text, uri):
        self.text = text
        self.uri = uri


class AnnotatedText:
    def __init__(self, text_id, text):
        self.text_id = text_id
        self.text = text
        self.annotations = []

    def add_annotation(self, annotation):
        self.annotations.append(annotation)

    def to_string(self):
        annot_texts = map(lambda annot: annot.text + "\t" + annot.uri, self.annotations)
        return self.text_id + "\t" + "\t".join(annot_texts)
