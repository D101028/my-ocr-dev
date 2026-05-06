import os
from subprocess import Popen, PIPE, CREATE_NO_WINDOW

from config import Config

def md_to_html(raw_md: str) -> str:
    with open(os.path.join(Config.WORKING_DIR, "in.md"), mode="w", encoding="utf8") as fp:
        fp.write(raw_md)
    p = Popen(
        ["pandoc", "in.md", "-s", "--mathjax"], 
        cwd=Config.WORKING_DIR, 
        stdout=PIPE, 
        stderr=PIPE, 
        shell=True, 
        creationflags=CREATE_NO_WINDOW
    )
    stdout, stderr = p.communicate()

    if p.returncode:
        try:
            stdout = stdout.decode()
            stderr = stderr.decode()
        except:
            stdout = str(stdout)
            stderr = str(stderr)
        raise Exception(f"Pandoc Convert Error: stdout:\n{stdout}\n\nstderr:\n{stderr}")
    
    return stdout.decode()




