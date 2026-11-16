#!/usr/bin/env bash
# Package and sign the watch face. Needs the Android build tools (aapt, zipalign, apksigner) and an android.jar.
# Sign with YOUR OWN key:  KEYSTORE=~/my.jks KEY_ALIAS=me KS_PASS=secret ANDROID_JAR=/path/to/android.jar tools/build_apk.sh
set -euo pipefail
cd "$(dirname "$0")/.."
: "${KEYSTORE:?set KEYSTORE to your .jks}" "${KEY_ALIAS:?set KEY_ALIAS}" "${KS_PASS:?set KS_PASS}"
ANDROID_JAR="${ANDROID_JAR:-/usr/lib/android-sdk/platforms/android-23/android.jar}"
VERSION=$(grep -o 'versionName="[^"]*"' watchface/src/main/AndroidManifest.xml | cut -d'"' -f2)
mkdir -p out
aapt package -f -M watchface/src/main/AndroidManifest.xml -S watchface/src/main/res -I "$ANDROID_JAR" -F out/unsigned.apk
zipalign -f -p 4 out/unsigned.apk out/aligned.apk
apksigner sign --ks "$KEYSTORE" --ks-pass "pass:$KS_PASS" --ks-key-alias "$KEY_ALIAS" --v3-signing-enabled true \
  --out "out/LivingLake-watchface-v$VERSION.apk" out/aligned.apk
apksigner verify "out/LivingLake-watchface-v$VERSION.apk" && echo "built out/LivingLake-watchface-v$VERSION.apk"
