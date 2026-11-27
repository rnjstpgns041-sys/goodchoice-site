# 매일 오전 8시 검색어 페이지 50개 (굿초이스 집수리, las8015.com)

사장님(권세훈) 요청 2026-11-27: "매일 오전 8시마다 색인 50개, 사람들이 검색 많이 할 만한 걸로".

1. `git fetch origin main && git checkout -B claude/<작업 브랜치> origin/main`
2. `pip install -q fonttools brotli` (없을 때만), `python3 tools/kw_daily.py 50`
   - 오늘(KST) 것이 이미 있으면 새로 고르지 않음. `left` 가 100 아래로 떨어지면 tools/kw_data.py 에
     네이버 자동완성에 실제로 뜨는 작업(굿초이스가 실제로 하는 것만)이나 지역을 더 넣고 사장님께 한 줄 알림.
3. `python3 tools/build.py` (10초 정도, /mnt/project-files/homepage/photos/blog 필요)
4. 커밋(`검색어 페이지 50개 추가 (YYYY-MM-DD)`) → push → main 으로 PR → squash 머지.
5. 머지되면 GitHub Action `indexnow` 가 배포를 기다렸다가 tools/indexnow-urls.txt 의 주소를
   네이버(searchadvisor.naver.com/indexnow)·빙에 보냄. 실행 결과에서 둘 다 200/202 인지 확인.
6. 스레드에 짧게 보고(오늘 대표 검색어 몇 개, 네이버 응답). 실패했을 때만 자세히.

규칙: 가격은 build.py PRICES 에 있는 것만. 사실이 아닌 후기·경력·숫자 금지. 노란색 금지, Pretendard.
페이지는 손으로 고치지 말고 kw_data.py / kw_pages.py 를 고친 뒤 build.py.
