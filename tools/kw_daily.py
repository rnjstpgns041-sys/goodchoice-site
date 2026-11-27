# -*- coding: utf-8 -*-
"""매일 새 검색어 페이지 N개 공개 목록에 추가.

사용: python3 tools/kw_daily.py [N=50] [YYYY-MM-DD=오늘 KST]
- tools/kw_published.json 에 오늘 날짜로 N개 추가(이미 오늘 것이 있으면 그대로 둠 = 같은 날 두 번 돌려도 안전).
- tools/indexnow-urls.txt 에 오늘 새 주소를 씀 (GitHub Action 이 main 에 올라오면 네이버·빙 IndexNow 로 보냄).
- 남은 조합 수를 출력. 0 이면 kw_data.py 에 작업이나 지역을 더 넣어야 함.
그다음 python3 tools/build.py 로 페이지·sitemap.xml·rss.xml 을 다시 만듭니다.
"""
import datetime, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import kw_data

n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
day = sys.argv[2] if len(sys.argv) > 2 else (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d')
fp = os.path.join(ROOT, 'tools/kw_published.json')
pub = json.load(open(fp, encoding='utf-8')) if os.path.exists(fp) else {}
done = {s for v in pub.values() for s in v}
if day not in pub:
    new, per = [], {}
    for cap in (5, 10, 10 ** 6):  # 하루에 한 지역이 몰리지 않게 지역당 5개까지 먼저
        for t, r in kw_data.candidates():
            k = '%s@%s' % (t, r)
            if k in done or k in new or per.get(r, 0) >= cap: continue
            new.append(k); per[r] = per.get(r, 0) + 1
            if len(new) == n: break
        if len(new) == n: break
    if new: pub[day] = new
    json.dump(pub, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
today = pub.get(day, [])
urls = ['https://las8015.com/k/%s-%s/' % (k.split('@')[1], k.split('@')[0]) for k in today]
open(os.path.join(ROOT, 'tools/indexnow-urls.txt'), 'w').write('\n'.join(urls + ['https://las8015.com/k/']) + '\n')
left = len(kw_data.candidates()) - len({s for v in pub.values() for s in v})
T = {t['slug']: t['kw'] for t in kw_data.TOPICS}
R = {r[0]: r[1] for r in kw_data.REGIONS}
print('date', day, 'today', len(today), 'left', left)
for k in today:
    t, r = k.split('@')
    print(' ', R[r], T[t])
