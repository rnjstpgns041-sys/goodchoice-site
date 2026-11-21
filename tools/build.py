# -*- coding: utf-8 -*-
"""굿초이스 집수리 정적 사이트 생성기.

python3 tools/build.py  (저장소 루트에서 실행)
- 블로그 원본: /mnt/project-files/homepage/photos/blog/<id>/{NN.jpg,text.txt}, manifest.json
- 출력: index.html, service/, cases/, area/, process/, contact/, 404.html, robots.txt, sitemap.xml, assets/, photos/c/
"""
import json, os, re, html, shutil, datetime, urllib.parse
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOGDIR = '/mnt/project-files/homepage/photos/blog'
SITE = 'https://las8015.com'
TEL = '010-5809-9275'
TELN = '01058099275'
TALK = 'https://talk.naver.com/w5i8w9'
BLOG = 'https://blog.naver.com/las8015'

# ---- 사장님 계정이 필요한 값 (받으면 여기에 넣고 다시 빌드) ----
NAVER_SITE_VERIFICATION = ''   # 네이버 서치어드바이저 HTML 태그의 content 값
GOOGLE_SITE_VERIFICATION = ''  # 구글 서치콘솔 (선택)
NAVER_ANALYTICS_ID = ''        # 네이버 애널리틱스 사이트 ID (예: 'a1b2c3d4e5f6')
GA4_ID = ''                    # 구글 애널리틱스 측정 ID (예: 'G-XXXXXXX')

PHOTO_GUIDE = '전체 현장 사진 1장과 문제 부위 사진 1장을 보내주시면 확인 후 상담해 드립니다.'
PHOTO_NOTE = '단, 사진만으로 견적이 어려운 작업은 현장 확인이 필요할 수 있습니다.'
SMS_BODY = '[굿초이스 견적 문의]\n작업 종류: \n지역(동까지): \n※ 전체 사진 1장 + 문제 부위 사진 1장 첨부'
SMS_HREF = 'sms:%s?body=%s' % (TELN, urllib.parse.quote(SMS_BODY))

# 블로그 하단에 사장님이 직접 적어둔 출장 가능 지역
AREA_LIST = [
    ('서울', ['강남구', '서초구', '송파구', '강동구', '광진구', '성동구', '동대문구', '중랑구', '성북구', '강북구', '노원구', '도봉구']),
    ('경기', ['용인시', '수원시', '성남시', '고양시', '김포시', '파주시', '남양주시', '하남시']),
    ('그 외', ['인천 미추홀구', '인천 연수구', '세종시', '천안시', '아산시']),
]

E = lambda s: html.escape(str(s), quote=True)
legacy = json.load(open(os.path.join(ROOT, 'tools/legacy.json')))
LSVC = {s['id']: s for s in legacy['SVC']}
LCASE = {c['id']: c for c in legacy['CASES']}
LEGACY_HTML = open(os.path.join(ROOT, 'tools/legacy_index.html')).read()

# ------------------------------------------------------------------ services
SERVICES = [
    dict(slug='dishwasher', old='dish', icon='dish', name='빌트인 식기세척기 설치 및 철거', short='식기세척기',
         title='빌트인 식기세척기 설치·철거 | 하부장 철거, 급수·배수 연결',
         desc='빌트인 식기세척기 신규 설치와 철거, 싱크대 하부장 철거로 공간 확보, 급수·배수 연결, 이사 시 이전 설치와 원상복구까지 굿초이스 집수리가 직접 시공합니다.',
         items=['식기세척기 신규 설치', '기존 식기세척기 철거', '싱크대 하부장 철거 및 공간 확보', '급수 및 배수 연결', '이전 설치 및 원상복구']),
    dict(slug='dryer', old='laundry', icon='dryer', name='건조기 직렬 설치', short='건조기 직렬',
         title='건조기 직렬 설치 | 세탁기 위 건조기, 맞춤 선반 시공',
         desc='세탁기·건조기 직렬 설치, 직렬 키트가 맞지 않을 때 맞춤형 선반 설치, 건조기 이전 설치와 좁은 세탁실 구조 변경까지 현장에 맞춰 시공합니다.',
         items=['세탁기·건조기 직렬 설치', '맞춤형 선반 설치', '건조기 이전 설치', '설치 공간 구조 변경']),
    dict(slug='shower-booth', old='bath', icon='shower', name='샤워부스 철거 및 욕실 복원', short='샤워부스',
         title='샤워부스 철거·물막이 설치 | 욕실 벽면·바닥 복원',
         desc='샤워부스 철거와 유리·프레임 제거, 물이 넘칠 때 물막이(쫄대) 설치, 철거 후 남은 욕실 벽면과 바닥 흔적 복원까지 굿초이스 집수리 시공사례로 확인하세요.',
         items=['샤워부스 철거', '유리 및 프레임 제거', '물막이 설치', '욕실 벽면 및 바닥 복원']),
    dict(slug='water-purifier-restore', old='restore', icon='restore', name='정수기 철거 및 싱크대 상판 복원', short='정수기·상판 복원',
         title='정수기 철거·싱크대 상판 타공 복원 | 이사 전 원상복구',
         desc='이사 전 정수기 철거, 싱크대 상판 타공 구멍 복원, 인조대리석 상판 보수, 수전·배관 정리 등 퇴거 전 원상복구 작업을 실제 사례와 함께 안내합니다.',
         items=['정수기 철거', '싱크대 타공 구멍 복원', '인조대리석 상판 보수', '수전 및 배관 정리']),
    dict(slug='door-furniture', old='furniture', icon='door', name='문 방향 변경 및 가구 리폼', short='문·가구 리폼',
         title='문 방향 변경·가구 리폼 | 방문 개폐 방향, 붙박이장 문짝 수리',
         desc='방문 개폐 방향 변경, 문짝·경첩 교체, 붙박이장 문짝 수리, 장롱·하부장 문짝 제작과 가구 리폼까지 현장에서 직접 가공해 맞춰 드립니다.',
         items=['방문 개폐 방향 변경', '문짝 및 경첩 교체', '붙박이장 문짝 수리', '가구 리폼 및 부속 교체']),
    dict(slug='home-repair', old='kitchen', icon='sink', name='주방·욕실 생활 수리', short='생활 수리',
         title='주방·욕실 생활 수리 | 세면대 배수, 디스펜서, 안전손잡이',
         desc='세면대 배수 팝업·트랩 교체, 싱크대 세제 디스펜서 교체, 안전손잡이 설치, 콘센트 교체, 빌트인 냉장고 철거처럼 생활 속 작은 수리를 굿초이스 집수리가 해결합니다.',
         items=['세면대 배수 팝업·트랩 교체', '싱크대 세제 디스펜서 교체', '주방·욕실 안전손잡이 설치', '파손 콘센트 교체', '빌트인 냉장고 철거', '그 밖의 생활 수리']),
]
SBY = {s['slug']: s for s in SERVICES}
for s in SERVICES:
    L = LSVC[s['old']]
    s['lead'] = L['lead']; s['who'] = L['who']; s['card'] = L['short']
SERVICES[5]['lead'] = '세면대 물이 안 내려갈 때, 세제 디스펜서 펌프가 고장 났을 때, 어르신을 위한 손잡이가 필요할 때처럼 생활하며 생기는 작은 불편도 원인을 확인하고 필요한 부분만 고칩니다.'
SERVICES[5]['who'] = ['세면대 물이 잘 안 내려가거나 팝업이 작동하지 않을 때', '싱크대 세제 디스펜서 펌프가 고장 났을 때', '거동이 불편한 가족을 위해 손잡이가 필요할 때']
SERVICES[5]['card'] = '세면대 배수, 디스펜서, 안전손잡이처럼 작지만 불편한 것들.'
SERVICES[3]['card'] = '정수기 철거 후 남은 상판 구멍까지, 퇴거 전 원상복구.'
OLD2SLUG = {s['old']: s['slug'] for s in SERVICES}


def svc_for(p):
    t, c = p['title'], p['category']
    if '정수기' in t: return 'water-purifier-restore'
    if c == '식기세척기': return 'dishwasher'
    if c == '세탁기·건조기': return 'dryer'
    if c == '샤워부스·욕실': return 'home-repair' if '세면대' in t else 'shower-booth'
    if c == '원상복구': return 'water-purifier-restore'
    if c in ('문 방향 변경', '가구·수납 리폼'): return 'door-furniture'
    return 'home-repair'

# ------------------------------------------------------------------ text parse
HEAD_RE = re.compile(r'^(?:【(.+?)】|◆\s*(.+))$')


