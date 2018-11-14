import annotation
import ru_spotlight_annotator
import person_detector
import wiki_annotator
import datetime


class TitlesAnnotator:
    def __init__(self):
        self.annotators = [ru_spotlight_annotator.RuSpotlightAnnotator(), wiki_annotator.WikiAnnotator()]
        self.restrictors = [person_detector.PersonDetector()]

    def restrict(self, annot_text: annotation.AnnotatedText):
        for restrictor in self.restrictors:
            restrictor.add_restrictions(annot_text)

    def annotate(self, annot_text: annotation.AnnotatedText):
        for annotator in self.annotators:
            annotator.annotate(annot_text)

    def annotate_titles(self, in_file_path, out_file_path):
        # TODO annotators selection
        with open(out_file_path, "w") as out:
            with open(in_file_path, "r") as inp:
                start_time = datetime.datetime.now()
                for line in inp:
                    line = line.replace("%", "")
                    splitted_line = line.split("\t")
                    line_id = splitted_line[0]
                    line_text = splitted_line[1]
                    annot_text = annotation.AnnotatedText(line_id, line_text)
                    self.restrict(annot_text)
                    self.annotate(annot_text)
                    out.write(annot_text.to_string() + "\n")
                    print(annot_text.to_string())
                    if line_id[-2:] == "00":
                        cur_time = datetime.datetime.now()
                        time_delta = cur_time - start_time
                        print("Annotated", line_id, "lines, took", time_delta)
                        out.flush()


if __name__ == "__main__":
    # TODO parse arguments
    t_annotator = TitlesAnnotator()
    t_annotator.annotate_titles("12800headlines.txt", "output.txt")
