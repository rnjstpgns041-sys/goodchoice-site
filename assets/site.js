/* 굿초이스 집수리 공통 스크립트 (본문은 모두 HTML에 들어 있고, 이 파일은 편의 기능만 담당) */
(function () {
  var d = document;

  // 예전 한 페이지 주소(#svc-dish, #case-123 등)로 들어온 경우 새 주소로 이동
  var OLD = { dish: 'dishwasher', laundry: 'dryer', bath: 'shower-booth', restore: 'water-purifier-restore', kitchen: 'home-repair', furniture: 'door-furniture' };
  var h = location.hash.slice(1);
  if (location.pathname === '/' && h) {
    var m;
    if ((m = h.match(/^case-(\d+)$/))) location.replace('/cases/' + m[1] + '/');
    else if ((m = h.match(/^svc-(\w+)$/)) && OLD[m[1]]) location.replace('/service/' + OLD[m[1]] + '/');
    else if (/^(service|cases|process|area|contact)$/.test(h)) location.replace('/' + h + '/');
  }

  // 아이폰은 sms 본문 구분자가 & 이므로 바꿔줌
  if (/iPhone|iPad|iPod|Macintosh/.test(navigator.userAgent)) {
    d.querySelectorAll('a[data-sms]').forEach(function (a) { a.href = a.getAttribute('href').replace('?body=', '&body='); });
  }

  // 클릭 측정: 전화·문자 버튼 (애널리틱스가 연결되어 있을 때만 전송)
  function track(name, label) {
    try { if (window.gtag) gtag('event', name, { event_label: label || location.pathname }); } catch (e) {}
    try { if (window.wcs && wcs.event) wcs.event(name, label || location.pathname); } catch (e) {}
  }
  d.addEventListener('click', function (e) {
    var a = e.target.closest('[data-track]');
    if (a) track(a.getAttribute('data-track') === 'call' ? 'click_call' : 'click_sms', location.pathname);
  });

  // 헤더 그림자
  var hd = d.querySelector('header');
  function sc() { hd && hd.classList.toggle('scrolled', scrollY > 8); }
  sc(); addEventListener('scroll', sc, { passive: true });

  // 모바일 메뉴
  var dr = d.getElementById('drawer');
  if (dr) {
    var close = function () { dr.classList.remove('open'); d.body.style.overflow = ''; setTimeout(function () { dr.hidden = true; }, 280); };
    d.getElementById('burger').addEventListener('click', function () { dr.hidden = false; d.body.style.overflow = 'hidden'; requestAnimationFrame(function () { requestAnimationFrame(function () { dr.classList.add('open'); }); }); });
    d.getElementById('closer').addEventListener('click', close);
    dr.querySelectorAll('.dlist a, .dtiles a').forEach(function (a) { if (a.getAttribute('href') === location.pathname) a.setAttribute('aria-current', 'page'); });
    dr.addEventListener('click', function (e) { if (e.target.closest('a') || e.target.hasAttribute('data-close')) close(); });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !dr.hidden) close(); });
  }

  // 메인: 전후 비교 탭
  var tabs = d.getElementById('baTabs');
  if (tabs) tabs.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    tabs.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-selected', x === b ? 'true' : 'false'); });
    d.querySelectorAll('#baView [data-panel]').forEach(function (p) { p.hidden = p.getAttribute('data-panel') !== b.dataset.id; });
  });

  // 시공사례 목록: 분야 필터
  var fw = d.getElementById('filters');
  if (fw) fw.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    var f = b.dataset.f;
    fw.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    d.querySelectorAll('#allCases [data-svc]').forEach(function (c) { c.hidden = !(f === 'all' || c.dataset.svc === f); });
  });

  // 사진 크게 보기
  var links = [].slice.call(d.querySelectorAll('a[data-lb]'));
  if (links.length) {
    var lb = d.createElement('div'), i = 0;
    lb.className = 'lb'; lb.hidden = true; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); lb.setAttribute('aria-label', '사진 크게 보기');
    lb.innerHTML = '<button type="button" class="lbx" aria-label="닫기">✕</button><button type="button" class="lbp" aria-label="이전 사진">‹</button><figure><img alt=""><figcaption class="lbcap"></figcaption></figure><button type="button" class="lbn" aria-label="다음 사진">›</button>';
    d.body.appendChild(lb);
    var img = lb.querySelector('img'), cap = lb.querySelector('.lbcap');
    var show = function (k) { i = (k + links.length) % links.length; img.src = links[i].href; var al = links[i].querySelector('img').alt; img.alt = al; cap.textContent = al + '  (' + (i + 1) + ' / ' + links.length + ')'; };
    var hide = function () { lb.hidden = true; d.body.style.overflow = ''; };
    links.forEach(function (a, k) { a.addEventListener('click', function (e) { e.preventDefault(); show(k); lb.hidden = false; d.body.style.overflow = 'hidden'; }); });
    lb.addEventListener('click', function (e) {
      if (e.target.closest('.lbx') || e.target === lb) hide();
      else if (e.target.closest('.lbp')) show(i - 1);
      else if (e.target.closest('.lbn')) show(i + 1);
    });
    d.addEventListener('keydown', function (e) { if (lb.hidden) return; if (e.key === 'Escape') hide(); else if (e.key === 'ArrowLeft') show(i - 1); else if (e.key === 'ArrowRight') show(i + 1); });
  }

  // 견적 문의 폼 → 문자 앱
  var f = d.getElementById('qform');
  if (f) f.addEventListener('submit', function (e) {
    e.preventDefault();
    var g = function (id) { return (d.getElementById(id).value || '').trim(); };
    var done = d.getElementById('done');
    if (!g('f-area') || !d.getElementById('f-agree').checked) {
      done.hidden = false; done.textContent = '지역을 적고 동의에 체크해 주세요.'; return;
    }
    var body = '[굿초이스 견적 문의]\n작업 종류: ' + g('f-type') + '\n지역: ' + g('f-area') + (g('f-name') ? '\n이름: ' + g('f-name') : '') + (g('f-date') ? '\n희망 일정: ' + g('f-date') : '') + (g('f-msg') ? '\n내용: ' + g('f-msg') : '') + '\n※ 전체 사진 1장 + 문제 부위 사진 1장 첨부';
    var sep = /iPhone|iPad|iPod|Macintosh/.test(navigator.userAgent) ? '&' : '?';
    track('click_sms', 'contact_form');
    done.hidden = false; done.innerHTML = '문자 앱이 열립니다. 사진 2장을 첨부해서 보내주세요. 문자 앱이 열리지 않으면 <a href="tel:01058099275">010-5809-9275</a>로 직접 보내주세요.';
    location.href = 'sms:01058099275' + sep + 'body=' + encodeURIComponent(body);
  });

  // 부드러운 등장 (움직임 최소화 설정이면 생략)
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    d.querySelectorAll('.symgrid>a,.whogrid>a,.flowsteps>li,.posts>a,.services>*,.cgrid3>*,.princ>*,.story>li,.rgrid>*').forEach(function (el, k) {
      var r = el.getBoundingClientRect(); if (r.top < innerHeight) return;
      el.classList.add('rv'); el.style.setProperty('--d', (k % 3) * 60 + 'ms'); io.observe(el);
    });
  }
})();