def classify(h):
    if h is None: return 'intro'
    if '자주 묻는' in h: return 'faq'
    if '추천' in h or '문의해 주세요' in h or '미리 철거' in h: return 'rec'
    if '느낀' in h: return 'feel'
    if re.search(r'결과|변화', h): return 'result'
    if re.search(r'전 상황|전 상태|현장 점검|현장 확인|전 확인|시공 전|설치 전|철거 전|교체 전', h): return 'pre'
    if re.search(r'작동 확인|물을 뿌려|최종 점검|점검 및|마감|마무리|테스트|후 확인|완료', h): return 'check'
    return 'step'


def parse_text(pid, title):
    lines = open(os.path.join(BLOGDIR, pid, 'text.txt'), encoding='utf-8').read().split('\n')
    hdr = {}; i = 0
    while i < len(lines) and lines[i].strip():
        k, _, v = lines[i].partition(':'); hdr[k.strip()] = v.strip(); i += 1
    body = lines[i + 1:]
    new_fmt = any(re.match(r'^【.+】$', l.strip()) for l in body)
    secs = [dict(h=None, kind='intro', items=[])]
    para = []

    def flush():
        if para:
            secs[-1]['items'].append(('p', ' '.join(para))); para.clear()
    skip = False
    for ln in body:
        s = ln.strip()
        if s.startswith('견적 문의 방법') or s.startswith('함께보면 좋은'): break
        if skip: skip = False; continue
        if '방문한 지역' in s: flush(); skip = True; continue
        if '『굿초이스' in s or s.startswith('깔끔하게 해결해 드리겠습니다'): continue
        if len(s) >= 6 and s in title: continue
        if not s: flush(); continue
        m = re.match(r'^\[사진 (\d+)\]$', s)
        if m: flush(); secs[-1]['items'].append(('img', m.group(1))); continue
        if new_fmt and s.startswith('◆'):
            flush(); secs[-1]['items'].append(('li', s.lstrip('◆ ').strip())); continue
        m = HEAD_RE.match(s)
        if m:
            flush(); h = (m.group(1) or m.group(2)).strip()
            secs.append(dict(h=h, kind=classify(h), items=[])); continue
        if re.match(r'^[–\-•·]\s+', s):
            flush(); secs[-1]['items'].append(('li', re.sub(r'^[–\-•·]\s+', '', s))); continue
        para.append(s)
    flush()
    # 점검/결과 뒤에 나오는 일반 단계는 관리 팁이므로 작업 단계에서 뺀다
    seen = False
    for sc in secs:
        if sc['kind'] in ('check', 'result'): seen = True
        elif seen and sc['kind'] == 'step': sc['kind'] = 'tip'
    # 홍보 문구 제거
    for sc in secs:
        sc['items'] = [x for x in sc['items'] if not (x[0] == 'p' and re.search(r'해결해\s?드리고 있습니다|전문가 맡겨주세요|굿초이스', x[1]))]
    return hdr, secs


def cond(paras, n=200):
    """문단을 이어 붙여 n자 안팎에서 문장 끝(다.)으로 자른다."""
    t = ''
    for p in paras:
        if len(p) < 12: continue  # 사진 밑 짧은 캡션 제외
        t = (t + ' ' + p).strip()
        if len(t) >= n: break
    ends = [m.end() for m in re.finditer(r'(다|요)\.', t) if m.end() <= n + 40]
    if ends: return t[:ends[-1]]
    if len(t) <= n + 40 and re.search(r'[.?!]$', t): return t
    return ''


def region_of(visited):
    v = visited or ''
    m = re.match(r'서울(?:특별)?시?\s+(\S+구)', v)
    if m: return ('서울', m.group(1))
    m = re.match(r'경기도\s+(\S+?)시', v)
    if m:
        city = m.group(1)
        return ('경기 광주' if city == '광주' else city, None)
    return (v.split(' ')[0] if v else '', None)


# 블로그 제목 맨 앞 지역명이 실제 방문 지역과 다른 경우가 있어(검색용 제목), 실제 지역으로 바로잡는다.
PLACE_OK = {'분당': ['분당구'], '판교': ['분당구', '판교'], '위례': ['위례', '위레'], '광교': ['광교', '영통구'], '동탄': ['동탄']}
PLACE_WORDS = ['강남구', '강남', '송파', '강동', '중랑구', '중랑', '노원', '광진', '서초', '분당', '판교', '위례', '광교', '동탄',
               '과천', '광명', '용인', '수원', '성남', '하남', '안양', '화성', '경기 광주', '광주']


def place_label(visited):
    v = visited or ''
    m = re.match(r'서울(?:특별)?시?\s+(\S+?)구', v)
    if m: return m.group(1)
    m = re.match(r'경기도\s+(\S+?)시', v)
    if m:
        city = '경기 광주' if m.group(1) == '광주' else m.group(1)
        return city + (' 위례' if ('위례' in v or '위레' in v) else '')
    return ''


def fix_place(title, visited):
    v = visited or ''
    for w in PLACE_WORDS:
        if not title.startswith(w + ' '): continue
        oks = PLACE_OK.get(w, [w.replace('구', '') if w.endswith('구') else w])
        if w == '경기 광주': oks = ['광주시']
        if any(o in v for o in oks): return title
        lab = place_label(v)
        return (lab + title[len(w):]) if lab else title[len(w) + 1:]
    return title


REGION_PAGES = [  # (key, slug, 표시명)
    ('서울', 'seoul', '서울'), ('성남', 'seongnam', '성남'), ('하남', 'hanam', '하남'),
    ('용인', 'yongin', '용인'), ('수원', 'suwon', '수원'), ('경기 광주', 'gwangju', '경기 광주'),
]
RSLUG = {k: s for k, s, _ in REGION_PAGES}

# ------------------------------------------------------------------ images
def save_img(src, dst, maxw, square=False, q=78):
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src): return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im = Image.open(src); im = ImageOps.exif_transpose(im).convert('RGB')
    if square:
        w, h = im.size; s = min(w, h)
        im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    im.save(dst, 'JPEG', quality=q, optimize=True, progressive=True)


manifest = json.load(open(os.path.join(BLOGDIR, 'manifest.json')))
CASES = []
for p in manifest['posts']:
    pid = p['id']
    if p['category'].startswith('정보글'): continue
    if not os.path.exists(os.path.join(BLOGDIR, pid, 'text.txt')): continue
    hdr, secs = parse_text(pid, p['title'])
    visited = hdr.get('방문 지역') or p.get('visited') or ''
    reg, gu = region_of(visited)
    ptype = {ph['file'][:2]: ph for ph in p['photos']}
    valid = lambda n: n in ptype and ptype[n]['type'] == 'photo' and os.path.exists(os.path.join(BLOGDIR, pid, n + '.jpg'))
    # 사진 분류 (글 위치 기준)
    before, during, after = [], [], []
    for s in secs:
        imgs = [x[1] for x in s['items'] if x[0] == 'img' and valid(x[1])]
        s['imgs'] = imgs
        k = s['kind']
        (before if k in ('intro', 'pre') else during if k == 'step' else after).extend(imgs)
    if not before: before = [n for n, ph in ptype.items() if ph.get('stage') == 'before' and valid(n)]
    if not after: after = [n for n, ph in ptype.items() if ph.get('stage') == 'after' and valid(n)]
    allimg = [n for n in sorted(ptype) if valid(n)]
    # 이미지 저장
    for n in allimg:
        save_img(os.path.join(BLOGDIR, pid, n + '.jpg'), os.path.join(ROOT, 'photos/c', pid, n + '.jpg'), 960)
        save_img(os.path.join(BLOGDIR, pid, n + '.jpg'), os.path.join(ROOT, 'photos/c', pid, n + '_s.jpg'), 420, q=74)
    bsrc = os.path.join(ROOT, 'photos', pid + '_before.jpg'); asrc = os.path.join(ROOT, 'photos', pid + '_after.jpg')
    if not (os.path.exists(bsrc) and os.path.exists(asrc)):
        b0 = (before or allimg)[0]; a0 = (after or allimg)[-1]
        bsrc = os.path.join(BLOGDIR, pid, b0 + '.jpg'); asrc = os.path.join(BLOGDIR, pid, a0 + '.jpg')
    save_img(bsrc, os.path.join(ROOT, 'photos/c', pid, 'before.jpg'), 720, square=True)
    save_img(asrc, os.path.join(ROOT, 'photos/c', pid, 'after.jpg'), 720, square=True)
    save_img(asrc, os.path.join(ROOT, 'photos/c', pid, 'after_s.jpg'), 320, square=True, q=70)
    # 내용 요약
    paras = lambda kinds: [x[1] for s in secs if s['kind'] in kinds for x in s['items'] if x[0] == 'p']
    problem = cond(paras(('intro',)) + paras(('pre',)), 260)
    lis = lambda kinds: [x[1] for s in secs if s['kind'] in kinds for x in s['items'] if x[0] == 'li']
    problem_li = lis(('pre',))[:5]
    result_li = lis(('result',))[:5]
    steps = []
    for s in secs:
        if s['kind'] != 'step': continue
        ps = [x[1] for x in s['items'] if x[0] == 'p']; lis = [x[1] for x in s['items'] if x[0] == 'li']
        steps.append(dict(h=s['h'], t=cond(ps, 170) if ps else '', li=lis, imgs=s['imgs'][:2]))
    checks = []
    for s in secs:
        if s['kind'] != 'check': continue
        ps = [x[1] for x in s['items'] if x[0] == 'p']; lis = [x[1] for x in s['items'] if x[0] == 'li']
        checks.append(dict(h=s['h'], t=cond(ps, 170) if ps else '', li=lis))
    result = cond(paras(('result',)), 220) or cond(paras(('feel',)), 160)
    rec = []
    for s in secs:
        if s['kind'] == 'rec':
            rec += [x[1] for x in s['items'] if x[0] == 'li']
            if not rec: rec = [cond([x[1] for x in s['items'] if x[0] == 'p'], 200)]
    faq = []
    for s in secs:
        if s['kind'] != 'faq': continue
        cur = None
        for x in s['items']:
            if x[0] != 'p': continue
            t = x[1]
            if re.match(r'^Q\d*[\.\s]', t):
                cur = [re.sub(r'^Q\d*\.?\s*', '', t), []]; faq.append(cur)
            elif cur is not None:
                cur[1].append(re.sub(r'^A\.?\s+', '', t))
        faq = [(q, cond(a, 220)) for q, a in faq if a]
    L = LCASE.get(pid)
    svc = svc_for(p)
    p = dict(p, title=fix_place(p['title'], visited))
    if L: L = dict(L, title=fix_place(L['title'], visited))
    CASES.append(dict(
        id=pid, title=p['title'], date=hdr.get('날짜') or p['date'], visited=visited, reg=reg, gu=gu, svc=svc,
        blog=hdr.get('원문') or p['url'], problem=problem, problem_li=problem_li, result_li=result_li, steps=steps, checks=checks, result=result, rec=rec[:6], faq=faq,
        before=before[:6], during=during[:9], after=after[:6], allimg=allimg,
        sum=(L['sum'] if L else (cond([problem], 80) or p['title'])), short=(L['title'] if L else p['title']),
    ))
