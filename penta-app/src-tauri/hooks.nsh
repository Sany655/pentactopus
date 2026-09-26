; NSIS post-uninstall hook to ensure complete zero-residue cleanup of AppData folders
!macro NSIS_HOOK_POSTUNINSTALL
  RMDir /r "$LOCALAPPDATA\PentaAssistant"
  RMDir /r "$LOCALAPPDATA\com.penta.assistant"
  RMDir /r "$APPDATA\com.penta.assistant"
  RMDir /r "$LOCALAPPDATA\Pentactopus"
!macroend
