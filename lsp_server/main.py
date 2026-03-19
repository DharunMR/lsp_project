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

class LanguageServer:
    def __init__(self):
        self.workspace = WorkspaceManager()

    def send(self, data):
        """Binary-safe output for JSON-RPC."""
        # ADD THIS LINE to inject the jsonrpc version
        data["jsonrpc"] = "2.0" 
        
        body = json.dumps(data, separators=(",", ":")).encode("utf-8")
        sys.stdout.buffer.write(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii"))
        sys.stdout.buffer.write(body)
        sys.stdout.buffer.flush()

    def publish_diagnostics(self, uri, diagnostics):
        self.send({"method": "textDocument/publishDiagnostics", "params": {"uri": uri, "diagnostics": diagnostics}})

    def serve(self):
        logger.info("Server started.")
        while True:
            try:
                line = sys.stdin.readline()
                if not line: break
                if not line.startswith("Content-Length"): continue
                
                length = int(line.split(":")[1].strip())
                sys.stdin.readline() # Consume blank line
                req = json.loads(sys.stdin.read(length))
                
                method = req.get("method")
                rid = req.get("id")
                params = req.get("params", {})
                
                logger.debug(f"Received method: {method}")

                # --- 1. Server Lifecycle & Synchronization ---
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
                    text = params['contentChanges'][0]['text'] if 'contentChanges' in params else params['textDocument']['text']
                    diagnostics = self.workspace.update(uri, text)
                    self.publish_diagnostics(uri, diagnostics)

                # --- 2. Feature Dispatching ---
                doc = self.workspace.get(params.get('textDocument', {}).get('uri'))
                if not doc: continue

                pos = params.get('position', {})
                line_no, char_no = pos.get('line', 0), pos.get('character', 0)

                if method == "textDocument/completion":
                    self.send({"id": rid, "result": completion.get_completions(doc)})
                
                elif method == "textDocument/hover":
                    self.send({"id": rid, "result": hover.get_hover(doc, line_no, char_no)})
                
                elif method in ["textDocument/definition", "textDocument/declaration"]:
                    self.send({"id": rid, "result": hover.get_definition(doc, line_no, char_no)})
                
                elif method == "textDocument/signatureHelp":
                    self.send({"id": rid, "result": hover.get_signature_help(doc, line_no, char_no)})
                
                elif method == "textDocument/documentHighlight":
                    self.send({"id": rid, "result": semantic.get_document_highlights(doc, line_no, char_no)})
                
                elif method == "textDocument/codeLens":
                    self.send({"id": rid, "result": folding.get_code_lens(doc)})
                
                elif method == "textDocument/foldingRange":
                    self.send({"id": rid, "result": folding.get_folding_ranges(doc)})
                
                elif method == "textDocument/semanticTokens/full":
                    self.send({"id": rid, "result": semantic.get_semantic_tokens(doc)})

            except Exception as e:
                logger.error(f"Error processing request: {traceback.format_exc()}")
                if rid: self.send({"id": rid, "error": {"code": -32603, "message": str(e)}})

if __name__ == "__main__":
    LanguageServer().serve()