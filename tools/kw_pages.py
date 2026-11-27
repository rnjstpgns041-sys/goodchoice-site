# -*- coding: utf-8 -*-
# build.py 안에서 exec 됩니다 (head/header/footer/write/CASES/PRICES 등 그대로 사용).
# tools/kw_published.json 에 올라간(공개된) 검색어 페이지만 /k/<지역>-<작업>/ 으로 만듭니다.
import sys as _sys
_sys.path.insert(0, os.path.join(ROOT, 'tools'))
import kw_data as _kd

KW_PUB = json.load(open(os.path.join(ROOT, 'tools/kw_published.json'), encoding='utf-8')) if os.path.exists(os.path.join(ROOT, 'tools/kw_published.json')) else {}
KT = {t['slug']: t for t in _kd.TOPICS}
KR = {r[0]: r for r in _kd.REGIONS}
KSUB = {'bundang': '분당', 'pangyo': '판교', 'wirye': '위례', 'gwanggyo': '광교', 'dongtan': '동탄', 'ilsan': '일산', 'pyeongchon': '평촌', 'songdo': '송도', 'cheongna': '청라'}
KPRICE = {n: (d, v) for _, rows in PRICES for n, d, v in rows}
KPRICE['기본 설치'] = ('', '15만원부터')
KPAGES = []  # (date, topic, region)
for _d in sorted(KW_PUB):
    for _s in KW_PUB[_d]:
        _t, _r = _s.split('@')
        if _t in KT and _r in KR: KPAGES.append((_d, _t, _r))
KSET = {(t, r) for _, t, r in KPAGES}
KDATE = {(t, r): d for d, t, r in KPAGES}


def kurl(t, r): return '/k/%s-%s/' % (r, t)
def ktitle(t, r): return '%s %s' % (KR[r][1], KT[t]['kw'])


def kcases_region(r):
    reg = KR[r][3]
    if r in KSUB: return [c for c in CASES if KSUB[r] in c['visited']]
    if reg[1]: return [c for c in CASES if c['reg'] == reg[0] and c['gu'] == reg[1]]
    return [c for c in CASES if c['reg'] == reg[0]]


