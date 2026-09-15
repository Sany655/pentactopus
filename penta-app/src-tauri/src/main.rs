// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

#[tauri::command]
fn get_device_info() -> serde_json::Value {
    serde_json::json!({
        "platform": std::env::consts::OS,
        "arch": std::env::consts::ARCH,
        "name": "Penta-Host-Node"
    })
}

use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::CommandEvent;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // Spawn the penta_daemon sidecar
            let sidecar_command = app.shell().sidecar("penta_daemon")
                .expect("failed to setup `penta_daemon` sidecar");
            
            let (mut rx, _child) = sidecar_command
                .spawn()
                .expect("Failed to spawn sidecar");

            tauri::async_runtime::spawn(async move {
                // Read events such as stdout
                while let Some(event) = rx.recv().await {
                    if let CommandEvent::Stdout(line) = event {
                        println!("Sidecar: {:?}", String::from_utf8_lossy(&line));
                    }
                }
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_device_info])
        .run(tauri::generate_context!())
        .expect("error while running penta-assistant application");
}
