#!/usr/bin/env bash
# Downloads the 3D library files the app needs into web/lib
set -euo pipefail
mkdir -p web/lib
BASE=https://cdn.jsdelivr.net/npm/three@0.128.0
curl -fsSL "$BASE/build/three.min.js" -o web/lib/three.min.js
curl -fsSL "$BASE/examples/js/controls/OrbitControls.js" -o web/lib/OrbitControls.js
curl -fsSL "$BASE/examples/js/utils/BufferGeometryUtils.js" -o web/lib/BufferGeometryUtils.js
