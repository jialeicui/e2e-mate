import dataclasses
import os
import re
import typing

import fastapi
import uvicorn

from kubernetes import client, config
from fastapi import FastAPI

if os.environ.get("KUBERNETES_SERVICE_HOST"):
    config.load_incluster_config()
else:
    config.load_kube_config()

coreV1 = client.CoreV1Api()


@dataclasses.dataclass
class Instance:
    name: str
    namespace: str
    available: bool

    @property
    def url(self) -> str:
        return f"http://{self.name}.pre.intra.starwhale.ai"


def check_controller_exists(namespace: str) -> bool:
    p = re.compile(r'controller-.*')
    pods = coreV1.list_namespaced_pod(namespace)
    return any(p.match(pod.metadata.name) for pod in pods.items)


def get_e2e_instances() -> typing.List[Instance]:
    p = re.compile(r'e2e-[0-9]{8}')
    ns = coreV1.list_namespace()

    ret = []
    for n in ns.items:
        name = n.metadata.name
        if not p.match(name):
            continue
        ins = Instance(name, name, check_controller_exists(n.metadata.name))
        ret.append(ins)

    return sorted(ret, key=lambda x: x.name, reverse=True)


def main():
    app = FastAPI()

    # index
    @app.get("/", response_class=fastapi.responses.HTMLResponse)
    def read_root():
        ins = get_e2e_instances()
        style = "<style>table, th, td {border: 1px solid black; border-collapse: collapse;}</style>"
        html = "<table>"
        html += "<tr><th>name</th><th>available</th></tr>"
        for i in ins:
            html += f"<tr><td><a target=\"_blank\" href=\"{i.url}\">{i.name}</a></td><td>{i.available and 'OK' or 'Die'}</td></tr>"
        html += "</table>"
        return style + html

    # serve
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == '__main__':
    main()
