import os
import subprocess
import time
from multiprocessing import Process, Queue, Manager

import markdown

from config import Config

def md_to_html_worker(q: Queue, raw_md_tex: str):
    try:
        html_body = markdown.markdown(
            raw_md_tex, extensions=['fenced_code', 'codehilite'])
        q.put(('ok', html_body))
    except Exception:
        import traceback
        q.put(('err', traceback.format_exc()))

def md_to_html(raw_md_tex: str, thread=None) -> str:

    q = Queue()
    p = Process(target=md_to_html_worker, args=(q, raw_md_tex))
    p.start()

    while p.is_alive():
        if thread and thread.isInterruptionRequested():
            print("Terminating md to html worker...")
            p.terminate()
            p.join()
            raise Exception("Compilation interrupted")
        time.sleep(0.1)
    
    html_body: str = ""
    if not q.empty():
        status, value = q.get()
        if status == 'ok':
            html_body = value
        else:
            raise Exception(f"Compilation failed: {value}")
    else:
        raise Exception("Empty Queue")
    
    return html_body
    
def compile_by_katex_worker(q: Queue, html_body: str):
    script_filename = f"{os.urandom(6).hex()}.js"
    script_path = os.path.join(Config.KATEX_WORKING_DIR, script_filename)
    output_filename = f"{os.urandom(6).hex()}.html"
    output_path = os.path.join(Config.KATEX_WORKING_DIR, output_filename)
    try:
        script = r"""
const katex = require('katex');
const { JSDOM } = require('jsdom');

const inputHtml = `
{{HTML_BODY}}
`;

function convertLatexToStaticHtml(html) {
    const dom = new JSDOM(html);
    const document = dom.window.document;

    // A recursive function to walk through text nodes
    function processNode(node) {
        if (node.nodeType === 3) { // Text node
            let text = node.nodeValue;
            
            // 1. Handle Display Math ($$ ... $$)
            text = text.replace(/\$\$(.+?)\$\$/g, (match, formula) => {
                return katex.renderToString(formula, { displayMode: true, throwOnError: false });
            });

            // 2. Handle Inline Math ($ ... $)
            text = text.replace(/\$(.+?)\$/g, (match, formula) => {
                return katex.renderToString(formula, { displayMode: false, throwOnError: false });
            });

            if (text !== node.nodeValue) {
                const replacement = document.createElement('span');
                replacement.innerHTML = text;
                node.parentNode.replaceChild(replacement, node);
            }
        } else {
            for (let i = 0; i < node.childNodes.length; i++) {
                processNode(node.childNodes[i]);
            }
        }
    }

    processNode(document.body);
    return dom.serialize();
}

const staticHtml = convertLatexToStaticHtml(inputHtml);

const fs = require('fs');

fs.writeFile('{{OUTPUT_FILENAME}}', staticHtml, (err) => {
  if (err) throw err;
  console.log('File saved!');
});
""".replace('{{HTML_BODY}}', html_body.replace('\\', '\\\\')).replace('{{OUTPUT_FILENAME}}', output_filename)
        
        with open(script_path, mode="w", encoding="utf8") as fp:
            fp.write(script)
        p = subprocess.Popen(
            ["node", script_filename], 
            cwd=Config.KATEX_WORKING_DIR, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            shell=True, 
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        stdout, stderr = p.communicate()
        if p.returncode:
            raise Exception(f"Node.js script execution error: \n{stdout}\n\n{stderr}")
        
        with open(output_path, mode="r", encoding="utf8") as fp:
            html = fp.read()
        
        q.put(('ok', html))
    except Exception:
        import traceback
        q.put(('err', traceback.format_exc()))
    finally:
        if os.path.isfile(script_path):
            os.remove(script_path)
        if os.path.isfile(output_path):
            os.remove(output_path)

def compile_by_katex(html_body: str, thread=None) -> str:
    
    manager = Manager()
    q = manager.Queue()
    p = Process(target=compile_by_katex_worker, args=(q, html_body))
    p.start()

    while p.is_alive():
        if thread and thread.isInterruptionRequested():
            print("Terminating katex compilation worker...")
            p.terminate()
            p.join()
            raise Exception("Compilation interrupted")
        time.sleep(0.1)
    
    if not q.empty():
        status, value = q.get()
        if status == 'ok':
            html_body = value
        else:
            raise Exception(f"Compilation failed: {value}")
    else:
        raise Exception(f"Empty Queue")
    
    return html_body

def compile_to_html(raw_md_tex: str, thread=None) -> str:

    html_body = md_to_html(raw_md_tex, thread)

    html_body = compile_by_katex(html_body, thread)
    
    full_html = f"""
<html>
<head>
    <style>
        body {{ font-family: sans-serif; padding: 20px; line-height: 1.6; }}
        code {{ background: #f4f4f4; padding: 2px 4px; }}
        .katex-html {{ display: none; }}
    </style>
</head>
<body>
{html_body}
</body>
</html>
"""
    return full_html
    

