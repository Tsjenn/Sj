#!/usr/bin/env python3
"""Diagrams for WORKING WITH INTELLIGENCE (bookfactory7).

    python3 scripts/ai_art.py          # render bookfactory7/art/chNN.png
    python3 scripts/ai_art.py cover    # dist/WorkingWithIntelligence-cover.jpg

Every chapter declares an art spec in plan.json:
    {"type": "flow", "title": "...", "labels": [...]}
Types: flow cycle matrix playbook stack tree compare anatomy grid
       checklist network ladder timeline
All art is parametric PIL drawing; nothing is traced from any source.
"""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BF   = os.path.join(ROOT, "bookfactory7")
OUT  = os.path.join(BF, "art")

PAPER=(244,246,248); NAVY=(15,36,56); INK=(22,33,58); CYAN=(31,168,199)
AMBER=(224,163,62); SLATE=(91,107,124); LIGHT=(219,227,233); WHITE=(255,255,255)
W,H = 1200,780

def font(sz, bold=False):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
              "/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf" % ("Bold" if bold else "Regular")):
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur+" "+w_).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w_
    if cur: lines.append(cur)
    return lines

def ctext(d, box, text, f, fill=NAVY, lead=4):
    x0,y0,x1,y1 = box
    lines = wrap(d, text, f, (x1-x0)-14)
    lh = f.size + lead
    ty = (y0+y1)/2 - len(lines)*lh/2
    for ln in lines:
        d.text(((x0+x1)/2 - d.textlength(ln,font=f)/2, ty), ln, font=f, fill=fill)
        ty += lh

def box(d, x0,y0,x1,y1, text, fill=WHITE, edge=NAVY, tcol=NAVY, sz=20, bold=False, r=10, wgt=3):
    d.rounded_rectangle([x0,y0,x1,y1], radius=r, fill=fill, outline=edge, width=wgt)
    ctext(d, (x0,y0,x1,y1), text, font(sz,bold), tcol)

def arrow(d, x0,y0,x1,y1, col=CYAN, wgt=4, head=13):
    d.line([(x0,y0),(x1,y1)], fill=col, width=wgt)
    a = math.atan2(y1-y0, x1-x0)
    d.polygon([(x1,y1),
               (x1-head*math.cos(a-0.42), y1-head*math.sin(a-0.42)),
               (x1-head*math.cos(a+0.42), y1-head*math.sin(a+0.42))], fill=col)

def canvas(title):
    im = Image.new("RGB",(W,H),PAPER); d = ImageDraw.Draw(im)
    d.rectangle([0,0,W,10], fill=NAVY)
    f = font(30,True)
    for ln_i, ln in enumerate(wrap(d,title,f,W-160)[:2]):
        d.text((70, 46+ln_i*38), ln, font=f, fill=NAVY)
    d.line([(70,124),(150,124)], fill=CYAN, width=5)
    return im, d

# ---------- diagram types ----------
def t_flow(d, L):
    n=len(L); rows=[L] if n<=4 else [L[:math.ceil(n/2)], L[math.ceil(n/2):]]
    ytop=190; rowh=210
    for ri,row in enumerate(rows):
        k=len(row); m=54; bw=(W-2*m-(k-1)*58)/k; y0=ytop+ri*rowh; y1=y0+150
        for i,lab in enumerate(row):
            x0=m+i*(bw+58); x1=x0+bw
            box(d,x0,y0,x1,y1,lab,WHITE,NAVY,NAVY,19,False)
            d.ellipse([x0+10,y0+10,x0+40,y0+40], fill=CYAN)
            num = sum(len(r) for r in rows[:ri])+i+1
            fn=font(16,True); d.text((x0+25-d.textlength(str(num),font=fn)/2, y0+16), str(num), font=fn, fill=WHITE)
            if i<k-1: arrow(d,x1+10,(y0+y1)/2,x0+bw+48,(y0+y1)/2)
        if ri==0 and len(rows)>1:
            arrow(d, W-m-bw/2, y1+8, W-m-bw/2, y1+40)
            d.line([(W-m-bw/2,y1+40),(m+bw/2,y1+40)], fill=CYAN, width=4)
            arrow(d, m+bw/2, y1+40, m+bw/2, ytop+rowh-8)

