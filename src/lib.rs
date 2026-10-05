use zed_extension_api as zed;

struct RevoExtension;

impl zed::Extension for RevoExtension {
    fn new() -> Self {
        Self
    }

    fn language_server_command(
        &mut self,
        _language_server_id: &zed::LanguageServerId,
        worktree: &zed::Worktree,
    ) -> zed::Result<zed::Command> {
        // Zed applies binary path, arguments and environment overrides itself.
        let command = worktree.which("revo").ok_or_else(|| {
            "Install revo or set lsp.revolt.binary.path in Zed settings".to_string()
        })?;
        Ok(zed::Command {
            command,
            args: vec!["lsp".to_string()],
            env: Vec::new(),
        })
    }
}

zed::register_extension!(RevoExtension);
