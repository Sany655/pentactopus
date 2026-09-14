# Pentatopus v1.0.0 Launch Changelog

- **Brand Evolution**: Transitioned to Pentatopus with enterprise matte carbon UI.
- **Security Foundation**: Implemented PBKDF2 password hashing and 15-minute brute-force lockouts.
- **Persistence**: Added `DatabaseAdapter` for Supabase/Neon PostgreSQL support with fallback to local JSON.
- **Monetization**: Integrated Stripe Checkout and automated webhook license provisioning.
- **Client Binaries**: Automated compilation of the standalone Windows PyInstaller executable (`PentaAssistant-Setup.exe`).
- **AI Gateway**: Unified multi-model routing supporting Gemini 2.5 Flash, Anthropic, and open-source models.
