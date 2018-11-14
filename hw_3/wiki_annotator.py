import wikipedia
import annotation
import pymystem3
import ner_detector
from SPARQLWrapper import SPARQLWrapper, JSON


class WikiAnnotator:
    _query_template = """
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX : <http://dbpedia.org/resource/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        
        SELECT ?res WHERE {
            ?res dbo:wikiPageID "%s"^^xsd:integer .
            ?res rdf:type dbo:%s .
        }
    """

    def __init__(self):
        wikipedia.set_lang("en")
        self.stem = pymystem3.Mystem()
        self.sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        self.sparql.setReturnFormat(JSON)
        self.ner = ner_detector.NerDetector()

    def annotate(self, annot_text):
        for restr in self.ner.get_restrictions(annot_text):
            annot = self.__get_annotation(restr, annot_text)
            if annot is not None:
                annot_text.add_annotation(annot)
        for restr in annot_text.restrictions:
            annot = self.__get_annotation(restr, annot_text)
            if annot is not None:
                annot_text.add_annotation(annot)

    def __get_annotation(self, restr, annot_text):
        text = annot_text.text[restr.lpos:restr.rpos]
        text = "".join(self.stem.lemmatize(text))
        s_res = wikipedia.search(text)
        if len(s_res) == 0:
            return None
        pg = wikipedia.page(s_res[0])
        query = self._query_template % (pg.pageid, restr.type)
        self.sparql.setQuery(query)
        uri = self.__retrieve_uri(self.sparql.query().convert())
        if uri == "":
            return None
        return annotation.Annotation(restr.lpos, restr.rpos, uri, restr.type)

    @staticmethod
    def __retrieve_uri(query_res):
        try:
            return query_res["result"]["bindings"][0]["res"]["value"]
        except:
            return ""
