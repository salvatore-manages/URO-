#!/usr/bin/env python3
"""Generate a grouped procurement BOM from the current KiCad PCB."""
import csv
from collections import defaultdict
from pathlib import Path
import pcbnew

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / 'board.kicad_pcb'
OUT = ROOT / 'BOM.csv'

NOTES = {
    'J2': 'Requires a protected 1-cell LiPo pack with compatible 10k NTC lead; verify connector polarity and pack dimensions.',
    'J3': 'Speaker connector only; verify speaker impedance and rated power before fitting.',
    'J4': 'Connector only. Camera sensor/module and flex contact orientation are not yet selected.',
    'J5': 'Connector only. Display controller, resolution, flex orientation and backlight current must be confirmed.',
    'J6': '2x3 programming header: GND, 3V3, UART_TX, UART_RX, ESP_EN, BOOT0. 3.3V logic only.',
    'U1': 'ESP32-S3-WROOM-1-N16R8 module; verify exact module marking and antenna keep-out.',
    'U4': 'BQ24074 charger/power-path IC; use only with the specified protected 1-cell battery arrangement.',
    'U5': 'TPS63020 buck-boost regulator; verify inductor and capacitor effective values under DC bias.',
}

def fields(fp):
    return {f.GetName(): f.GetText() for f in fp.GetFields()}

board = pcbnew.LoadBoard(str(BOARD))
groups = defaultdict(list)
for fp in board.GetFootprints():
    ref = fp.GetReference()
    f = fields(fp)
    value = fp.GetValue()
    footprint = f'{fp.GetFPID().GetLibNickname()}:{fp.GetFPID().GetLibItemName()}'
    mpn = f.get('MPN', '').strip()
    lcsc = f.get('LCSC', '').strip()
    note = NOTES.get(ref, '')
    if not mpn and not lcsc and ref[:1] in ('C', 'R'):
        note = (note + ' ' if note else '') + 'Manufacturer part number and electrical rating are not specified; select and verify before ordering.'
    groups[(value, footprint, mpn, lcsc, note)].append(ref)

rows = []
for (value, footprint, mpn, lcsc, note), refs in groups.items():
    refs = sorted(refs, key=lambda x: (x.rstrip('0123456789'), int(''.join(c for c in x if c.isdigit()) or 0)))
    rows.append({
        'Designators': ', '.join(refs),
        'Value': value,
        'Manufacturer Part Number': mpn,
        'Footprint': footprint,
        'Qty': len(refs),
        'LCSC Part Number': lcsc,
        'Notes': note,
    })
rows.sort(key=lambda r: r['Designators'])
with OUT.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['Designators','Value','Manufacturer Part Number','Footprint','Qty','LCSC Part Number','Notes'])
    writer.writeheader(); writer.writerows(rows)
print(f'Wrote {OUT.name}: {len(rows)} grouped lines, {sum(r["Qty"] for r in rows)} total components.')
for row in rows:
    if row['Designators'] == 'U4': print('U4 order code:', row['LCSC Part Number'], row['Manufacturer Part Number'])
