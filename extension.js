const { LanguageClient } = require('vscode-languageclient/node');

function activate(context) {
    const serverOptions = {
        command: 'python3', 
        args: ['-u', '-m', 'lsp_server.main'],
        options: {
            cwd: context.extensionPath
        }
    };

    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'plaintext' }]
    };

    const client = new LanguageClient('fortlsPrep', 'Fortls GSoC Prep', serverOptions, clientOptions);
    client.start();
}
exports.activate = activate;