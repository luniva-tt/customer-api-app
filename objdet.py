
from roboflow import Roboflow
rf = Roboflow(api_key="v0l7zJjs8tENLPrgvrDY")
project = rf.workspace("ali-u2nwj").project("people-jysvi")
version = project.version(1)
dataset = version.download("coco")