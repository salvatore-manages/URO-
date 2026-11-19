"""Generate URO V1 PCB footprints and net assignments from scripts/design.py."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
from design import design, PROJECT

X0,Y0,W,H = 100.0,100.0,60.0,60.0
PLACE = {
 "U1":(130.0,112.75,0),
 "J1":(134.5,153.5,180),
 "J2":(156.0,139.0,90),
 "J3":(155.0,145.0,0),
 "J4":(110.0,132.0,90),
 "J5":(148.0,131.0,270),
 "J6":(105.0,149.0,0),
 "U2":(118.0,145.5,0),
 "U3":(146.0,146.0,0),
 "U4":(122.5,145.5,0),
 "U5":(133.0,139.0,0),
 "U6":(121.0,150.0,0),
 "L1":(133.0,141.8,180),
 "R1":(126.5,141.5,90),"R2":(145.0,151.0,90),
 "R3":(115.5,112.5,0),"R4":(135.0,146.0,90),"R5":(140.0,146.0,90),
 "R6":(116.0,152.0,0),"R7":(116.0,153.5,0),"R8":(149.0,143.0,90),
 "C1":(117.0,139.0,90),"C2":(121.0,141.5,90),"C3":(126.5,149.0,90),
 "C4":(127.0,134.0,90),"C5":(129.0,141.5,90),"C6":(136.5,141.5,90),
 "C7":(139.5,141.5,90),"C8":(142.5,141.5,90),"C9":(129.5,136.5,0),
 "C10":(115.5,115.5,0),"C11":(115.5,109.5,0),"C12":(116.5,149.0,0),
 "C13":(147.0,151.0,90),"C14":(151.0,154.5,90),
}
LIBROOT="/usr/share/kicad/footprints"

def make_tps63020(board):
    fp=pcbnew.FOOTPRINT(board)
    fp.SetFPID(pcbnew.LIB_ID("parts","TPS63020"))
    fp.SetReference("U5"); fp.SetValue("TPS63020DSJR")
    fp.SetLibDescription("TI TPS63020 VSON-14 3x4mm, 0.5mm pitch, exposed PGND pad")
    fp.SetAttributes(pcbnew.FP_SMD)
    fp.SetPosition(pcbnew.VECTOR2I_MM(133.0,139.0))
    def addpad(num,x,y,sx,sy):
        pad=pcbnew.PAD(fp); pad.SetNumber(str(num)); pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT); pad.SetSize(pcbnew.VECTOR2I_MM(sx,sy))
        pad.SetRoundRectRadiusRatio(0.12)
        layers=pcbnew.LSET(); layers.AddLayer(pcbnew.F_Cu); layers.AddLayer(pcbnew.F_Paste); layers.AddLayer(pcbnew.F_Mask); pad.SetLayerSet(layers)
        pad.SetPosition(pcbnew.VECTOR2I_MM(133.0+x,139.0+y)); fp.Add(pad)
    # Pin table and package drawing from TI TPS63020 DSJ datasheet and PCBKit part footprint:
    # seven pins down the left edge (1..7), seven up the right (8..14), exposed PGND in centre.
    for i in range(7): addpad(i+1,-1.45,-1.5+0.5*i,0.25,0.70)
    for i in range(7): addpad(i+8,1.45,1.5-0.5*i,0.25,0.70)
    addpad(15,0,0,1.6,1.6)
    return fp

def load_fp(lib,name):
    if lib=="parts":
        fp=pcbnew.FootprintLoad(os.path.join(PROJECT,"parts.pretty"),name)
        if fp: return fp
    return pcbnew.FootprintLoad(os.path.join(LIBROOT,lib+".pretty"),name)

s=design()
b=pcbnew.LoadBoard(os.path.join(PROJECT,"board.kicad_pcb"))

# Keep the existing 60 x 60 mm Edge.Cuts outline and the ESP32 antenna keepout.
nets={}
for name in s.nets():
    n=b.FindNet(name)
    if n is None:
        n=pcbnew.NETINFO_ITEM(b,name); b.Add(n)
    nets[name]=n

for p in s.parts:
    ref=p["ref"]
    fp=b.FindFootprintByReference(ref)
    if fp is None:
        lib,name=p["footprint"].split(":",1)
        print("Loading",ref,lib,name)
        fp=make_tps63020(b) if ref=="U5" else load_fp(lib,name)
        if fp is None:
            print("FOOTPRINT FAILED",ref,p["footprint"])
            raise RuntimeError(f"Cannot load footprint {p['footprint']} for {ref}")
        fp.SetFPID(pcbnew.LIB_ID(lib,name))
        fp.SetReference(ref)
        for k,v in p["fields"].items():
            try: fp.SetField(k,str(v))
            except Exception: pass
        for fld in fp.GetFields():
            if not fld.IsReference():
                fld.SetVisible(False); fld.SetLayer(pcbnew.F_Fab)
        b.Add(fp)
    if ref not in PLACE:
        raise RuntimeError(f"No placement for {ref}")
    fp.SetValue(p["value"])
    for k,v in p["fields"].items():
        try: fp.SetField(k,str(v))
        except Exception: pass
    x,y,a=PLACE[ref]
    fp.SetPosition(pcbnew.VECTOR2I_MM(x,y)); fp.SetOrientationDegrees(a)
    if ref=="U5":
        for pad in fp.Pads():
            pn=int(pad.GetNumber()) if pad.GetNumber().isdigit() else 0
            if 1 <= pn <= 9: pad.SetOrientationDegrees(270)
            elif 10 <= pn <= 14: pad.SetOrientationDegrees(90)
            else: pad.SetOrientationDegrees(0)
        for graphic in list(fp.GraphicalItems()): fp.Remove(graphic)
    for pad in fp.Pads():
        netname=next((part["nets"].get(pad.GetNumber()) for part in s.parts if part["ref"]==ref),None)
        if netname and netname in nets:
            pad.SetNet(nets[netname])
        else:
            pad.SetNetCode(0)

# Keep the single back-side GND plane. Its net, layer and fill are explicit.
zones=list(b.Zones())
gnd_zone=next((z for z in zones if z.GetNetname()=="GND"),None)
if gnd_zone is None:
    raise RuntimeError("GND copper zone missing; restore the board's B.Cu ground zone before continuing")
gnd_zone.SetNetCode(nets["GND"].GetNetCode())
gnd_zone.SetLayer(pcbnew.B_Cu)
gnd_zone.SetLocalClearance(pcbnew.FromMM(0.25))
gnd_zone.SetThermalReliefGap(pcbnew.FromMM(0.25))
gnd_zone.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.3))
filler=pcbnew.ZONE_FILLER(b); filler.Fill(b.Zones())

b.Save(os.path.join(PROJECT,"board.kicad_pcb"))
print("Wrote",len(s.parts),"footprints and",len(s.nets()),"nets")