def t_cycle(d, L):
    cx,cy,R = W/2, 470, 210; n=len(L)
    for i,lab in enumerate(L):
        a = -math.pi/2 + i*2*math.pi/n
        x,y = cx+R*math.cos(a)*1.45, cy+R*math.sin(a)
        box(d,x-150,y-52,x+150,y+52,lab,WHITE,NAVY,NAVY,19)
        a2 = -math.pi/2 + (i+0.5)*2*math.pi/n
        x2,y2 = cx+ (R-10)*math.cos(a2)*1.45, cy+(R-10)*math.sin(a2)
        a3 = -math.pi/2 + (i+0.62)*2*math.pi/n
        arrow(d, x2, y2, cx+(R-10)*math.cos(a3)*1.45, cy+(R-10)*math.sin(a3))
    d.ellipse([cx-52,cy-52,cx+52,cy+52], outline=CYAN, width=5)

def t_matrix(d, L, quad_only=False):
    if len(L)>=8: axes,quads = L[:4],L[4:8]
    else: axes,quads = None,(L+["","","",""])[:4]
    x0,y0,x1,y1 = 250,190,1010,700; mx,my=(x0+x1)/2,(y0+y1)/2
    cols=[(232,245,248),(252,244,228),(240,243,245),(246,238,238)]
    for i,(qx0,qy0,qx1,qy1) in enumerate([(x0,y0,mx,my),(mx,y0,x1,my),(x0,my,mx,y1),(mx,my,x1,y1)]):
        d.rectangle([qx0,qy0,qx1,qy1], fill=cols[i], outline=SLATE, width=2)
        ctext(d,(qx0,qy0,qx1,qy1),quads[i],font(21,True),NAVY)
    d.line([(x0,my),(x1,my)],fill=NAVY,width=4); d.line([(mx,y0),(mx,y1)],fill=NAVY,width=4)
    if axes:
        f=font(17,True)
        d.text((mx-d.textlength(axes[0],font=f)/2, y0-32), axes[0], font=f, fill=SLATE)
        d.text((mx-d.textlength(axes[1],font=f)/2, y1+12), axes[1], font=f, fill=SLATE)
        for j,(ax,anchor) in enumerate(((axes[2],x0-18),(axes[3],x1+18))):
            for k,ln in enumerate(wrap(d,ax,f,150)):
                wl=d.textlength(ln,font=f)
                d.text((anchor-wl if j==0 else anchor, my-20+k*22), ln, font=f, fill=SLATE)

def t_stack(d, L):
    n=len(L); m=200; top=200; hgt=min(96,(600-20*n)/n)
    for i,lab in enumerate(L):
        y0=top+i*(hgt+18); y1=y0+hgt
        shade=(15+i*8,36+i*14,56+i*16) if i<4 else NAVY
        box(d,m,y0,W-m,y1,lab,shade,NAVY,WHITE,20,True,8,2)
        if i<n-1: arrow(d,W/2,y1+2,W/2,y1+16,SLATE,3,8)

def t_tree(d, L):
    root=L[0]; kids=L[1:]
    box(d,W/2-190,180,W/2+190,270,root,NAVY,NAVY,WHITE,22,True)
    k=len(kids); m=54; bw=(W-2*m-(k-1)*26)/k; y0=420; y1=y0+180
    d.line([(W/2,270),(W/2,350)], fill=CYAN, width=4)
    d.line([(m+bw/2,350),(m+(k-1)*(bw+26)+bw/2,350)], fill=CYAN, width=4)
    for i,lab in enumerate(kids):
        x0=m+i*(bw+26); x1=x0+bw
        arrow(d,x0+bw/2,350,x0+bw/2,y0-6)
        box(d,x0,y0,x1,y1,lab,WHITE,NAVY,NAVY,18)

def t_compare(d, L):
    cols=[c.split("|") for c in L][:2]
    for i,col in enumerate(cols):
        x0 = 70 + i*(W/2-40); x1 = x0 + (W/2-110)
        head=col[0]; items=col[1:]
        d.rounded_rectangle([x0,190,x1,262], radius=10, fill=(NAVY if i==0 else CYAN), outline=None)
        ctext(d,(x0,190,x1,262),head,font(24,True),WHITE)
        y=286
        for it in items:
            lines=wrap(d,it,font(19),(x1-x0)-56)
            hbox=len(lines)*26+26
            d.rounded_rectangle([x0,y,x1,y+hbox], radius=8, fill=WHITE, outline=LIGHT, width=2)
            d.ellipse([x0+16,y+hbox/2-6,x0+28,y+hbox/2+6], fill=(SLATE if i==0 else AMBER))
            ty=y+13
            for ln in lines:
                d.text((x0+42,ty), ln, font=font(19), fill=NAVY); ty+=26
            y+=hbox+14