for _d, t, r in KPAGES:
    T, R = KT[t], KR[r]
    lab, full = R[1], R[2]
    kw = T['kw']
    h1 = '%s %s' % (lab, kw)
    s = SBY[T['svc']]
    lead = T['lead'].format(R=lab, RF=full)
    # 가격
    prows = ''
    for pn in T['price']:
        if pn in KPRICE:
            d, v = KPRICE[pn]
            prows += f'<tr><th>{E(pn)}</th><td>{E(v)}{(" · " + E(d)) if d else ""}</td></tr>'
    if not prows: prows = '<tr><th>비용</th><td>사진 확인 후 안내</td></tr>'
    summary = (f'<div class="block"><h2>{E(h1)} 한눈에 보기</h2><table class="info">'
               f'<tr><th>작업</th><td>{E(kw)}</td></tr>{prows}'
               f'<tr><th>출장 지역</th><td>{E(full)} 포함 서울·경기·인천</td></tr>'
               f'<tr><th>상담</th><td>전체 사진 1장 + 문제 부위 사진 1장을 문자로 보내주세요</td></tr>'
               f'<tr><th>전화·문자</th><td><a href="tel:{TELN}" data-track="call">{TEL}</a></td></tr></table>'
               '<p class="muted" style="margin-top:10px">가격은 사장님이 안내한 기준 가격이에요. 현장 상태와 자재에 따라 달라질 수 있어요.</p></div>')
    who = '<div class="block"><h2>이럴 때 맡겨주세요</h2><ul class="checks">%s</ul></div>' % ''.join('<li>%s</li>' % E(w) for w in T['who'])
    pts = '<div class="block"><h2>%s 이렇게 진행해요</h2><ol class="story">%s</ol></div>' % (E(kw), ''.join('<li><h3><span class="sn">STEP %d</span>%s</h3></li>' % (i + 1, E(p)) for i, p in enumerate(T['points'])))
    # 실제 사례: 같은 지역 → 같은 작업 순
    local = kcases_region(r)
    same = [c for c in local if c['svc'] == T['svc']]
    picks, seen = [], set()
    for c in same + [c for c in CASES if c['svc'] == T['svc']] + local:
        if c['id'] in seen: continue
        seen.add(c['id']); picks.append(c)
        if len(picks) == 3: break
    if local:
        note = '%s에서 굿초이스 집수리가 직접 다녀온 현장은 %d곳이에요.' % (lab, len(local))
        if same: note += ' 그중 %s 작업 %d건을 먼저 보여드려요.' % (s['short'], len(same))
    else:
        note = '아직 %s 현장 기록은 없어서, 다른 지역에서 진행한 %s 시공사례를 보여드려요.' % (lab, s['short'])
    cases_html = ('<div class="block"><h2>실제 시공사례</h2><p class="muted">%s</p><div class="cgrid3" style="grid-template-columns:repeat(auto-fill,minmax(260px,1fr))">%s</div></div>' % (E(note), ''.join(case_card(c) for c in picks))) if picks else ''
    faq = list(T['faq']) + [('%s도 출장 오시나요?' % lab, '네. %s는 출장 지역이에요. 사진과 동 이름을 문자로 보내주시면 가능한 일정을 알려드려요.' % full)]
    faq_html = '<div class="block"><h2>자주 묻는 질문</h2>%s</div>' % ''.join('<details><summary>%s</summary><p>%s</p></details>' % (E(q), E(a)) for q, a in faq)
    # 내부 링크 (이미 공개된 페이지만)
    near_t = [x for x in _kd.TOPICS if x['slug'] != t and (x['slug'], r) in KSET]
    near_r = [x for x in _kd.REGIONS if x[0] != r and (t, x[0]) in KSET][:24]
    links = ''
    if near_t:
        links += '<div class="block"><h2>%s 다른 작업</h2><div class="ctas">%s</div></div>' % (E(lab), ''.join('<a class="btn btn-line" href="%s">%s</a>' % (kurl(x['slug'], r), E(ktitle(x['slug'], r))) for x in near_t))
    if near_r:
        links += '<div class="block"><h2>다른 지역 %s</h2><div class="ctas">%s</div></div>' % (E(kw), ''.join('<a class="btn btn-line" href="%s">%s</a>' % (kurl(t, x[0]), E(x[1])) for x in near_r))
    links += '<p><a class="link" href="/service/%s/">%s 서비스 자세히 보기 %s</a></p>' % (s['slug'], E(s['name']), ARR)
    crumb, ld = crumbs([('지역별 안내', '/k/'), (h1, None)])
    sld = {"@context": "https://schema.org", "@type": "Service", "name": h1, "serviceType": kw, "description": lead,
           "provider": {"@type": "HomeAndConstructionBusiness", "name": "굿초이스 집수리", "telephone": "+82-10-5809-9275", "url": SITE + "/"},
           "areaServed": full}
    fld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    ld += '<script type="application/ld+json">%s</script>\n<script type="application/ld+json">%s</script>\n' % (json.dumps(sld, ensure_ascii=False), json.dumps(fld, ensure_ascii=False))
    img = (picks[0] and 'photos/c/%s/after.jpg' % picks[0]['id']) if picks else s['img']
    body = phero(img, crumb, E(h1), E(lead))
    body += (f'<section style="padding-top:56px"><div class="wrap detail"><div>{summary}{who}{pts}{cases_html}{faq_html}{links}</div>'
             f'{aside(h1 + " 견적 받기")}</div></section>')
    pdesc = lead[:150].rstrip() + ('…' if len(lead) > 150 else '')
    ttl = '%s | %s 출장 · 사진 견적 - 굿초이스 집수리' % (h1, full)
    write(kurl(t, r), head(ttl, pdesc, kurl(t, r), img, ld) + header('') + body + footer())

# ---------- /k/ 모음 페이지
if KPAGES:
    crumb, ld = crumbs([('지역별 안내', None)])
    body = phero('photos/c/224235324262/after.jpg', crumb, '지역별 집수리 안내', '서울·경기·인천 동네별로 많이 찾는 작업을 정리했어요. 지역과 작업을 골라 가격·진행 방법·실제 시공사례를 확인하세요.')
    sec = ''
    for T in _kd.TOPICS:
        rs = [x for x in _kd.REGIONS if (T['slug'], x[0]) in KSET]
        if not rs: continue
        sec += '<div class="block"><h2>%s</h2><div class="ctas">%s</div></div>' % (E(T['kw']), ''.join('<a class="btn btn-line" href="%s">%s</a>' % (kurl(T['slug'], x[0]), E(ktitle(T['slug'], x[0]))) for x in rs))
    body += '<section style="padding-top:48px"><div class="wrap">%s<div style="margin-top:56px">%s</div></div></section>' % (sec, cta_band())
    write('/k/', head('지역별 집수리 안내 | 동네별 작업·가격·시공사례 - 굿초이스 집수리', '서울·경기·인천 지역별로 식기세척기 설치, 건조기 직렬설치, 샤워부스 철거, 욕조 코팅, 도배 등 많이 찾는 작업의 가격과 진행 방법, 실제 시공사례를 정리했습니다.', '/k/', extra=ld) + header('') + body + footer())
