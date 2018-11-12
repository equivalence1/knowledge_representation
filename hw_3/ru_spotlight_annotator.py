import docker
import docker.errors
import urllib3
import json
import annotation
import time


class RuSpotlightAnnotator:
    image_name = "dbpedia/spotlight-russian"
    cmd = "spotlight.sh"
    host_port = 2227
    container_name = "dbpedia-spotlight-russian"
    host = "127.0.0.1"
    url_base = "http://" + host + ":" + str(host_port) + "/rest/annotate"

    def __init__(self):
        self.docker_client = docker.from_env()
        self.cnt = None
        self.http = urllib3.PoolManager()
        self.__start_container()
        self.__wait_server_start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cnt is not None:
            self.cnt.stop()

    def annotate(self, ann_text):
        json_annotations = self.__get_json_annotations(ann_text.text)
        annotations = self.__json_extract_annotations(json_annotations)
        for ann in annotations:
            ann_text.add_annotation(ann)

    def __get_json_annotations(self, text):
        r = self.http.request(
            method="POST",
            url=self.url_base,
            headers={
                "Accept": "application/json",
            },
            body=("text=" + text + "&" + "types=Person,Organisation,Place").encode('utf-8'))
        return r.data.decode('utf-8')

    @staticmethod
    def __json_extract_annotation(resource):
        text = resource["@surfaceForm"]
        uri = resource["@URI"]
        return annotation.Annotation(text, uri)

    def __json_extract_annotations(self, json_annotations):
        annotations_map = json.loads(json_annotations)
        if "Resources" in annotations_map:
            annotations = [self.__json_extract_annotation(res) for res in annotations_map["Resources"]]
        else:
            annotations = []
        return annotations

    def __wait_server_start(self):
        while True:
            try:
                self.__get_json_annotations("dummy text")
                return
            except:
                time.sleep(0.5)

    def __container_exists(self):
        try:
            self.docker_client.containers.get(self.container_name)
            return True
        except docker.errors.NotFound:
            return False

    def __create_container(self):
        self.docker_client.containers.create(
            image=self.image_name,
            command=self.cmd,
            detach=True,
            auto_remove=True,
            ports={'80/tcp': self.host_port},
            stdin_open=True,
            name=self.container_name)

    def __start_container(self):
        if not self.__container_exists():
            self.__create_container()
        self.cnt = self.docker_client.containers.get(self.container_name)
        if not self.cnt.status == "running":
            self.cnt.start()
