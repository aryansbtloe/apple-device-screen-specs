#!/bin/bash
# Build the probe app and run it on every iPhone/iPad/iPod device type, max 2 booted at once.
# Usage: run_all.sh <workdir>   (runtime per device type: newest installed iOS runtime that lists it in supportedDeviceTypes)
set -u
W="$1"; cd "$W"
mkdir -p out logs build/Measure.app
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
xcrun --sdk iphonesimulator swiftc -parse-as-library -module-name Measure -target arm64-apple-ios27.0-simulator -sdk "$SDK" -O Measure.swift -o build/Measure.app/Measure || exit 1
cp Info.plist build/Measure.app/Info.plist
codesign -f -s - build/Measure.app >/dev/null 2>&1
python3 - > types.tsv <<'PY'
import json,subprocess
d=json.loads(subprocess.check_output(['xcrun','simctl','list','devicetypes','-j']))['devicetypes']
rts=json.loads(subprocess.check_output(['xcrun','simctl','list','runtimes','-j']))['runtimes']
rts=[r for r in rts if r.get('platform')=='iOS' and r.get('isAvailable')]
rts.sort(key=lambda r:[int(x) for x in r['version'].split('.')], reverse=True)
for t in d:
    if t.get('productFamily') in ('iPhone','iPad'):
        rt=next((r['identifier'] for r in rts if any(s['identifier']==t['identifier'] for s in r.get('supportedDeviceTypes',[]))),'NONE')
        print(t['identifier']+'\t'+t['name']+'\t'+rt)
PY
measure() {  # $1 typeid $2 name $3 runtime
  local tid="$1" name="$2" RT="$3" slug udid
  slug=$(echo "$name" | tr -c 'A-Za-z0-9' '-' | sed 's/-\{2,\}/-/g; s/-$//')
  if [ "$RT" = NONE ]; then echo -e "$name\t$tid\tUNSUPPORTED\tnot in supportedDeviceTypes of any installed iOS runtime" >> status.tsv; return; fi
  udid=$(xcrun simctl create "ssm-$slug" "$tid" "$RT" 2>logs/$slug.create.err | grep -E '^[0-9A-F-]{36}$')
  if [ -z "$udid" ]; then echo -e "$name\t$tid\tUNSUPPORTED\t$(tr '\n' ' ' < logs/$slug.create.err)" >> status.tsv; return; fi
  echo "$udid" >> created_udids.txt
  xcrun simctl boot "$udid" 2>>logs/$slug.err
  xcrun simctl bootstatus "$udid" -b >/dev/null 2>>logs/$slug.err
  xcrun simctl install "$udid" build/Measure.app 2>>logs/$slug.err
  ( xcrun simctl launch --console-pty "$udid" com.ssm.measure > logs/$slug.console.txt 2>&1 & )
  local ok=0
  for i in $(seq 1 60); do
    sleep 1
    local c; c=$(xcrun simctl get_app_container "$udid" com.ssm.measure data 2>/dev/null)
    if [ -n "$c" ] && [ -f "$c/Documents/measure.json" ]; then cp "$c/Documents/measure.json" "out/$slug.json"; ok=1; break; fi
  done
  xcrun simctl terminate "$udid" com.ssm.measure >/dev/null 2>&1
  xcrun simctl shutdown "$udid" 2>>logs/$slug.err
  xcrun simctl delete "$udid" 2>>logs/$slug.err
  if [ $ok = 1 ]; then echo -e "$name\t$tid\tOK\t$udid\t$RT" >> status.tsv; else echo -e "$name\t$tid\tNO_OUTPUT\t$udid\t$RT" >> status.tsv; fi
}
: > status.tsv
worker() { local n=0; while IFS=$'\t' read -r tid name rt; do n=$((n+1)); [ $((n % 2)) = "$1" ] && measure "$tid" "$name" "$rt" < /dev/null; done < types.tsv; }
if [ "${ONLY:-}" != "" ]; then grep -F "$ONLY" types.tsv | while IFS=$'\t' read -r tid name rt; do measure "$tid" "$name" "$rt" < /dev/null; done; exit 0; fi
worker 0 & worker 1 & wait
echo DONE
