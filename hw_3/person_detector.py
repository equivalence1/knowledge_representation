import pymystem3
import annotation


class PersonDetector:
    def __init__(self):
        self.model = pymystem3.Mystem()

    def add_restrictions(self, annot_text):
        people_positions = self.detect_people(annot_text.text)
        for pos in people_positions:
            annot_text.add_restriction(annotation.Restriction(pos[0], pos[1], "Person"))

    def detect_people(self, text):
        """
        Tries to spot all the mentions of people in the given text.
        For this classification we use Yandex's pymystem3 library.

        Unfortunately, it's not always 100% correct. Especially with
        foreign names. E.g. it can sometimes classify a surname as a first name.
        It's also generally hard to detect middle names and ring names.
        But since we only annotate news titles or short queries, it seems
        a legitimate to think that all people mentions come in one of
        three forms:

        1) (last name)
           corresponds to titles with some famous people like "Trump" or "Putin"
        2) (first name) (last name)
        3) (first name) (middle name|ring name) (last name)

        It still might be hard to differ between middle name and some
        other terms, so in this case we just use a simple heuristic:
        if we see construction like (name) (something) (name), then
        if this (something) start with an upper-case letter or is in
        quotes, then we consider it as a middle name|ring name.
        """
        terms_analysis = self.model.analyze(text)

        term_bounds = []
        start = 0
        last_name_ids = []
        last_name_id = -1

        for i in range(len(terms_analysis)):
            term = terms_analysis[i]
            text = term["text"]
            term_bounds.append((start, start + len(text)))
            start = start + len(text)
            last_name_ids.append(last_name_id)
            if self.__is_name(term):
                last_name_id = i

        res = []
        i = last_name_id

        def is_single_person_mention(j, i):
            if j < 0:
                return False
            if j == i:
                return True
            if i - j == 2:
                mid_term = terms_analysis[j + 1]
                if mid_term["text"].strip() == "":
                    return True
            if i - j == 4:
                mid_term = terms_analysis[j + 2]
                if PersonDetector.__can_be_middle_name(mid_term):
                    return True
            return False

        while i >= 0:
            j = i
            last_j = j
            while j >= 0 and is_single_person_mention(j, i):
                last_j = j
                j = last_name_ids[j]
            res.append((term_bounds[last_j][0], term_bounds[i][1]))
            i = j

        return res[::-1]

    @staticmethod
    def __is_name(term_analysis):
        try:
            gr = term_analysis["analysis"][0]["gr"]
            return "имя" in gr or "фам" in gr
        except:
            return False

    @staticmethod
    def __can_be_middle_name(term_analysis):
        if PersonDetector.__is_name(term_analysis):
            return True
        if "analysis" not in term_analysis:
            return False
        text = term_analysis["text"]
        gr = term_analysis["analysis"][0]["gr"]
        return text[0].isupper() and "S" in gr
