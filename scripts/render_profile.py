#!/usr/bin/env python3
"""Render the GitHub profile as self-contained SVG assets. Python standard library only."""
import argparse, base64, datetime as dt, html, json, math, os, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'profile'
BG, PANEL, BORDER, INK, MUTED = '#080E19', '#0D1522', '#223047', '#F0F5FF', '#9CABBF'
CYAN, VIOLET, PINK, GREEN = '#53D7F9', '#B994FF', '#F17BB5', '#50D9AB'
QUERY = '''query($login:String!,$cursor:String){user(login:$login){login name followers{totalCount} repositories(first:100,after:$cursor,privacy:PUBLIC,ownerAffiliations:OWNER,orderBy:{field:UPDATED_AT,direction:DESC}){totalCount pageInfo{hasNextPage endCursor} nodes{name isFork stargazerCount primaryLanguage{name color} url description}} contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount color weekday}}}}}}'''

def fetch():
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if not token:
        raise SystemExit('Set GITHUB_TOKEN or use --data with a captured GraphQL response.')
    cursor, result = None, None
    while True:
        body = json.dumps({'query': QUERY, 'variables': {'login': 'anilpdv', 'cursor': cursor}}).encode()
        req = urllib.request.Request('https://api.github.com/graphql', data=body, headers={
            'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', 'User-Agent': 'anilpdv-profile'})
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = json.load(response)
        if payload.get('errors'):
            raise RuntimeError('GitHub GraphQL request failed: ' + str(payload['errors']))
        user = payload['data']['user']
        if not user: raise RuntimeError('GitHub user was not returned')
        if result is None: result = user
        else: result['repositories']['nodes'].extend(user['repositories']['nodes'])
        page = user['repositories']['pageInfo']
        if not page['hasNextPage']: break
        cursor = page['endCursor']
    result['repositories']['pageInfo'] = {'hasNextPage': False, 'endCursor': cursor}
    return result

def esc(value): return html.escape(str(value), quote=True)
def text(x,y,value,size=16,color=INK,weight=400,mono=False,anchor='start'):
    family = 'ui-monospace, SFMono-Regular, Consolas, monospace' if mono else 'Segoe UI, Arial, sans-serif'
    return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{esc(value)}</text>'
