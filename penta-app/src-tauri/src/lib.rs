use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::CommandEvent;

#[tauri::command]
fn get_device_info() -> serde_json::Value {
    serde_json::json!({
        "platform": std::env::consts::OS,
        "arch": std::env::consts::ARCH,
        "name": "Penta-Host-Node"
    })
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // Spawn the penta_daemon sidecar
            #[cfg(not(mobile))]
            {
                if let Ok(sidecar_command) = app.shell().sidecar("penta_daemon") {
                    if let Ok((mut rx, _child)) = sidecar_command.spawn() {
                        tauri::async_runtime::spawn(async move {
                            // Read events such as stdout
                            while let Some(event) = rx.recv().await {
                                if let CommandEvent::Stdout(line) = event {
                                    println!("Sidecar: {:?}", String::from_utf8_lossy(&line));
                                }
                            }
                        });
                    }
                }
            }

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_device_info])
        .run(tauri::generate_context!())
        .expect("error while running penta-assistant application");
}
