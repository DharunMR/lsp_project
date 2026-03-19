const { LanguageClient } = require('vscode-languageclient/node');

function activate(context) {
    const serverOptions = {
        command: 'python3', 
        // '-u' ensures the output is unbuffered so the LSP messages send instantly
        args: ['-u', '-m', 'lsp_server.main'],
        options: {
            cwd: context.extensionPath // This tells Python to look in the project root
        }
    };

    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'plaintext' }]
    };

    const client = new LanguageClient('fortlsPrep', 'Fortls GSoC Prep', serverOptions, clientOptions);
    client.start();
}
exports.activate = activate;