def rect(x,y,w,h,fill=PANEL,stroke=BORDER,r=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'
def line(x1,y1,x2,y2,color=BORDER,width=1):
    return f'<path d="M{x1} {y1}H{x2}" stroke="{color}" stroke-width="{width}"/>' if y1==y2 else f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" stroke-width="{width}"/>'
def circle(x,y,r,color):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'
def svg(w,h,body,title,desc=''):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{esc(title)}</title><desc id="desc">{esc(desc or title)}</desc><defs><linearGradient id="accent" x1="0" x2="1"><stop stop-color="{CYAN}"/><stop offset=".55" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient><linearGradient id="shade"><stop stop-color="{BG}" stop-opacity=".97"/><stop offset=".49" stop-color="{BG}" stop-opacity=".83"/><stop offset=".8" stop-color="{BG}" stop-opacity="0"/></linearGradient><linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>{body}</svg>'''
def save(name,w,h,body,title,desc=''):
    (OUT / name).write_text(svg(w,h,body,title,desc))

SYMBOLS={
 'code':'M8 5 2 12l6 7m8-14 6 7-6 7m-3-16-2 18',
 'users':'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m20 0v-2a4 4 0 0 0-3-3.87M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8m7-7.87a4 4 0 0 1 0 7.75',
 'book':'M4 3h6a3 3 0 0 1 3 3v15a4 4 0 0 0-4-2H4V3m9 3a3 3 0 0 1 3-3h5v16h-4a4 4 0 0 0-4 2',
 'star':'m12 3 2.8 5.7 6.3.9-4.6 4.5 1.1 6.3L12 17.4l-5.6 3 1.1-6.3L3 9.6l6.2-.9L12 3',
 'git':'M6 3v12m0 0a3 3 0 1 0 0 6 3 3 0 0 0 0-6m0-9a3 3 0 1 0 0-6 3 3 0 0 0 0 6m0 9c0-5 12-1 12-8m0 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6',
 'layers':'m12 3 10 6-10 6L2 9l10-6m-10 11 10 6 10-6M2 19l10 6 10-6',
 'arrow':'M5 19 19 5M5 5h14v14',
 'mail':'M3 5h18v14H3V5m0 0 9 7 9-7',
 'globe':'M3 12h18M12 3c6 5 6 13 0 18-6-5-6-13 0-18m9 9a9 9 0 1 1-18 0 9 9 0 0 1 18 0',
 'linkedin':'M5 9v11m0-16v.1M10 20V9h4v2c4-4 7-1 7 3v6m-7 0v-6',
 'terminal':'m4 6 6 6-6 6m9 0h7'
}
def icon(name,x,y,size=24,color=CYAN):
    return f'<g transform="translate({x} {y}) scale({size/24})" fill="none" stroke="{color}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="{SYMBOLS[name]}"/></g>'
def pill(x,y,label,color=CYAN):
    w=len(label)*6.8+20
    return rect(x,y,w,24,'#111D2E','none',6)+text(x+10,y+16,label,11.5,color,500,True),w

def hero():
    art=base64.b64encode((OUT/'night-vista.jpg').read_bytes()).decode()
    for mobile in [False,True]:
        w,h=(320,414) if mobile else (900,360)
        b=f'<defs><clipPath id="frame"><rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="14"/></clipPath></defs><g clip-path="url(#frame)">'
        b+=rect(0,0,w,h,BG,'none',14)
        if mobile:
            b+=f'<image x="0" y="36" width="320" height="178" preserveAspectRatio="xMaxYMid slice" href="data:image/jpeg;base64,{art}"/>'
            b+='<rect x="0" y="168" width="320" height="50" fill="url(#fade)"/>'
        else:
            b+=f'<image x="0" y="44" width="900" height="316" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{art}"/>'
            b+='<rect x="0" y="44" width="900" height="316" fill="url(#shade)"/>'
        b+=rect(0,0,w,36 if mobile else 44,'#0A111D','none',0)
        b+=icon('book',16,10,17,VIOLET)+text(42,24 if mobile else 28,'anilpdv / README.md',12,MUTED,mono=True)
        if not mobile:b+=text(872,28,'Code  /  Build  /  Learn',12,MUTED,mono=True,anchor='end')
        if mobile:
            b+=text(22,240,"Hey there, I'm",14,VIOLET,mono=True)
            b+=text(20,286,'Anil Palli',43,'url(#accent)',700)
            b+=text(22,316,'Full-stack developer',16,INK,600)
            b+=text(22,339,'& product engineer',16,INK,600)
            b+=text(22,367,'6+ years building software.',13,MUTED,mono=True)
            b+=icon('terminal',22,384,15,CYAN)+text(46,397,'build. learn. repeat.',12,CYAN,mono=True)
        else:
            b+=text(38,93,"Hey there, I'm",15,VIOLET,mono=True)
            b+=text(35,154,'Anil Palli',62,'url(#accent)',700)
            b+=text(39,194,'Full-stack developer & product engineer',19,INK,600)
            b+=text(39,230,'From web interfaces to native apps,',17,'#BDC9E1')
            b+=text(39,255,'I build things I want to use.',17,'#BDC9E1')
            b+=circle(45,300,4,GREEN)+text(59,306,'6+ years building software',14,MUTED,mono=True)
            b+=rect(617,290,250,45,'#080E19CC','#465274',8)
            b+=icon('terminal',631,302,20,CYAN)+text(660,318,'build. learn. repeat.',13,VIOLET,mono=True)
        b+='</g>'+rect(.5,.5,w-1,h-1,'none',BORDER,14)
        save('hero-mobile.svg' if mobile else 'hero.svg',w,h,b,'Anil Palli — Full-stack developer & product engineer','Self-taught engineer with 6+ years of experience building web interfaces, native applications, and developer tools. An original illustrated midnight landscape.')

def metrics(user,today):
    repos=user['repositories']
    values=[('Followers',user['followers']['totalCount'],'People along the way','users',CYAN),('Public repos',repos['totalCount'],'Ideas turned into code','book',GREEN),('Repo stars',sum(r['stargazerCount'] for r in repos['nodes'] if not r['isFork']),'Public non-fork repos','star','#F9D275'),('Contributions',user['contributionsCollection']['contributionCalendar']['totalContributions'],'Over the past year','git',VIOLET)]
    for mobile in [False,True]:
        w,h=(320,210) if mobile else (900,118)
        cw,ch,gap=(155,90,10) if mobile else (213,92,16)
        b=''
        for i,(label,value,sub,symbol,color) in enumerate(values):
            x=(i%2)*(cw+gap) if mobile else i*(cw+gap);y=(i//2)*100 if mobile else 0
            b+=rect(x+.5,y+.5,cw-1,ch-1)
            if mobile:
                b+=icon(symbol,x+13,y+12,17,color)+text(x+38,y+26,label,12,MUTED)
                b+=text(x+13,y+64,f'{value:,}',28,INK,650)
                if i==3:b+=text(x+13,y+80,'past year',10,MUTED)
            else:
                b+=rect(x+15,24,40,40,'#142036','none',10)+icon(symbol,x+23,32,24,color)
                b+=text(x+69,27,label,12,MUTED,mono=True)+text(x+68,57,f'{value:,}',28,INK,650)+text(x+69,78,sub,10.5,MUTED)
        b+=text(w-2,h-4,'GitHub data · '+today,10,MUTED,mono=True,anchor='end')
        save('metrics-mobile.svg' if mobile else 'metrics.svg',w,h,b,'Live GitHub profile metrics', '; '.join(f'{a}: {v:,}' for a,v,*_ in values)+'. Updated '+today)

TECH=[('React','react','#61DAFB'),('TypeScript','typescript','#409FE7'),('Next.js','nextdotjs','#F0F5FF'),('Node.js','nodedotjs','#78C957'),('Go','go','#50CDE5'),('Rust','rust','#E9A26E'),('Elixir','elixir','#B799E3'),('Swift','swift','#FF8B67'),('Flutter','flutter','#5BC9F1'),('Postgres','postgresql','#83B7DC'),('Docker','docker','#53AEF7'),('Git','git','#F47A65')]
def logo(slug,x,y,size,color):
    import xml.etree.ElementTree as ET
    root=ET.parse(OUT/'icons'/(slug+'.svg')).getroot()
    paths=''.join('<path d="'+esc(p.attrib['d'])+'"/>' for p in root.iter() if p.tag.endswith('path'))
    return f'<g transform="translate({x} {y}) scale({size/24})" fill="{color}">{paths}</g>'
def stack(w,h):
    small=w<400
    b=rect(.5,.5,w-1,h-1)+icon('layers',22,22,21,VIOLET)+text(54,40,'Tech stack',21,INK,600)+text(23,64,'Tools I build with & explore.',13,MUTED)
    gap=9;tw=(w-46-gap*3)/4;th=76 if small else 77
    for i,(label,slug,color) in enumerate(TECH):
        x=23+(i%4)*(tw+gap);y=86+(i//4)*(th+10)
        b+=rect(x,y,tw,th,'#0A121F','#1D2B40',9)+logo(slug,x+(tw-28)/2,y+12,28,color)+text(x+tw/2,y+61,label,10.5,MUTED,anchor='middle')
    return b

def focus(w,h,user):
    small=w<400
    b=rect(.5,.5,w-1,h-1)+icon('code',22,23,21,CYAN)+text(54,40,'Building & exploring',20,INK,600)
    b+=circle(27,79,3,GREEN)+text(40,84,'YouTube subtitle tools',14,INK)
    b+=circle(27,107,3,CYAN)+text(40,112,'Native desktop & mobile apps',14,INK)
    b+=text(23,148,'Exploring Go, Rust & Elixir',12.5,VIOLET,mono=True)
    b+=line(23,172,w-23,172)
    cal=user['contributionsCollection']['contributionCalendar'];weeks=cal['weeks']
    b+=text(23,203,f'{cal["totalContributions"]:,} contributions',17,INK,600)+text(23,224,'A year of showing up.',12,MUTED)
    pitch=(w-46)/len(weeks);size=pitch-1.8 if small else pitch-2
    colors=['#18253A','#1B4852','#246C6C','#34A49C',CYAN]
    counts=[d['contributionCount'] for week in weeks for d in week['contributionDays'] if d['contributionCount']]
    peak=max(counts,default=1)
    for i,week in enumerate(weeks):
        for d in week['contributionDays']:
            count=d['contributionCount'];level=0 if not count else min(4,max(1,math.ceil(4*math.log1p(count)/math.log1p(peak))))
            b+=rect(23+i*pitch,243+d['weekday']*pitch,size,size,colors[level],'none',1.2)
    y=243+7*pitch+19
    start=weeks[0]['contributionDays'][0]['date'];end=weeks[-1]['contributionDays'][-1]['date']
    b+=text(23,y,start+' / '+end,9.5,MUTED,mono=True)
    return b

def dashboard(user):
    save('dashboard.svg',900,358,stack(442,358)+'<g transform="translate(458 0)">'+focus(442,358,user)+'</g>','Tech stack and development activity','React, TypeScript, Next.js, Node.js, Go, Rust, Elixir, Swift, Flutter, PostgreSQL, Docker, and Git. Building YouTube subtitle tools and native applications; exploring Go, Rust, and Elixir. Contribution calendar from GitHub.')
    save('dashboard-mobile.svg',320,724,stack(320,354)+'<g transform="translate(0 370)">'+focus(320,354,user)+'</g>','Tech stack and development activity')

PROJECTS=[
 ('translator','YouTube Translator','Synchronized bilingual subtitles.','Resume translations. Export SRT.','TypeScript / React / WXT',CYAN),
 ('libgen','LibGen Downloader','A native client for desktop & mobile.','Resilient search and downloads.','Go / Fyne',VIOLET),
 ('music','MusicApp','Music discovery, playlists, playback.','Built for iOS.','Swift / iOS',PINK),
 ('pipeline','ProjectK8','Recognize digits. Translate text.','Turn the result into speech.','React / Python / Docker',GREEN)]
def illustration(kind,x,y,w,color):
    b=rect(x,y,w,76,'#09111E','#1D2B40',8)
    if kind=='translator':
        b+=rect(x+12,y+12,67,51,'#182840','none',5)+f'<path d="M{x+37} {y+26}l18 11-18 11Z" fill="{color}"/>'
        b+=text(x+94,y+32,'Hello, world.',13,INK,mono=True)+text(x+94,y+54,'Hola, mundo.',13,color,mono=True)
        b+=line(x+12,y+68,x+w-12,y+68,'#203149',2)+line(x+12,y+68,x+w*.66,y+68,color,2)
    elif kind=='libgen':
        for i,bh in enumerate([40,48,34]):
            b+=rect(x+15+i*18,y+60-bh,13,bh,['#62568B','#5A7DA9','#7B659F'][i],'none',3)
        b+=text(x+87,y+28,'Search. Find. Read.',12,INK,mono=True)
        b+=rect(x+87,y+41,w-105,8,'#203149','none',4)+rect(x+87,y+41,(w-105)*.73,8,color,'none',4)
        b+=text(x+87,y+65,'Resumable downloads',10.5,MUTED,mono=True)
    elif kind=='music':
        for i in range(29):
            bh=9+36*abs(math.sin(i*.63)*math.cos(i*.19));px=x+15+i*(w-30)/29
            b+=rect(px,y+38-bh/2,3,bh,color,'none',1.5)
    else:
        bw=(w-56)/3
        for i,label in enumerate(['Recognize','Translate','Speak']):
            xx=x+10+i*(bw+18)
            b+=rect(xx,y+19,bw,38,'#122238','#29423D',6)+text(xx+bw/2,y+42,label,11,color,mono=True,anchor='middle')
            if i<2:b+=line(xx+bw+3,y+38,xx+bw+15,y+38,color)
    return b

def projects():
    for key,name,a,b,tech,color in PROJECTS:
        for small in [False,True]:
            w=320 if small else 442;h=246
            body=rect(.5,.5,w-1,h-1)+f'<path d="M18 1H{w-18}" stroke="{color}" stroke-width="2" opacity=".7"/>'
            body+=text(22,38,name,20,INK,650)+icon('arrow',w-39,23,16,color)
            # Short, predictable copy remains readable in mobile variants.
            if small and key=='libgen':a1='A native desktop & mobile client.'
            else:a1=a
            body+=text(22,70,a1,14,MUTED)+text(22,91,b,14,MUTED)
            body+=illustration(key,22,111,w-44,color)
            body+=text(22,220,tech,11.5,color,mono=True)+text(w-22,220,'View code',11,MUTED,anchor='end')
            save('project-'+key+('-mobile' if small else '')+'.svg',w,h,body,name,a1+' '+b+' Built with '+tech+'.')

def footer():
    for small in [False,True]:
        w,h=(320,100) if small else (900,80)
        b=rect(.5,.5,w-1,h-1,PANEL,'url(#accent)',12)
        b+=text(w/2,34,'Build useful things. Keep learning.',15 if small else 19,VIOLET,600,anchor='middle')
        if small:
            b+=text(w/2,61,'Open to conversations about web,',12,MUTED,anchor='middle')+text(w/2,80,'native apps & developer tools.',12,MUTED,anchor='middle')
        else:b+=text(w/2,59,'Open to conversations about web, native apps & developer tools.',13,MUTED,mono=True,anchor='middle')
        save('footer-mobile.svg' if small else 'footer.svg',w,h,b,'Build useful things. Keep learning.')
    for slug,label,symbol,color in [('website','Website','globe',CYAN),('linkedin','LinkedIn','linkedin',VIOLET),('email','Email me','mail',PINK),('repositories','All repos','code',GREEN)]:
        save('link-'+slug+'.svg',142,42,rect(.5,.5,141,41,PANEL,BORDER,8)+icon(symbol,16,12,18,color)+text(44,27,label,13,INK,500),'Visit '+label)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path);args=parser.parse_args()
    user=json.loads(args.data.read_text())['data']['user'] if args.data else fetch()
    if user['repositories']['pageInfo']['hasNextPage']:raise ValueError('Repository data is incomplete; paginate before rendering.')
    today=dt.datetime.now(dt.timezone.utc).date().isoformat()
    OUT.mkdir(parents=True,exist_ok=True)
    hero();metrics(user,today);dashboard(user);projects();footer()
    public={'updated':today,'followers':user['followers']['totalCount'],'public_repositories':user['repositories']['totalCount'],'stars':sum(r['stargazerCount'] for r in user['repositories']['nodes'] if not r['isFork']),'contributions_last_year':user['contributionsCollection']['contributionCalendar']['totalContributions']}
    (OUT/'data.json').write_text(json.dumps(public,indent=2)+'\n')
    print('Rendered profile:',json.dumps(public))
if __name__=='__main__':main()
