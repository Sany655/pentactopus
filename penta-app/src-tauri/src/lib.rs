use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::{CommandEvent, CommandChild};
use std::sync::Mutex;

/// Holds the sidecar child process so it is killed when the app exits.
struct SidecarChild(Mutex<Option<CommandChild>>);

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
        .manage(SidecarChild(Mutex::new(None)))
        .setup(|app| {
            // Spawn the penta_daemon sidecar (desktop only)
            #[cfg(not(mobile))]
            {
                if let Ok(sidecar_command) = app.shell().sidecar("penta_daemon") {
                    match sidecar_command.spawn() {
                        Ok((mut rx, child)) => {
                            // Store child handle — Tauri will call kill() when the app exits
                            *app.state::<SidecarChild>().0.lock().unwrap() = Some(child);

                            tauri::async_runtime::spawn(async move {
                                while let Some(event) = rx.recv().await {
                                    match event {
                                        CommandEvent::Stdout(line) => {
                                            println!("[penta_daemon] {}", String::from_utf8_lossy(&line));
                                        }
                                        CommandEvent::Stderr(line) => {
                                            eprintln!("[penta_daemon ERR] {}", String::from_utf8_lossy(&line));
                                        }
                                        CommandEvent::Terminated(payload) => {
                                            println!("[penta_daemon] exited with code {:?}", payload.code);
                                            break;
                                        }
                                        _ => {}
                                    }
                                }
                            });
                        }
                        Err(e) => {
                            eprintln!("[penta_daemon] Failed to spawn sidecar: {e}");
                        }
                    }
                }
            }

            Ok(())
        })
        // Kill the daemon when the last window is closed
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                if let Some(mut child) = window
                    .state::<SidecarChild>()
                    .0
                    .lock()
                    .unwrap()
                    .take()
                {
                    let _ = child.kill();
                }
            }
        })
        .invoke_handler(tauri::generate_handler![get_device_info])
        .run(tauri::generate_context!())
        .expect("error while running penta-assistant application");
}
