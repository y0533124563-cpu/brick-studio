#!/usr/bin/env bash
# Downloads the 3D library files the app needs into web/lib
set -euo pipefail
mkdir -p web/lib
BASE=https://cdn.jsdelivr.net/npm/three@0.128.0
curl -fsSL "$BASE/build/three.min.js" -o web/lib/three.min.js
curl -fsSL "$BASE/examples/js/controls/OrbitControls.js" -o web/lib/OrbitControls.js
curl -fsSL "$BASE/examples/js/utils/BufferGeometryUtils.js" -o web/lib/BufferGeometryUtils.js
# Google sign-in and cloud storage for projects (Firebase)
FB=https://cdn.jsdelivr.net/npm/firebase@10.12.2
curl -fsSL "$FB/firebase-app-compat.js" -o web/lib/firebase-app-compat.js
curl -fsSL "$FB/firebase-auth-compat.js" -o web/lib/firebase-auth-compat.js
curl -fsSL "$FB/firebase-firestore-compat.js" -o web/lib/firebase-firestore-compat.js
