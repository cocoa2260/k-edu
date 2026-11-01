"""python -m tools.stream_browser_lab --ui ../stream-ui --output NEW_DIR

Starts loopback server and Node/Playwright in one runtime process tree.
Build UI first; provide Playwright and optional executable via environment.
"""
import argparse
import os
from pathlib import Path
import subprocess
import threading
from tools.stream_lab import make_server


def run(ui,output):
    ui=Path(ui).resolve();output=Path(output).resolve()
    if output.exists():raise FileExistsError('New output required')
    server=make_server(ui/'dist');thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        subprocess.run([os.environ.get('CODEX_PRIMARY_RUNTIME_NODE','node'),str(ui/'tests/browser-check.mjs'),f'http://127.0.0.1:{server.server_port}',str(output)],check=True,timeout=90)
    finally:server.shutdown();server.server_close();thread.join(timeout=2)


if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--ui',required=True);p.add_argument('--output',required=True);a=p.parse_args();run(a.ui,a.output)