def t_anatomy(d, L):
    cx,cy=W/2,470
    d.rounded_rectangle([cx-170,cy-90,cx+170,cy+90], radius=14, fill=NAVY)
    ctext(d,(cx-170,cy-90,cx+170,cy+90),"THE PROMPT" if len(L)>4 else "THE ANSWER",font(24,True),WHITE)
    n=len(L)
    for i,lab in enumerate(L):
        side = -1 if i < math.ceil(n/2) else 1
        idx  = i if side<0 else i-math.ceil(n/2)
        cnt  = math.ceil(n/2) if side<0 else n-math.ceil(n/2)
        y = 230 + idx*(460/max(cnt,1)) + (460/max(cnt,1))/2 - 46
        x0 = 60 if side<0 else W-490
        box(d,x0,y,x0+430,y+92,lab,WHITE,CYAN if side<0 else AMBER,NAVY,18)
        ty = max(cy-64, min(cy+64, y+46))
        arrow(d, (x0+430 if side<0 else x0), y+46, (cx-176 if side<0 else cx+176), ty, SLATE,3,10)

def t_grid(d, L):
    n=len(L); cols=4 if n>6 else 3; rows=math.ceil(n/cols)
    m=60; gw=(W-2*m-(cols-1)*22)/cols; gh=min(150,(560-(rows-1)*22)/rows)
    for i,lab in enumerate(L):
        r,cc = divmod(i,cols); x0=m+cc*(gw+22); y0=210+r*(gh+22)
        box(d,x0,y0,x0+gw,y0+gh,lab,WHITE,NAVY,NAVY,18,False,10,2)
        d.line([(x0,y0+gh-8),(x0+gw,y0+gh-8)], fill=CYAN if i%2==0 else AMBER, width=6)

def t_checklist(d, L):
    m=140; y=200
    for lab in L:
        lines=wrap(d,lab,font(21),W-2*m-90); hbox=len(lines)*30+30
        d.rounded_rectangle([m,y,W-m,y+hbox], radius=10, fill=WHITE, outline=LIGHT, width=2)
        d.rounded_rectangle([m+20,y+hbox/2-17,m+54,y+hbox/2+17], radius=6, outline=NAVY, width=3)
        d.line([(m+28,y+hbox/2),(m+36,y+hbox/2+10)], fill=CYAN, width=5)
        d.line([(m+36,y+hbox/2+10),(m+48,y+hbox/2-10)], fill=CYAN, width=5)
        ty=y+15
        for ln in lines:
            d.text((m+76,ty), ln, font=font(21), fill=NAVY); ty+=30
        y+=hbox+14

def t_network(d, L):
    hub=L[0]; spokes=L[1:]; cx,cy=W/2,470
    n=len(spokes)
    for i,lab in enumerate(spokes):
        a=-math.pi/2+i*2*math.pi/n; x,y=cx+330*math.cos(a)*1.35, cy+250*math.sin(a)
        d.line([(cx,cy),(x,y)], fill=SLATE, width=3)
        box(d,x-140,y-42,x+140,y+42,lab,WHITE,CYAN,NAVY,18,False,22,3)
    d.ellipse([cx-110,cy-72,cx+110,cy+72], fill=NAVY)
    ctext(d,(cx-110,cy-72,cx+110,cy+72),hub,font(22,True),WHITE)

def t_ladder(d, L):
    n=len(L); base_y=700; step=(base_y-210)/n
    for i,lab in enumerate(L):
        y1=base_y-i*step; y0=y1-step+14
        x0=110+i*((W-260)/n*0.55); x1=x0+560
        box(d,x0,y0,x1,y1,lab,WHITE,NAVY,NAVY,20,False,10,3)
        d.rectangle([x0,y0,x0+12,y1], fill=CYAN if i%2==0 else AMBER)
        if i<n-1: arrow(d,x1+8,(y0+y1)/2, x1+8, y0-step+30, SLATE,3,9)

def t_timeline(d, L):
    y=470; m=110
    d.line([(m,y),(W-m,y)], fill=NAVY, width=6)
    n=len(L); step=(W-2*m)/max(n-1,1)
    for i,lab in enumerate(L):
        x=m+i*step
        d.ellipse([x-16,y-16,x+16,y+16], fill=CYAN, outline=NAVY, width=4)
        up = (i%2==0)
        y0 = y-190 if up else y+52
        box(d,x-150,y0,x+150,y0+130,lab,WHITE,NAVY,NAVY,19)
        d.line([(x, y0+130 if up else y0),(x, y-18 if up else y+18)], fill=SLATE, width=3)

