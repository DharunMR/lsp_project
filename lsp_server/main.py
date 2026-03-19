import sys
import json
import os
import logging
import traceback

# Ensure internal modules are discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from manager import WorkspaceManager
from features import completion, hover, semantic, folding

# 1. Standard Logging (For human-readable debugging)
logging.basicConfig(filename='lsp.log', level=logging.DEBUG, filemode='w')
logger = logging.getLogger("LSP")

# 2. Raw RPC Capture (The .txt file for protocol verification)
RAW_RPC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw_rpc.txt")

class LanguageServer:
    def __init__(self):
        self.workspace = WorkspaceManager()
        # Clear the raw log on startup for a clean session
        with open(RAW_RPC_FILE, "w") as f:
            f.write("=== NEW LSP SESSION STARTED ===\n")

    def log_raw(self, direction, content):
        """Helper to write raw strings to the capture file."""
        with open(RAW_RPC_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{direction}\n")
            f.write(content)
            f.write("\n" + "="*40 + "\n")

    def send(self, data):
        """Constructs the full packet and sends it to the IDE."""
        # Inject protocol version
        data["jsonrpc"] = "2.0" 
        
        # 1. Generate JSON body
        body = json.dumps(data, separators=(",", ":"))
        body_bytes = body.encode("utf-8")
        
        # 2. Construct the exact header
        header = f"Content-Length: {len(body_bytes)}\r\n\r\n"
        full_packet = header + body

        # 3. MIRROR TO FILE (The raw .txt capture)
        self.log_raw(">>> SERVER RESPONSE >>>", full_packet)

        # 4. SEND TO SYSTEM STDOUT
        sys.stdout.buffer.write(header.encode("ascii"))
        sys.stdout.buffer.write(body_bytes)
        sys.stdout.buffer.flush()

    def publish_diagnostics(self, uri, diagnostics):
        self.send({
            "method": "textDocument/publishDiagnostics", 
            "params": {"uri": uri, "diagnostics": diagnostics}
        })

    def serve(self):
        logger.info("Server started and listening for JSON-RPC...")
        while True:
            try:
                # Read header
                line = sys.stdin.readline()
                if not line: break
                if line.startswith("Content-Length"):
                    length = int(line.split(":")[1].strip())
                    sys.stdin.readline() # Consume the empty \r\n
                    
                    # Read the raw JSON body
                    raw_json = sys.stdin.read(length)
                    
                    # Log the incoming IDE request
                    self.log_raw("<<< IDE REQUEST <<<", f"Content-Length: {length}\r\n\r\n{raw_json}")
                    
                    req = json.loads(raw_json)
                    method = req.get("method")
                    rid = req.get("id")
                    params = req.get("params", {})
                    
                    logger.debug(f"Processing method: {method}")

                    # --- Lifecycle ---
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
                                "legend": {
                                    "tokenTypes": ["variable", "function", "keyword"], 
                                    "tokenModifiers": []
                                },
                                "full": True
                            }
                        }}})
                    
                    elif method in ["textDocument/didOpen", "textDocument/didChange"]:
                        uri = params['textDocument']['uri']
                        text = params['contentChanges'][0]['text'] if 'contentChanges' in params else params['textDocument']['text']
                        diagnostics = self.workspace.update(uri, text)
                        self.publish_diagnostics(uri, diagnostics)

                    # --- Feature Dispatch ---
                    doc = self.workspace.get(params.get('textDocument', {}).get('uri'))
                    if not doc: continue

                    pos = params.get('position', {})
                    l, c = pos.get('line', 0), pos.get('character', 0)

                    if method == "textDocument/completion":
                        self.send({"id": rid, "result": completion.get_completions(doc)})
                    elif method == "textDocument/hover":
                        self.send({"id": rid, "result": hover.get_hover(doc, l, c)})
                    elif method in ["textDocument/definition", "textDocument/declaration"]:
                        self.send({"id": rid, "result": hover.get_definition(doc, l, c)})
                    elif method == "textDocument/signatureHelp":
                        self.send({"id": rid, "result": hover.get_signature_help(doc, l, c)})
                    elif method == "textDocument/documentHighlight":
                        self.send({"id": rid, "result": semantic.get_document_highlights(doc, l, c)})
                    elif method == "textDocument/codeLens":
                        self.send({"id": rid, "result": folding.get_code_lens(doc)})
                    elif method == "textDocument/foldingRange":
                        self.send({"id": rid, "result": folding.get_folding_ranges(doc)})
                    elif method == "textDocument/semanticTokens/full":
                        self.send({"id": rid, "result": semantic.get_semantic_tokens(doc)})

            except Exception as e:
                err_msg = traceback.format_exc()
                logger.error(f"Critical Error: {err_msg}")
                # Log the crash to the .txt file too
                self.log_raw("!!! SERVER ERROR !!!", err_msg)
                
                if rid:
                    self.send({"id": rid, "error": {"code": -32603, "message": str(e)}})

if __name__ == "__main__":
    LanguageServer().serve()