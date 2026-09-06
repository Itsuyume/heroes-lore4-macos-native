# 영웅서기 4 macOS 네이티브 실행 패키징

WIE의 Rust 데스크톱 실행부를 Apple Silicon용으로 빌드하고, 사용자가 제공한 게임 데이터를 포함하는 독립 macOS 앱을 만든다. 게임 원본 소스를 macOS로 다시 컴파일한 이식판은 아니며, WIPI/ARM 호환 런타임을 포함하는 네이티브 실행 패키지다. WebView, 웹브라우저, 안드로이드 가상머신은 사용하지 않는다.

게임 데이터, APK, 세이브, 완성 앱은 이 저장소에 포함하지 않는다.

## 경계

- `patches/macos-native.patch`: 번들 상대 경로, 저장 디렉터리, 네이티브 창 크기와 검은 여백, 포커스 해제 시 키 해제, macOS 내장 MIDI 합성기와 효과음을 단일 오디오 출력에 연결, 유휴 CPU 대기, LGT 표준 문자열 비교 구현.
- `build.py`: WIE의 고정 리비전 체크아웃 및 패치·검증·컴파일.
- `package.py`: 로컬 게임 ZIP과 실행 파일을 `.app`으로 패키징하고 임시 서명 검증.
- 게임 엔진·CPU·그래픽 API 구현은 WIE에 유지한다.

## 빌드

macOS, Xcode Command Line Tools, Rust stable(rustfmt/clippy), Python 3 필요.

```sh
python3 build.py
python3 package.py build/wie/target/release/wie /path/to/game.zip 'dist/영웅서기 4.app' --license build/wie/LICENSE
```

`package.py`는 기존 출력 앱을 덮어쓰지 않는다. 빌드 머신에서 현재 SDK를 사용하므로 다른 macOS 버전에서의 실행은 별도 검증이 필요하다.

## 저장 데이터 처리

LGT 런타임의 표준 라이브러리 import `0x40a`가 미구현이라 저장 이름 비교가 실패했다. 해당 import를 `strncmp`로 구현해 길이 제한, NUL 종료, unsigned byte 비교와 0 길이 입력을 처리한다. 런타임의 공용 저장 코드를 특정 게임 이름에 따라 분기하지 않는다.

패키징할 때 `P/kickass`라는 배포본의 옛 초기 저장 백업은 제외한다. 게임 JAR과 리소스는 보존하고, 입력 ZIP/APK도 수정하지 않는다. 새 진행은 macOS 사용자 데이터 폴더에 기록한다.

## 조작

| 동작 | 키 |
| --- | --- |
| 이동 | 방향키 |
| 확인·공격 | Space |
| 게임 메뉴·뒤로 | Backspace |
| 1·2·3 | 1·2·3 |
| 4·5·6 | Q·W·E |
| 7·8·9 | A·S·D |
| *·0·# | Z·X·C |
| 스토리 건너뛰기 | C (#) |
| 휴대폰 왼쪽·오른쪽 소프트키 | 왼쪽·오른쪽 Shift |

저장: 게임 메뉴 → SYSTEM → 세이브. 창 닫기는 자동 저장을 보장하지 않는다.

저장 위치: `~/Library/Application Support/local.HeroesLore.HeroesLore4/`

## 기반

- WIE: https://github.com/dlunch/wie
- 고정 리비전: `91c367031624cb7f52184d72496e95d57cf363ce`
- WIE 라이선스: MIT, 앱 번들에도 원문 포함.
- 이 저장소는 비공식 개인 호환 작업이며 권리자와 관계없다.
