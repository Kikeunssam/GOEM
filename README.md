# 전자음악수호대 (GoEM)

모둠별로 코드 진행을 정하고 채널을 나눠 전자음악을 만드는 수업용 웹앱입니다. 원화와 기획: 키큰쌤.

- 첫 화면: `index.html`
- 학생 출동 링크: `…/#student`, 혼자 연습: `…/#solo`, 지휘본부: `…/#teacher`
- 수업 자료(작전 수첩 학습지 4마디·8마디): `worksheet/`

## 실시간 저장소 (Firebase)

1. Firebase 콘솔에서 웹 앱을 등록하고 `firebaseConfig` 값을 `firebase-config.js`의 `window.GOEM_FIREBASE`에 넣습니다.
2. Firestore Database를 만들고(서울 `asia-northeast3` 권장), 규칙 탭에 `firestore.rules` 내용을 붙여 게시합니다.
3. Authentication에서 **익명** 로그인을 켭니다.
4. Authentication 설정 > 승인된 도메인에 GitHub Pages 도메인(`kikeunssam.github.io`)을 추가합니다.

지휘본부(`#teacher`)는 잠금 없이 누구나 열 수 있습니다. 학생에게는 `#student` 주소만 나눠 주세요.

## 배포 (Firebase Hosting)

주소: https://goem-82232.web.app

```
cd ~/GOEM && git pull
npx -y firebase-tools@13 deploy --only hosting --project goem-82232
```

## 다시 만들기

`index.html`은 claude.ai 아티팩트판(`src/app-vNN.html`)에서 만듭니다.

```
python3 tools/add_web.py src/app-v35.html index.html
```