CASES.sort(key=lambda c: c['id'], reverse=True)
CBY = {c['id']: c for c in CASES}
print('cases', len(CASES))


def place(c):
    """사례 카드/제목용 지역 표기"""
    return (c['gu'] and '서울 ' + c['gu']) or c['reg']


def seo_title(c):
    r = c['reg'] if c['reg'] != '서울' else (c['gu'] or '서울').replace('구', '') if c['gu'] and len(c['gu']) > 2 else c['reg']
    t = c['title']
    first = t.split(' ')[0]
    if r and r not in t and first not in ('위례', '광교', '동탄', '판교', '분당'):
        t = r + ' ' + t
    return t

# ------------------------------------------------------------------ html parts
SPRITE = LEGACY_HTML[LEGACY_HTML.index('<svg width="0"'):LEGACY_HTML.index('</defs></svg>') + len('</defs></svg>')]
SPRITE = SPRITE.replace('</defs>', '<symbol id="ok" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7"/></symbol></defs>')
ARR = '<svg><use href="#arrow"/></svg>'
CALL = '<a class="btn btn-accent" href="tel:%s" data-track="call"><svg><use href="#phone"/></svg>전화하기</a>' % TELN
SMS = '<a class="btn btn-line" href="%s" data-sms data-track="sms"><svg><use href="#chat"/></svg>문자로 견적 받기</a>' % E(SMS_HREF)
SMS_G = '<a class="btn btn-ghost" href="%s" data-sms data-track="sms"><svg><use href="#chat"/></svg>문자로 견적 받기</a>' % E(SMS_HREF)
NAV = [('/service/', '서비스', 'service'), ('/cases/', '시공사례', 'cases'), ('/process/', '진행 방법', 'process'), ('/area/', '출장 지역', 'area'), ('/contact/', '견적 문의', 'contact')]


def head(title, desc, path, img=None, extra=''):
    url = SITE + path
    img = SITE + '/' + (img or 'photos/c/224425527882/after.jpg')
    v = ''
    if NAVER_SITE_VERIFICATION: v += '<meta name="naver-site-verification" content="%s">\n' % E(NAVER_SITE_VERIFICATION)
    if GOOGLE_SITE_VERIFICATION: v += '<meta name="google-site-verification" content="%s">\n' % E(GOOGLE_SITE_VERIFICATION)
    an = ''
    if GA4_ID:
        an += '<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag("js",new Date());gtag("config","%s");</script>\n' % (GA4_ID, GA4_ID)
    if NAVER_ANALYTICS_ID:
        an += '<script src="//wcs.naver.net/wcslog.js"></script><script>if(!wcs_add)var wcs_add={};wcs_add["wa"]="%s";if(window.wcs){wcs_do();}</script>\n' % NAVER_ANALYTICS_ID
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="굿초이스 집수리">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:locale" content="ko_KR">
<meta name="theme-color" content="#0B0B0B">
<meta name="format-detection" content="telephone=no">
{v}<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="/assets/site.css?v={VER}">
{extra}{an}</head>
<body>
{SPRITE}
'''


def header(active):
    menu = ''.join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if k == active else '', t) for h, t, k in NAV)
    dnav = '<a href="/">홈 <small>HOME</small></a>' + ''.join('<a href="%s">%s <small>%s</small></a>' % (h, t, k.upper()) for h, t, k in NAV)
    return f'''<header>
  <div class="wrap nav">
    <a class="logo" href="/"><span class="mark"><svg><use href="#check"/></svg></span><span><span class="tagline">집수리 &amp; 리폼 전문</span>굿초이스 집수리</span></a>
    <nav class="menu" aria-label="주요 메뉴">{menu}</nav>
    <a class="hcall" href="tel:{TELN}" data-track="call"><svg><use href="#phone"/></svg>전화하기</a>
    <a class="hcall hsms" href="{E(SMS_HREF)}" data-sms data-track="sms"><svg><use href="#chat"/></svg>문자하기</a>
    <button class="burger" type="button" id="burger" aria-label="메뉴 열기"><svg><use href="#menu"/></svg></button>
  </div>
</header>
<div class="drawer" id="drawer" hidden>
  <div class="top"><span class="logo"><span class="mark"><svg><use href="#check"/></svg></span>굿초이스 집수리</span><button class="burger" type="button" id="closer" aria-label="메뉴 닫기" style="margin:0"><svg><use href="#close"/></svg></button></div>
  <nav aria-label="모바일 메뉴">{dnav}</nav>
  <div style="margin-top:auto;display:grid;grid-template-columns:1fr 1fr;gap:10px"><a class="btn btn-accent" href="tel:{TELN}" data-track="call"><svg><use href="#phone"/></svg>전화하기</a><a class="btn btn-ghost" href="{E(SMS_HREF)}" data-sms data-track="sms"><svg><use href="#chat"/></svg>문자하기</a></div>
</div>
<main>
'''


def footer():
    svc = ''.join('<a href="/service/%s/">%s</a>' % (s['slug'], E(s['name'])) for s in SERVICES)
    reg = ''.join('<a href="/area/%s/">%s</a>' % (sl, E(nm)) for k, sl, nm in REGION_PAGES)
    return f'''</main>
<footer>
  <div class="wrap fgrid">
    <div>
      <a class="logo" href="/"><span class="mark"><svg><use href="#check"/></svg></span>굿초이스 집수리</a>
      <p>집수리 &amp; 리폼 전문 · 설치부터 철거·복원까지<br>전화·문자 <a class="ftel" href="tel:{TELN}" data-track="call">{TEL}</a> · <a href="{TALK}" target="_blank" rel="noopener">네이버 톡톡</a><br>서울 · 경기 · 인천 출장 시공<br>© 2026 굿초이스 집수리</p>
    </div>
    <div><h4>서비스</h4><nav>{svc}</nav></div>
    <div><h4>안내</h4><nav><a href="/cases/">시공사례</a><a href="/process/">진행 방법</a><a href="/area/">출장 지역</a><a href="/contact/">견적 문의</a><a href="{BLOG}" target="_blank" rel="noopener">네이버 블로그</a></nav><h4 style="margin-top:18px">지역</h4><nav>{reg}</nav></div>
  </div>
</footer>
<nav class="bar" aria-label="빠른 상담">
  <a class="btn btn-accent" href="tel:{TELN}" data-track="call"><svg><use href="#phone"/></svg>전화 상담</a>
  <a class="btn btn-ghost" href="{E(SMS_HREF)}" data-sms data-track="sms"><svg><use href="#chat"/></svg>문자 견적</a>
