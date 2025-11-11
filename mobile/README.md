# Mobile (React Native / Expo) - Garbage Detection App

## Prereqs
- Node.js (16+)
- npm or yarn
- Expo CLI (optional but recommended): `npm install -g expo-cli`

## Setup
1. cd mobile
2. npm install
3. Edit BACKEND_URL in App.js to point to your backend (e.g. http://192.168.1.10:8000/predict)(Put your IP Address)
4. Run:
   expo start
   - use Expo Go on mobile or emulator

## Notes
- When running backend on local machine for a phone, use your machine IP (same LAN).
- To test from a phone not on the same LAN, use `ngrok http 8000` and set BACKEND_URL to the ngrok URL.
