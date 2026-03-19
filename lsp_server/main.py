import sys
import json
import os
import logging
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from manager import WorkspaceManager
from features import completion, hover, semantic, folding

logging.basicConfig(filename='lsp.log', level=logging.DEBUG, filemode='w')
logger = logging.getLogger("LSP")

RAW_RPC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw_rpc.txt")

class LanguageServer:
    def __init__(self):
        self.workspace = WorkspaceManager()
        with open(RAW_RPC_FILE, "w", encoding="utf-8") as f:
            f.write("=== PRETTIFIED LSP SESSION ===\n")

    def log_prettier_rpc(self, direction, header, body_dict):
        """Logs a readable, indented version of the JSON-RPC traffic."""
        try:
            pretty_json = json.dumps(body_dict, indent=4)
            with open(RAW_RPC_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n{direction}\n")
                f.write(header)
                f.write(pretty_json)
                f.write("\n" + "-"*50 + "\n")
        except Exception as e:
            logger.error(f"Logging failed: {e}")

    def send(self, data):
        """Sends compact JSON to IDE, but logs pretty JSON to file."""
        data["jsonrpc"] = "2.0" 
        
        compact_json = json.dumps(data, separators=(",", ":"))
        body_bytes = compact_json.encode("utf-8")
        
        header = f"Content-Length: {len(body_bytes)}\r\n\r\n"
        
        self.log_prettier_rpc(">>> SENT TO IDE >>>", header, data)

        sys.stdout.buffer.write(header.encode("ascii"))
        sys.stdout.buffer.write(body_bytes)
        sys.stdout.buffer.flush()

    def publish_diagnostics(self, uri, diagnostics):
        self.send({
            "method": "textDocument/publishDiagnostics", 
            "params": {"uri": uri, "diagnostics": diagnostics}
        })

    def serve(self):
        logger.info("LSP Server online.")
        while True:
            try:
                line = sys.stdin.readline()
                if not line: break
                if line.startswith("Content-Length"):
                    length = int(line.split(":")[1].strip())
                    sys.stdin.readline()
                    
                    raw_body = sys.stdin.read(length)
                    req = json.loads(raw_body)
                    
                    self.log_prettier_rpc("<<< RECEIVED FROM IDE <<<", f"Content-Length: {length}\r\n\r\n", req)
                    
                    method = req.get("method")
                    rid = req.get("id")
                    params = req.get("params", {})

                    if method == "initialize":
                        self.send({"id": rid, "result": {"capabilities": {
                            "textDocumentSync": 1,
                            "completionProvider": {"triggerCharacters": [" ", "."]},
                            "hoverProvider": True,
                            "definitionProvider": True,
                            "declarationProvider": True,
                            "signatureHelpProvider": {"triggerCharacters": ["("]},
                            "codeLensProvider": {"resolveProvider": False},
                            "foldingRangeProvider": True,
                            "documentHighlightProvider": True,
                            "semanticTokensProvider": {
                                "legend": {"tokenTypes": ["variable", "function", "keyword"], "tokenModifiers": []},
                                "full": True
                            }
                        }}})
                    
                    elif method in ["textDocument/didOpen", "textDocument/didChange"]:
                        uri = params['textDocument']['uri']
                        if 'contentChanges' in params:
                            text = params['contentChanges'][0]['text']
                        else:
                            text = params['textDocument']['text']
                            
                        diagnostics = self.workspace.update(uri, text)
                        self.publish_diagnostics(uri, diagnostics)

                    doc = self.workspace.get(params.get('textDocument', {}).get('uri'))
                    if not doc: continue

                    pos = params.get('position', {})
                    l, c = pos.get('line', 0), pos.get('character', 0)

                    handlers = {
                        "textDocument/completion": lambda: completion.get_completions(doc, l, c),
                        "textDocument/hover": lambda: hover.get_hover(doc, l, c),
                        "textDocument/definition": lambda: hover.get_definition(doc, l, c),
                        "textDocument/declaration": lambda: hover.get_definition(doc, l, c),
                        "textDocument/signatureHelp": lambda: hover.get_signature_help(doc, l, c),
                        "textDocument/documentHighlight": lambda: semantic.get_document_highlights(doc, l, c),
                        "textDocument/codeLens": lambda: folding.get_code_lens(doc),
                        "textDocument/foldingRange": lambda: folding.get_folding_ranges(doc),
                        "textDocument/semanticTokens/full": lambda: semantic.get_semantic_tokens(doc),
                    }

                    if method in handlers:
                        self.send({"id": rid, "result": handlers[method]()})

            except Exception as e:
                stack = traceback.format_exc()
                logger.error(f"Crash: {stack}")
                with open(RAW_RPC_FILE, "a") as f:
                    f.write(f"\n!!! CRASH !!!\n{stack}\n")
                if rid:
                    self.send({"id": rid, "error": {"code": -32603, "message": str(e)}})

if __name__ == "__main__":
    LanguageServer().serve()