</nav>
<script src="/assets/site.js?v={VER}" defer></script>
</body>
</html>
'''


def crumbs(items):
    """items: [(name, path or None)]"""
    h = '<div class="crumb"><a href="/">홈</a>' + ''.join('<span>/</span>' + ('<a href="%s">%s</a>' % (p, E(n)) if p else '<span>%s</span>' % E(n)) for n, p in items) + '</div>'
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + "/"}]}
    for i, (n, p) in enumerate(items):
        e = {"@type": "ListItem", "position": i + 2, "name": n}
        if p: e["item"] = SITE + p
        ld["itemListElement"].append(e)
    return h, '<script type="application/ld+json">%s</script>\n' % json.dumps(ld, ensure_ascii=False)


def phero(img, crumb, h1, lead, extra=''):
    return f'<section class="phero img" style="background-image:url(/{img})"><div class="wrap">{crumb}<h1>{h1}</h1><p class="lead">{lead}</p>{extra}</div></section>\n'


def svc_card(s):
    img = s.get('img') or ''
    return f'<a class="scard" href="/service/{s["slug"]}/"><div class="ph"><img src="/{img}" alt="{E(s["name"])} 시공 사진" width="720" height="720" loading="lazy"><span class="ic"><svg><use href="#{s["icon"]}"/></svg></span></div><div class="bd"><h3>{E(s["name"])}</h3><p>{E(s["card"])}</p><span class="go">자세히 보기 {ARR}</span></div></a>'


def case_card(c):
    s = SBY[c['svc']]
    return (f'<a class="ccard" href="/cases/{c["id"]}/"><div class="pair"><figure><img src="/photos/c/{c["id"]}/before.jpg" alt="{E(c["title"])} 작업 전" width="720" height="720" loading="lazy"><figcaption>전</figcaption></figure>'
            f'<figure><img src="/photos/c/{c["id"]}/after.jpg" alt="{E(c["title"])} 작업 후" width="720" height="720" loading="lazy"><figcaption class="af">후</figcaption></figure></div>'
            f'<div class="bd"><span class="cat">{E(place(c))} · {E(s["short"])}</span><h3>{E(c["short"])}</h3><p>{E(c["sum"])}</p><span class="go">사례 자세히 보기 {ARR}</span></div></a>')


def compare(c):
    return (f'<div class="compare"><img src="/photos/c/{c["id"]}/before.jpg" alt="{E(c["title"])} 작업 전" width="720" height="720" loading="lazy">'
            f'<img class="after" src="/photos/c/{c["id"]}/after.jpg" alt="{E(c["title"])} 작업 후" width="720" height="720" loading="lazy"><span class="tag b">작업 전</span><span class="tag a">작업 후</span></div>')


def gallery(c, nums, label):
    if not nums: return ''
    figs = ''.join(f'<figure><a class="gbtn" href="/photos/c/{c["id"]}/{n}.jpg" data-lb><img src="/photos/c/{c["id"]}/{n}_s.jpg" alt="{E(c["short"])} {label} 사진 {i + 1}" width="420" height="420" loading="lazy"></a></figure>' for i, n in enumerate(nums))
    return f'<div class="gal">{figs}</div>'


def cta_band(h='고칠 곳 사진, 지금 찍어 보내주세요', p=None):
    p = p or PHOTO_GUIDE + ' ' + PHOTO_NOTE
    return f'<div class="band on-blue"><div><h2>{h}</h2><p>{E(p)}</p></div><div class="ctas">{CALL}{SMS_G}</div></div>'


def aside(title, extra=''):
    return (f'<aside class="aside"><h3>{E(title)}</h3><p>{E(PHOTO_GUIDE)}</p><p class="note">{E(PHOTO_NOTE)}</p>'
            f'<dl><dt>전화·문자</dt><dd><a href="tel:{TELN}" data-track="call">{TEL}</a></dd><dt>출장</dt><dd>서울·경기·인천</dd></dl>{CALL}{SMS}{extra}</aside>')


def write(path, content):
    fp = os.path.join(ROOT, path.lstrip('/'), 'index.html') if path.endswith('/') else os.path.join(ROOT, path.lstrip('/'))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, 'w', encoding='utf-8').write(content)
    if path.endswith('/') or path.endswith('.html'): URLS.append(path if path != '/index.html' else '/')


URLS = []
VER = datetime.datetime.now().strftime('%Y%m%d%H%M')

# 서비스 대표 이미지
for s in SERVICES:
    cs = [c for c in CASES if c['svc'] == s['slug']]
    pick = {'dishwasher': '224425527882', 'dryer': '224365853425', 'shower-booth': '224457415114', 'water-purifier-restore': '224463095133', 'door-furniture': '224369548827', 'home-repair': '224325847991'}[s['slug']]
    s['img'] = 'photos/c/%s/after.jpg' % (pick if pick in CBY else cs[0]['id'])
    s['cases'] = cs

N = len(CASES)

# ================================================================== pages
# ---------- service list
crumb, ld = crumbs([('서비스', None)])
body = phero('photos/c/224425527882/after.jpg', crumb, '굿초이스 집수리 서비스', '빌트인 식기세척기, 건조기 직렬, 샤워부스 철거, 정수기 철거·상판 복원, 문 방향 변경과 가구 리폼까지. 분야별로 하는 일과 실제 시공사례를 정리했습니다.')
body += '<section><div class="wrap"><div class="services" style="margin-top:0">' + ''.join(svc_card(s) for s in SERVICES) + '</div><div style="margin-top:56px">' + cta_band('목록에 없는 작업도 문의해 주세요') + '</div></div></section>'
write('/service/', head('서비스 안내 | 식기세척기·건조기·샤워부스·원상복구 - 굿초이스 집수리', '굿초이스 집수리 서비스: 빌트인 식기세척기 설치·철거, 건조기 직렬 설치, 샤워부스 철거와 욕실 복원, 정수기 철거와 싱크대 상판 복원, 문 방향 변경과 가구 리폼, 주방·욕실 생활 수리.', '/service/', extra=ld) + header('service') + body + footer())

# ---------- service detail
for s in SERVICES:
    cs = s['cases']
    crumb, ld = crumbs([('서비스', '/service/'), (s['name'], None)])
    tabs = '<nav class="tabs" aria-label="서비스 분야">' + ''.join('<a href="/service/%s/"%s>%s</a>' % (x['slug'], ' aria-current="page"' if x is s else '', E(x['short'])) for x in SERVICES) + '</nav>'
    body = phero(s['img'], crumb, E(s['name']), E(s['lead']), tabs)
    items = ''.join('<div><b>%s</b></div>' % E(i) for i in s['items'])
    who = ''.join('<li>%s</li>' % E(w) for w in s['who'])
    # 작업 과정 예시: 대표 사례의 단계
    ex = next((c for c in cs if len(c['steps']) >= 3), cs[0] if cs else None)
    steps = ''
    if ex:
        steps = '<div class="block"><h2>작업 과정 예시</h2><p class="muted">%s · %s 현장</p><ol class="story">' % (E(ex['short']), E(place(ex)))
        for k, st in enumerate(ex['steps'][:5]):
            ph = ''.join(f'<img src="/photos/c/{ex["id"]}/{n}_s.jpg" alt="{E(st["h"])}" width="420" height="420" loading="lazy">' for n in st['imgs'][:2])
            li = ''.join('<li>%s</li>' % E(x) for x in st['li'][:4])
            steps += f'<li><h4>STEP {k + 1} · {E(st["h"])}</h4>' + (f'<p>{E(st["t"])}</p>' if st['t'] else '') + (f'<ul class="dots">{li}</ul>' if li else '') + (f'<div class="sph">{ph}</div>' if ph else '') + '</li>'
        steps += '</ol><p><a class="link" href="/cases/%s/">이 현장 전체 보기 %s</a></p></div>' % (ex['id'], ARR)
    photos = ''
    if cs:
        b = cs[0]
        photos = '<div class="block"><h2>시공 전·후</h2>' + compare(b) + '<p class="muted" style="margin-top:12px">%s · <a href="/cases/%s/">사례 보기</a></p></div>' % (E(b['short']), b['id'])
    cards = '<div class="block"><h2>%s 시공사례 %d건</h2><div class="cgrid3" style="grid-template-columns:repeat(auto-fill,minmax(260px,1fr))">%s</div></div>' % (E(s['short']), len(cs), ''.join(case_card(c) for c in cs))
    regs = sorted({place(c) for c in cs})
    regp = '<p class="muted">다녀온 지역: %s</p>' % E(' · '.join(regs)) if regs else ''
    body += (f'<section style="padding-top:56px"><div class="wrap detail"><div>'
             f'<div class="block"><h2>작업 항목</h2><div class="scope">{items}</div></div>'
             f'<div class="block"><h2>이럴 때 맡겨주세요</h2><ul class="checks">{who}</ul></div>'
             f'{photos}{steps}{cards}{regp}'
             f'</div>{aside(s["short"] + " 견적 받기")}</div></section>')
    svc_ld = {"@context": "https://schema.org", "@type": "Service", "name": s['name'], "serviceType": s['name'], "description": s['desc'],
              "provider": {"@type": "HomeAndConstructionBusiness", "name": "굿초이스 집수리", "telephone": "+82-10-5809-9275", "url": SITE + "/"},
              "areaServed": ["서울", "경기", "인천"]}
    ld += '<script type="application/ld+json">%s</script>\n' % json.dumps(svc_ld, ensure_ascii=False)
    write('/service/%s/' % s['slug'], head(s['title'] + ' - 굿초이스 집수리', s['desc'], '/service/%s/' % s['slug'], s['img'], ld) + header('service') + body + footer())

# ---------- case list
crumb, ld = crumbs([('시공사례', None)])
body = phero('photos/c/224468666985/after.jpg', crumb, '굿초이스 집수리 시공사례', '직접 다녀온 현장 %d곳을 지역, 문제, 작업 과정, 완료 사진까지 정리했습니다. 분야를 눌러 비슷한 사례를 찾아보세요.' % N)
filt = '<div class="filters" id="filters" role="group" aria-label="분야 선택" style="margin-top:0"><button type="button" data-f="all" aria-pressed="true">전체 %d</button>' % N + ''.join('<button type="button" data-f="%s" aria-pressed="false">%s %d</button>' % (s['slug'], E(s['short']), len(s['cases'])) for s in SERVICES) + '</div>'
grid = '<div class="cgrid3" id="allCases">' + ''.join(case_card(c).replace('<a class="ccard"', '<a class="ccard" data-svc="%s"' % c['svc'], 1) for c in CASES) + '</div>'
body += '<section style="padding-top:48px"><div class="wrap">' + filt + grid + '<p style="margin-top:40px"><a class="link" href="%s" target="_blank" rel="noopener">네이버 블로그에서 작업 기록 보기 %s</a></p></div></section>' % (BLOG, ARR)
write('/cases/', head('시공사례 %d건 | 지역별 설치·철거·복원 작업 기록 - 굿초이스 집수리' % N, '굿초이스 집수리가 서울·성남·하남·용인·수원 등에서 직접 진행한 시공사례 %d건. 식기세척기 설치, 건조기 직렬, 샤워부스 철거, 원상복구, 문 방향 변경 현장을 사진과 함께 확인하세요.' % N, '/cases/', extra=ld) + header('cases') + body + footer())

# ---------- case detail
for i, c in enumerate(CASES):
    s = SBY[c['svc']]
    t = seo_title(c)
    crumb, ld = crumbs([('시공사례', '/cases/'), (t, None)])
    body = phero('photos/c/%s/after.jpg' % c['id'], crumb, E(t), E(c['sum']))
    info = (f'<table class="info"><tr><th>시공 지역</th><td>{E(c["visited"])}</td></tr><tr><th>작업명</th><td>{E(c["title"])}</td></tr>'
            f'<tr><th>분야</th><td><a href="/service/{s["slug"]}/">{E(s["name"])}</a></td></tr><tr><th>작업일</th><td>{E(c["date"])}</td></tr></table>')
    parts = [f'<div class="block"><h2>현장 정보</h2>{info}</div>']
    if c['problem'] or c['problem_li']:
        pl = ''.join('<li>%s</li>' % E(x) for x in c['problem_li'])
        parts.append('<div class="block"><h2>고객이 요청한 문제</h2>' + ('<p>%s</p>' % E(c['problem']) if c['problem'] else '') + ('<ul class="checks">%s</ul>' % pl if pl else '') + '</div>')
    if c['before']: parts.append(f'<div class="block"><h2>시공 전 사진</h2>{gallery(c, c["before"], "시공 전")}</div>')
    if c['steps']:
        st = '<ol class="story">'
        for k, x in enumerate(c['steps']):
            li = ''.join('<li>%s</li>' % E(y) for y in x['li'][:5])
            ph = ''.join(f'<a class="gbtn" href="/photos/c/{c["id"]}/{n}.jpg" data-lb><img src="/photos/c/{c["id"]}/{n}_s.jpg" alt="{E(x["h"])}" width="420" height="420" loading="lazy"></a>' for n in x['imgs'])
            st += f'<li><h4>STEP {k + 1} · {E(x["h"])}</h4>' + (f'<p>{E(x["t"])}</p>' if x['t'] else '') + (f'<ul class="dots">{li}</ul>' if li else '') + (f'<div class="sph">{ph}</div>' if ph else '') + '</li>'
        st += '</ol>'
        parts.append(f'<div class="block"><h2>작업 방법</h2>{st}</div>')
    elif c['during']:
        parts.append(f'<div class="block"><h2>작업 과정 사진</h2>{gallery(c, c["during"], "작업 과정")}</div>')
    if c['after']: parts.append(f'<div class="block"><h2>시공 완료 사진</h2>{gallery(c, c["after"], "시공 완료")}</div>')
    if c['checks']:
        ck = ''.join(f'<li><b>{E(x["h"])}</b>' + (f'<span>{E(x["t"])}</span>' if x['t'] else '') + ''.join('<span>· %s</span>' % E(y) for y in x['li'][:5]) + '</li>' for x in c['checks'])
        parts.append(f'<div class="block"><h2>시공 후 점검</h2><ul class="checkbox">{ck}</ul></div>')
    if c['result'] or c['result_li']:
        rl = ''.join('<li>%s</li>' % E(x) for x in c['result_li'])
        parts.append('<div class="block"><h2>작업 결과</h2>' + ('<p>%s</p>' % E(c['result']) if c['result'] else '') + ('<ul class="checks">%s</ul>' % rl if rl else '') + '</div>')
    if c['rec'] and c['rec'][0]: parts.append('<div class="block"><h2>이런 경우 비슷한 작업이 필요해요</h2><ul class="checks">%s</ul></div>' % ''.join('<li>%s</li>' % E(x) for x in c['rec']))
    if c['faq']:
        parts.append('<div class="block"><h2>자주 묻는 질문</h2>%s</div>' % ''.join('<details><summary>%s</summary><p>%s</p></details>' % (E(q), E(a)) for q, a in c['faq']))
        ld += '<script type="application/ld+json">%s</script>\n' % json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in c['faq']]}, ensure_ascii=False)
    parts.append(f'<p><a class="link" href="{E(c["blog"])}" target="_blank" rel="noopener">네이버 블로그 원문에서 전체 과정 보기 {ARR}</a></p>')
    rel = [x for x in CASES if x['svc'] == c['svc'] and x['id'] != c['id']][:3]
    if rel: parts.append('<div class="block" style="margin-top:56px"><h2>%s 다른 사례</h2><div class="cgrid3" style="grid-template-columns:repeat(auto-fill,minmax(240px,1fr))">%s</div><p style="margin-top:20px"><a class="link" href="/service/%s/">%s 서비스 안내 %s</a></p></div>' % (E(s['short']), ''.join(case_card(x) for x in rel), s['slug'], E(s['name']), ARR))
    prev, nxt = CASES[i - 1], CASES[(i + 1) % N]
    parts.append(f'<div class="pager"><a href="/cases/{prev["id"]}/"><small>← 이전 사례</small><b>{E(prev["short"])}</b></a><a class="next" href="/cases/{nxt["id"]}/"><small>다음 사례 →</small><b>{E(nxt["short"])}</b></a></div>')
    rlink = ('<a class="btn btn-line" href="/area/%s/">%s 다른 현장 보기</a>' % (RSLUG[c['reg']], E(c['reg']))) if c['reg'] in RSLUG else ''
    body += '<section style="padding-top:56px"><div class="wrap detail"><div>' + compare(c) + ''.join(parts) + '</div>' + aside('비슷한 작업 견적 받기', '<a class="btn btn-line" href="/service/%s/">%s 서비스 보기</a>%s' % (s['slug'], E(s['short']), rlink)) + '</div></section>'
    desc = '%s %s 현장. %s' % (place(c), c['title'], c['problem'] or c['sum'])
    desc = desc[:150].rstrip() + ('…' if len(desc) > 150 else '')
    write('/cases/%s/' % c['id'], head(t + ' | 시공사례 - 굿초이스 집수리', desc, '/cases/%s/' % c['id'], 'photos/c/%s/after.jpg' % c['id'], ld) + header('cases') + body + footer())

# ---------- area index & region pages
by_reg = {}
for c in CASES: by_reg.setdefault(c['reg'], []).append(c)
crumb, ld = crumbs([('출장 지역', None)])
body = phero('photos/c/224235324262/after.jpg', crumb, '출장 지역', '서울·경기·인천을 중심으로 출장 시공합니다. 아래 지역 페이지에서 그 동네에서 실제로 작업한 현장을 확인할 수 있어요.')
rcards = ''
for k, sl, nm in REGION_PAGES:
    cs = by_reg.get(k, [])
    if not cs: continue
    sv = sorted({SBY[c['svc']]['short'] for c in cs})
    rcards += f'<a class="rcard" href="/area/{sl}/"><img src="/photos/c/{cs[0]["id"]}/after.jpg" alt="{E(nm)} 시공 현장" width="720" height="720" loading="lazy"><div><h3>{E(nm)}</h3><p>시공사례 {len(cs)}건 · {E(", ".join(sv[:3]))}</p><span class="go">지역 사례 보기 {ARR}</span></div></a>'
others = [(k, v) for k, v in by_reg.items() if k not in RSLUG]
oth = ''.join('<li><b>%s</b> %s</li>' % (E(k), ' · '.join('<a href="/cases/%s/">%s</a>' % (c['id'], E(c['short'])) for c in v)) for k, v in sorted(others))
alist = ''.join('<div class="acard"><h3>%s</h3><div class="chips">%s</div></div>' % (E(g), ''.join('<span>%s</span>' % E(x) for x in xs)) for g, xs in AREA_LIST)
body += (f'<section style="padding-top:48px"><div class="wrap"><h2 class="h2" style="margin-top:0">지역별 시공사례</h2><div class="rgrid">{rcards}</div>'
         f'<div class="block" style="margin-top:48px"><h2>그 밖에 다녀온 지역</h2><ul class="olist">{oth}</ul></div>'
         f'<h2 class="h2" style="margin-top:72px">출장 가능 지역</h2><div class="areagrid" style="margin-top:28px">{alist}</div>'
         f'<div class="nation"><div><b>목록에 없는 지역도 문의해 주세요</b><p style="color:var(--muted);font-size:15px">작업 내용과 일정에 따라 출장 가능 여부를 안내해 드립니다.</p></div><div class="ctas" style="margin:0">{CALL}{SMS}</div></div></div></section>')
write('/area/', head('출장 지역 | 서울·성남·하남·용인·수원 집수리 - 굿초이스 집수리', '굿초이스 집수리 출장 지역 안내. 서울, 성남, 하남, 용인, 수원, 경기 광주 등에서 실제로 진행한 시공사례를 지역별로 확인하세요.', '/area/', extra=ld) + header('area') + body + footer())

for k, sl, nm in REGION_PAGES:
    cs = by_reg.get(k, [])
    if not cs: continue
    crumb, ld = crumbs([('출장 지역', '/area/'), (nm, None)])
    svcs = []
    for c in cs:
        if c['svc'] not in svcs: svcs.append(c['svc'])
    svnames = [SBY[x]['short'] for x in svcs]
    spots = []
    for c in cs:
        v = c['visited'].replace('경기도 ', '').replace('서울시 ', '')
        if v not in spots: spots.append(v)
    lead = f'{nm}에서 굿초이스 집수리가 직접 진행한 시공사례 {len(cs)}건입니다. {", ".join(svnames)} 작업을 했습니다.'
    body = phero('photos/c/%s/after.jpg' % cs[0]['id'], crumb, E(nm) + ' 집수리 시공사례', E(lead))
    if k == '서울':
        groups = {}
        for c in cs: groups.setdefault(c['gu'] or '서울', []).append(c)
        sec = ''.join('<div class="block"><h2>%s <small>%d건</small></h2><div class="cgrid3" style="grid-template-columns:repeat(auto-fill,minmax(260px,1fr))">%s</div></div>' % (E(g), len(v), ''.join(case_card(c) for c in v)) for g, v in sorted(groups.items(), key=lambda x: -len(x[1])))
    else:
        sec = '<div class="block"><h2>%s 시공사례</h2><div class="cgrid3" style="grid-template-columns:repeat(auto-fill,minmax(260px,1fr))">%s</div></div>' % (E(nm), ''.join(case_card(c) for c in cs))
    rows = ''.join(f'<tr><td>{E(c["date"])}</td><td>{E(c["visited"].replace("경기도 ", "").replace("서울시 ", ""))}</td><td><a href="/cases/{c["id"]}/">{E(c["short"])}</a></td></tr>' for c in cs)
    table = f'<div class="block"><h2>{E(nm)} 작업 기록</h2><table class="info rtable"><tr><th>작업일</th><th>현장</th><th>작업</th></tr>{rows}</table></div>'
    links = ''.join('<a class="btn btn-line" href="/service/%s/">%s</a>' % (x, E(SBY[x]['short'])) for x in svcs)
    body += f'<section style="padding-top:56px"><div class="wrap detail"><div>{table}{sec}<div class="block"><h2>{E(nm)}에서 진행한 서비스</h2><div class="ctas">{links}</div></div></div>{aside(nm + " 출장 견적 받기")}</div></section>'
    desc = f'{nm} 집수리 시공사례 {len(cs)}건. {", ".join(svnames)} 등 {nm}에서 굿초이스 집수리가 직접 작업한 현장과 사진을 확인하세요.'
    write('/area/%s/' % sl, head(f'{nm} 집수리 | {", ".join(svnames[:3])} 시공사례 - 굿초이스 집수리', desc, '/area/%s/' % sl, 'photos/c/%s/after.jpg' % cs[0]['id'], ld) + header('area') + body + footer())

# ---------- process
crumb, ld = crumbs([('진행 방법', None)])
body = phero('photos/c/224219219612/after.jpg', crumb, '문자 한 통으로 시작합니다', '현장에서는 통화가 어려울 때가 많아요. 문자로 사진과 지역을 남겨주시면 확인하는 대로 바로 연락드립니다.')
FAQ = [
    ('견적은 어떻게 받나요?', PHOTO_GUIDE + ' 작업 종류와 지역(동까지)을 함께 적어주시면 더 빠릅니다. ' + PHOTO_NOTE),
    ('사진은 어떻게 보내나요?', '휴대폰 문자(MMS)에 사진을 첨부해 010-5809-9275로 보내주세요. 홈페이지의 문자 견적 버튼을 누르면 작업 종류와 지역을 적는 양식이 미리 채워집니다.'),
    ('전월세 이사 전에 작업해도 되나요?', '네, 가능합니다. 정수기나 식기세척기 설치 때 타공하거나 바꾼 부분이 있다면 퇴거 전에 원상복구를 많이 하십니다.'),
    ('제품은 제가 사도 되나요?', '가능합니다. 식기세척기·건조기처럼 구매하신 제품의 모델명을 먼저 알려주시면 설치 공간에 맞는지 확인해 드립니다.'),
    ('여러 가지를 한 번에 맡길 수 있나요?', '네. 한 번 방문할 때 여러 작업을 함께 처리해 드립니다. 문의하실 때 목록을 같이 적어주세요.'),
]
faq_html = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (E(q), E(a)) for q, a in FAQ)
faq_ld = '<script type="application/ld+json">%s</script>\n' % json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}, ensure_ascii=False)
body += f'''<section style="padding-top:24px"><div class="wrap">
<ol class="steps">
<li><h3>사진 2장 + 지역</h3><p>{E(PHOTO_GUIDE)} 작업할 지역(동까지)도 함께 적어주세요.</p></li>
<li><h3>상담 · 견적 안내</h3><p>사진 확인 후 연락드려 작업 방법과 견적을 안내합니다. {E(PHOTO_NOTE)}</p></li>
<li><h3>일정 확정</h3><p>편한 날짜와 시간을 정하고, 필요한 부품을 미리 준비해 갑니다.</p></li>
<li><h3>시공 · 마무리 점검</h3><p>작업 후 작동과 마감 상태를 함께 확인하고 주변 흔적까지 정리합니다.</p></li>
</ol></div></section>
<section style="background:var(--surface)"><div class="wrap">
<p class="label">Photo Guide</p><h2 class="h2">이렇게 찍어 보내주세요</h2><p class="sub">{E(PHOTO_GUIDE)}<br>{E(PHOTO_NOTE)}</p>
<div class="guide">
<figure><img src="/photos/c/224425527882/before.jpg" alt="주방 전체가 보이게 찍은 예시" width="720" height="720" loading="lazy"><figcaption><b>① 전체 현장 사진 1장</b><span>주변 가구와 위치가 함께 보이게</span></figcaption></figure>
<figure><img src="/photos/c/224409039077/before.jpg" alt="문제 부위를 가까이서 찍은 예시" width="720" height="720" loading="lazy"><figcaption><b>② 문제 부위 사진 1장</b><span>고장 난 부분, 구멍, 부속이 잘 보이게</span></figcaption></figure>
</div>
<div class="ctas" style="margin-top:28px">{CALL}{SMS}</div>
</div></section>
<section><div class="wrap" style="max-width:860px"><p class="label">FAQ</p><h2 class="h2" style="margin-bottom:28px">자주 묻는 질문</h2>{faq_html}</div></section>'''
write('/process/', head('진행 방법 | 사진 견적부터 시공까지 - 굿초이스 집수리', '굿초이스 집수리 진행 방법: ' + PHOTO_GUIDE + ' 상담 후 일정을 잡고 시공과 마무리 점검까지 진행합니다.', '/process/', extra=ld + faq_ld) + header('process') + body + footer())

# ---------- contact
crumb, ld = crumbs([('견적 문의', None)])
body = phero('photos/c/224471235220/after.jpg', crumb, '견적 문의', E(PHOTO_GUIDE) + ' 현장에서는 통화가 어려울 수 있어 문자를 남겨주시면 확인 후 바로 연락드립니다.')
opts = ''.join('<option>%s</option>' % E(s['name']) for s in SERVICES) + '<option>기타</option>'
body += f'''<section style="padding-top:48px"><div class="wrap ctgrid">
<div>
  <div class="telcard"><small>전화 · 문자 상담</small><a class="bigtel" id="tel" href="tel:{TELN}" data-track="call">{TEL}</a>
  <div class="ctas"><a class="btn" href="tel:{TELN}" data-track="call" style="background:#fff;color:#111"><svg><use href="#phone"/></svg>전화하기</a><a class="btn btn-ghost" href="{TALK}" target="_blank" rel="noopener"><svg><use href="#chat"/></svg>네이버 톡톡</a></div></div>
  <div class="how">
    <div><b>1</b><p>전체 현장 사진 1장<small>주변 가구와 위치가 함께 보이게</small></p></div>
    <div><b>2</b><p>문제 부위 사진 1장<small>고장 난 부분이 잘 보이게 가까이</small></p></div>
    <div><b>3</b><p>작업 종류와 지역<small>예) 식기세척기 설치 · 하남시 위례동</small></p></div>
  </div>
  <p class="note" style="margin-top:16px">{E(PHOTO_NOTE)}</p>