TYPES = {"flow":t_flow,"cycle":t_cycle,"matrix":t_matrix,"playbook":t_matrix,"stack":t_stack,
         "tree":t_tree,"compare":t_compare,"anatomy":t_anatomy,"grid":t_grid,
         "checklist":t_checklist,"network":t_network,"ladder":t_ladder,"timeline":t_timeline}

def make_cover(path):
    CW,CH=1600,2560
    im=Image.new("RGB",(CW,CH),NAVY); d=ImageDraw.Draw(im)
    for y in range(CH):
        t=y/CH; d.line([(0,y),(CW,y)], fill=(int(15+26*t),int(36+30*t),int(56+34*t)))
    # constellation motif: an evenly spread, connected network (not a brain)
    import random, math
    rnd=random.Random(11)
    X0,X1,Y0,Y1=130,CW-130,170,1040
    cols,rows=8,5
    cw=(X1-X0)/cols; chh=(Y1-Y0)/rows
    pts=[]
    for r in range(rows):
        for c in range(cols):
            if rnd.random()<0.10:      # a few gaps, so it is not a lattice
                continue
            x=X0+cw*(c+0.5)+rnd.uniform(-cw*0.34,cw*0.34)
            y=Y0+chh*(r+0.5)+rnd.uniform(-chh*0.34,chh*0.34)
            pts.append((x,y))
    # link each node to its three nearest neighbours -> one connected web
    seen=set()
    for i,(x,y) in enumerate(pts):
        order=sorted(range(len(pts)), key=lambda j:(pts[j][0]-x)**2+(pts[j][1]-y)**2)
        for j in order[1:4]:
            k=(min(i,j),max(i,j))
            if k in seen: continue
            seen.add(k)
            d.line([(x,y),pts[j]], fill=(40,78,108), width=2)
    for i,(x,y) in enumerate(pts):
        r=5 if i%4 else 10
        col=AMBER if i%6==0 else CYAN
        d.ellipse([x-r,y-r,x+r,y+r], fill=col)
    d.rectangle([0,1120,CW,1128], fill=CYAN)
    ft=font(150,True)
    for i,wd in enumerate(["WORKING","WITH","INTELLIGENCE"]):
        sz=150
        while d.textlength(wd,font=font(sz,True))>CW-200 and sz>60: sz-=4
        f=font(sz,True); d.text(((CW-d.textlength(wd,font=f))/2, 1230+i*182), wd, font=f, fill=WHITE)
    sub="The Professional's Complete Guide to AI"
    sz=58
    while d.textlength(sub,font=font(sz))>CW-260 and sz>28: sz-=2
    f=font(sz); d.text(((CW-d.textlength(sub,font=f))/2, 1830), sub, font=f, fill=(196,214,226))
    sub2="Prompting · Projects · Agents · Industry Playbooks"
    sz=44
    while d.textlength(sub2,font=font(sz))>CW-260 and sz>24: sz-=2
    f2=font(sz); d.text(((CW-d.textlength(sub2,font=f2))/2, 1912), sub2, font=f2, fill=CYAN)
    d.line([(CW/2-320,2210),(CW/2+320,2210)], fill=AMBER, width=4)
    fa=font(76,True); auth="TANG SHIUAN JENN"
    d.text(((CW-d.textlength(auth,font=fa))/2, 2250), auth, font=fa, fill=WHITE)
    fb=font(38); bl="Chartered Accountant"
    d.text(((CW-d.textlength(bl,font=fb))/2, 2350), bl, font=fb, fill=(176,196,210))
    im.save(path,"JPEG",quality=92); print("cover ->", path)

def main():
    plan=json.load(open(os.path.join(BF,"plan.json")))
    os.makedirs(OUT, exist_ok=True); n=0
    for part in plan["parts"]:
        for ch in part["chapters"]:
            spec=ch["art"]; im,d=canvas(spec["title"])
            TYPES[spec["type"]](d, spec["labels"])
            im.save(os.path.join(OUT, ch["id"]+".png"), optimize=True); n+=1
    print("rendered %d diagrams -> %s" % (n,OUT))

if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1]=="cover":
        os.makedirs(os.path.join(ROOT,"dist"),exist_ok=True)
        make_cover(os.path.join(ROOT,"dist","WorkingWithIntelligence-cover.jpg"))
    else: main()