</div>
<form id="qform" novalidate>
  <h3>문자 견적 보내기</h3>
  <p class="muted" style="margin:-4px 0 14px;font-size:14px">아래 내용을 적고 버튼을 누르면 휴대폰 문자 앱이 열리고 내용이 채워집니다. 사진은 문자 앱에서 첨부해 주세요.</p>
  <div class="fr">
    <label for="f-type">작업 종류<select id="f-type" name="type" required>{opts}</select></label>
    <label for="f-area">지역 (동까지)<input id="f-area" name="area" placeholder="예) 하남시 위례동" required></label>
  </div>
  <div class="fr">
    <label for="f-name">이름<input id="f-name" name="name" autocomplete="name" placeholder="홍길동"></label>
    <label for="f-date">희망 일정<input id="f-date" name="date" placeholder="예) 토요일 오전"></label>
  </div>
  <label for="f-msg">요청 내용<textarea id="f-msg" name="msg" placeholder="예) 빌트인 식기세척기를 넣고 싶은데 하부장이 있어요."></textarea></label>
  <label class="agree" for="f-agree"><input id="f-agree" type="checkbox" required>상담을 위해 입력한 내용이 문자로 전송되는 것에 동의합니다.</label>
  <button class="btn btn-accent" type="submit" data-track="sms_form">문자 앱으로 보내기</button>
  <div class="done" id="done" hidden></div>
  <p class="privacy">개인정보 안내: 이 홈페이지는 입력하신 내용을 서버에 저장하지 않습니다. 내용은 고객님 휴대폰의 문자 앱으로만 전달되며, 받은 문자는 상담과 시공 일정 안내에만 사용하고 상담이 끝나면 삭제합니다.</p>
</form>
</div></section>'''
write('/contact/', head('견적 문의 | 전화·문자 사진 견적 - 굿초이스 집수리', '굿초이스 집수리 견적 문의 010-5809-9275. ' + PHOTO_GUIDE + ' ' + PHOTO_NOTE, '/contact/', extra=ld) + header('contact') + body + footer())

# ---------- home
H = LEGACY_HTML
home = H[H.index('<div class="strip"'):H.index('<!-- ================= SERVICE LIST')]
home = home[:home.rindex('</div>')]  # .view 닫는 태그 제거
# 기준 문장: 애니메이션 없이 고정
home = re.sub(r'<section class="stmt" id="statement">.*?</section>', '<section class="stmt" id="statement"><div class="wrap"><p class="label">Our Standard</p><p class="stmt-t static">물이 넘친다고 바로 실리콘부터 쏘지 않습니다. 어디서 새는지 먼저 찾고, 꼭 필요한 만큼만 고치고, 나사 구멍 하나까지 정리하고 나옵니다.</p></div></section>', home, flags=re.S)
home = home.replace('<div class="services" id="homeServices"></div>', '<div class="services">' + ''.join(svc_card(s) for s in SERVICES) + '</div>')
# 전후 비교 탭: 정적 패널
ba_ids = ['224409039077', '224369548827', '224457415114', '224325847991']
ba_names = {'224409039077': '샤워부스 물막이', '224369548827': '문 방향 변경', '224457415114': '샤워부스 철거', '224325847991': '디스펜서 교체'}
tabs = ''.join('<button type="button" role="tab" data-id="%s" aria-selected="%s">%s</button>' % (i, 'true' if k == 0 else 'false', ba_names[i]) for k, i in enumerate(ba_ids))
panels = ''
for k, i in enumerate(ba_ids):
    c = CBY[i]; L = LCASE[i]
    panels += f'<div class="feature" data-panel="{i}"{"" if k == 0 else " hidden"}>{compare(c)}<div><span class="cat">{E(place(c))} · {E(SBY[c["svc"]]["short"])}</span><h3 style="margin-top:10px">{E(L["title"])}</h3><p>{E(L["sum"])}</p><ul class="checks">{"".join("<li>%s</li>" % E(w) for w in L["work"])}</ul><div class="ctas"><a class="btn btn-accent" href="/cases/{i}/">이 현장 자세히 보기 {ARR}</a></div></div></div>'
home = re.sub(r'<div class="batabs" id="baTabs"[^>]*></div>', '<div class="batabs" id="baTabs" role="tablist" aria-label="비교할 현장">' + tabs + '</div>', home)
home = re.sub(r'<div class="feature" id="baView">.*?</div>\s*</div>\s*</div>\s*</section>', '<div id="baView">' + panels + '</div>\n  </div>\n</section>', home, count=1, flags=re.S)
# 사진 릴
reel = []
for c in CASES:
    for n in (c['during'][:2] + c['after'][:1]):
        reel.append((c, n))
ra, rb = reel[0::2][:16], reel[1::2][:16]
row = lambda L: '<div class="track">' + ''.join(f'<a href="/cases/{c["id"]}/" tabindex="-1"><img src="/photos/c/{c["id"]}/{n}_s.jpg" alt="{E(c["short"])} 현장 사진" loading="lazy" width="240" height="240"><span>{E(place(c))}</span></a>' for c, n in L) * 2 + '</div>'
home = home.replace('<div class="row" id="reel1"></div>', '<div class="row">' + row(ra) + '</div>').replace('<div class="row rev" id="reel2"></div>', '<div class="row rev">' + row(rb) + '</div>')
home = home.replace('<div class="cgrid3" id="homeCases"></div>', '<div class="cgrid3">' + ''.join(case_card(c) for c in CASES[:6]) + '</div>')
# 링크 변환
home = re.sub(r'href="#case-(\d+)"', lambda m: 'href="/cases/%s/"' % m.group(1), home)
home = re.sub(r'href="#svc-(\w+)"', lambda m: 'href="/service/%s/"' % OLD2SLUG.get(m.group(1), ''), home)
for a, b in [('#service', '/service/'), ('#cases', '/cases/'), ('#process', '/process/'), ('#area', '/area/'), ('#contact', '/contact/')]:
    home = home.replace('href="%s"' % a, 'href="%s"' % b)
home = re.sub(r'src="photos/', 'src="/photos/', home)
home = home.replace('url(photos/', 'url(/photos/')
home = re.sub(r'/photos/(\d+)_after\.jpg"([^>]*?)width="120" height="120"', lambda m: '/photos/c/%s/after_s.jpg"%swidth="120" height="120"' % (m.group(1), m.group(2)), home)
home = re.sub(r'/photos/(\d+)_after\.jpg"', lambda m: '/photos/c/%s/after.jpg"' % m.group(1), home)
# 사진 견적 문구 통일
home = home.replace('<h3>사진 2장이면 바로 견적</h3><p>멀리서 1장, 가까이 1장. 문자로 사진과 지역을 보내주시면 확인 후 바로 견적과 일정을 잡아드립니다.</p>', '<h3>사진으로 먼저 상담</h3><p>%s %s</p>' % (E(PHOTO_GUIDE), E(PHOTO_NOTE)))
home = home.replace('서울·경기·인천은 물론 평택·천안까지. 어느 현장이든 같은 기준으로 시공합니다.', '서울·경기·인천은 물론 세종·천안·아산까지. 어느 현장이든 같은 기준으로 시공합니다.')
home = home.replace('<h3>사진 2장 + 지역</h3><p>멀리서 1장, 가까이 1장. 문자나 톡톡으로 보내주세요.</p>', '<h3>사진 2장 + 지역</h3><p>전체 현장 1장, 문제 부위 1장과 지역을 문자로 보내주세요.</p>')
home = home.replace('<h3>바로 견적</h3><p>사진을 보고 작업 방법과 비용을 안내해 드려요.</p>', '<h3>상담 · 견적 안내</h3><p>사진을 보고 작업 방법과 비용을 안내해 드려요. 사진만으로 어려우면 현장을 확인합니다.</p>')
home = home.replace('<h3>시공 · 정리</h3><p>흔적까지 정리하고, 함께 확인한 뒤 마무리해요.</p>', '<h3>시공 · 마무리 점검</h3><p>작동과 마감을 함께 확인하고 흔적까지 정리해요.</p>')
home = re.sub(r'<details><summary>견적은 어떻게 받나요\?</summary><p>.*?</p></details>', '<details><summary>견적은 어떻게 받나요?</summary><p>%s %s</p></details>' % (E(PHOTO_GUIDE), E(PHOTO_NOTE)), home)
home = re.sub(r'<div class="band on-blue photo"[^>]*>.*?</div>\s*</div>\s*</div>', cta_band() + '\n  </div>', home, count=1, flags=re.S)
# 지역 박스: 블로그 기준 지역 + 지역 페이지 링크
home = re.sub(r'<div class="wrap areabox">.*?</section>', '<div class="wrap areabox"><div><p class="label">Area</p><h2 class="h2">서울·경기·인천<br>출장 시공</h2><p class="sub">지역을 누르면 그 동네에서 실제로 작업한 현장을 볼 수 있어요.</p><div class="ctas">' + ''.join('<a class="btn btn-line" href="/area/%s/">%s</a>' % (sl, E(nm)) for k, sl, nm in REGION_PAGES) + '</div></div><div class="areachips">' + ''.join('<div><b>%s</b><p>%s</p></div>' % (E(g), E(' · '.join(xs))) for g, xs in AREA_LIST) + '<div class="all"><b>그 외 지역</b><p>작업과 일정에 따라 출장 가능 여부를 안내해 드려요</p></div></div></div>\n</section>', home, count=1, flags=re.S)
# 남은 sms/tel 링크 정리
home = home.replace('href="sms:01058099275"', 'href="%s" data-sms data-track="sms"' % E(SMS_HREF)).replace('href="tel:01058099275"', 'href="tel:01058099275" data-track="call"')
home = home.replace(' id="stmtT"', '')
home = re.sub(r'<img ([^>]*?)alt="" ([^>]*)><span><b>(.*?)</b>', lambda m: '<img %salt="%s 해결 사례" %s><span><b>%s</b>' % (m.group(1), m.group(3), m.group(2), m.group(3)), home)
home = re.sub(r'<img ([^>]*?)alt="" ([^>]*)><div><h3>(.*?)</h3>', lambda m: '<img %salt="%s 시공 사례" %s><div><h3>%s</h3>' % (m.group(1), m.group(3), m.group(2), m.group(3)), home)
home = re.sub(r'<img ([^>]*?)alt="" ([^>]*)><small>(.*?)</small><h3>(.*?)</h3>', lambda m: '<img %salt="%s" %s><small>%s</small><h3>%s</h3>' % (m.group(1), m.group(4), m.group(2), m.group(3), m.group(4)), home)

cols = [CASES[k::3][:7] for k in range(3)]
colhtml = ''.join('<div class="cc%d"><div class="ctrk">%s</div></div>' % (k + 1, ''.join(f'<img src="/photos/c/{c["id"]}/after_s.jpg" alt="" width="300" height="300" loading="{"eager" if (k == 1 and j < 2) else "lazy"}" decoding="async">' for j, c in enumerate(col)) * 2) for k, col in enumerate(cols))
hero = f'''<section class="cine">
  <div class="cine-cols" aria-hidden="true">{colhtml}</div>
  <div class="cine-shade" aria-hidden="true"></div>
  <div class="wrap cine-in">
    <span class="kicker"><i></i>집수리 &amp; 리폼 전문 · 누적 시공 1,000건+ · 공개 시공사례 {N}건</span>
    <h1 class="cine-h"><span class="ln"><span>굿초이스 집수리,</span></span><span class="ln"><span>설치부터 <em>철거·복원</em>까지</span></span></h1>
    <p class="cine-lead">빌트인 식기세척기 설치 및 철거, 건조기 직렬 설치, 샤워부스 철거, 정수기 철거 및 싱크대 상판 복원, 문 방향 변경, 가구 리폼까지. 다양한 생활 수리와 설치·철거 작업을 전문적으로 진행합니다.</p>
    <div class="ctas">
      <a class="btn btn-accent" href="tel:{TELN}" data-track="call"><svg><use href="#phone"/></svg>전화 상담 <span class="tnum">{TEL}</span></a>
      <a class="btn btn-ghost" href="{E(SMS_HREF)}" data-sms data-track="sms"><svg><use href="#chat"/></svg>문자 견적</a>
    </div>
  </div>
  <ul class="wrap cine-meta hl4">
    <li><svg><use href="#ok"/></svg><b>서울·경기·인천</b><span>출장 시공</span></li>
    <li><svg><use href="#ok"/></svg><b>현장 사진</b><span>사진으로 먼저 상담</span></li>
    <li><svg><use href="#ok"/></svg><b>합리적인 견적</b><span>필요한 작업만 안내</span></li>
    <li><svg><use href="#ok"/></svg><b>전문 시공</b><span>마무리 점검까지</span></li>
  </ul>
</section>
'''
lb_ld = {"@context": "https://schema.org", "@type": "HomeAndConstructionBusiness", "name": "굿초이스 집수리", "description": "빌트인 식기세척기 설치·철거, 건조기 직렬 설치, 샤워부스 철거, 정수기 철거 및 싱크대 상판 복원, 문 방향 변경, 가구 리폼 전문.",
         "telephone": "+82-10-5809-9275", "url": SITE + "/", "image": SITE + "/photos/c/224425527882/after.jpg", "areaServed": ["서울", "경기", "인천"], "sameAs": [BLOG],
         "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s['name'], "url": SITE + "/service/%s/" % s['slug']}} for s in SERVICES]}
extra = '<script type="application/ld+json">%s</script>\n' % json.dumps(lb_ld, ensure_ascii=False)
write('/index.html', head('굿초이스 집수리 | 식기세척기·건조기 설치, 샤워부스 철거, 원상복구', '굿초이스 집수리: 빌트인 식기세척기 설치·철거, 건조기 직렬 설치, 샤워부스 철거, 정수기 철거와 싱크대 상판 복원, 문 방향 변경, 가구 리폼. 서울·경기·인천 출장, 사진으로 먼저 상담합니다. 010-5809-9275', '/', extra=extra) + header('') + hero + home + footer())

# ---------- 404
write('/404.html', head('페이지를 찾을 수 없습니다 - 굿초이스 집수리', '요청하신 페이지를 찾을 수 없습니다.', '/404.html').replace('index,follow', 'noindex') + header('') + '<section class="phero"><div class="wrap"><h1>페이지를 찾을 수 없어요</h1><p class="lead">주소가 바뀌었을 수 있어요. 아래에서 찾아보세요.</p><div class="ctas"><a class="btn btn-accent" href="/">홈으로</a><a class="btn btn-ghost" href="/cases/">시공사례</a><a class="btn btn-ghost" href="/service/">서비스</a></div></div></section>' + footer())
URLS.remove('/404.html')

# ---------- robots / sitemap
open(os.path.join(ROOT, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\nDisallow: /tools/\n\nSitemap: %s/sitemap.xml\n' % SITE)
today = datetime.date.today().isoformat()
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in URLS:
    lm = today
    m = re.match(r'/cases/(\d+)/', u)
    if m: lm = CBY[m.group(1)]['date']
    sm += '  <url><loc>%s%s</loc><lastmod>%s</lastmod></url>\n' % (SITE, u, lm)
sm += '</urlset>\n'
open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(sm)
print('pages', len(URLS))
