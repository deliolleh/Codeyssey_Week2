"""사용자 입력을 받고 검증하는 공통 함수 모음.

프로그램 곳곳에서 입력을 받는데, 검증 규칙을 각 자리에 복사해두면
규칙이 바뀔 때 전부 찾아 고쳐야 한다. 그래서 형태별로 한 번만 정의하고
필요한 곳에서 불러 쓴다.

    ask_int    : 정해진 범위의 숫자   (메뉴 선택, 정답 번호, 문제 수)
    ask_text   : 문자열               (문제 문장, 선택지, 유저 이름, 힌트/해설)
    ask_yes_no : 예/아니오 확인       (힌트를 볼지 물어보기 등)

여기에 없는 입력도 있다. O/X 정답이나 선택지 번호처럼 "문제 유형마다
규칙이 다른" 입력은 각 Quiz 클래스가 스스로 판단한다. 그래야 문제 유형을
추가할 때 이 파일을 건드리지 않아도 된다.

Ctrl+C(KeyboardInterrupt)와 입력 종료(EOFError)는 여기서 잡지 않는다.
여기서 잡아 되묻기를 반복하면 Ctrl+C로 빠져나갈 수 없게 되기 때문이다.
그대로 위로 올려보내 main.py가 한 번만 처리하고 안전하게 종료한다.
"""

import unicodedata

import config

# 이 임포트는 아래 코드에서 쓰이지 않지만 지우면 안 된다.
# readline이 올라와 있지 않으면 input()의 줄 편집(백스페이스, 방향키)을
# 운영체제 터미널이 대신 처리하는데, 이쪽은 UTF-8을 모르고 바이트만 센다.
# 한글은 한 글자가 3바이트라서 백스페이스를 눌러도 3분의 1씩만 지워져,
# 앞 글자들이 안 지워지고 화면도 깨진다.
# readline은 글자 단위로 지우고 전각 문자의 폭도 제대로 계산한다.
#
# 윈도우에는 이 모듈이 없다. 그쪽 콘솔은 애초에 글자 단위로 지우므로
# 없으면 없는 대로 넘어간다.
try:
    import readline  # noqa: F401
except ImportError:
    pass


def ask_int(prompt, low, high):
    """low 이상 high 이하의 정수를 입력받아 반환한다.

    매개변수(parameter)는 함수가 밖에서 받아오는 값이다.
    이 세 개를 바꿔가며 호출하면 같은 코드로 전혀 다른 질문을 처리할 수 있다.
        prompt : 화면에 보여줄 질문 문구
        low    : 허용하는 가장 작은 값
        high   : 허용하는 가장 큰 값

    반환값(return value)은 함수가 일을 마치고 돌려주는 값이다.
    이 함수는 검증을 통과한 값이 나올 때까지 반복하므로,
    반환된 값은 항상 low~high 범위 안이라고 믿고 써도 된다.
    """
    while True:
        # input()의 결과는 언제나 문자열(str)이다.
        # strip()으로 앞뒤 공백을 먼저 없애야 " 1 " 같은 입력도 처리된다.
        raw = input(prompt).strip()

        # 빈 문자열은 조건문에서 False로 취급되므로 not raw로 검사할 수 있다.
        if not raw:
            print(f"⚠️ 입력이 비어 있습니다. {low}-{high} 사이의 숫자를 입력하세요.")
            continue

        # "abc"처럼 숫자로 바꿀 수 없는 값이면 int()가 ValueError를 낸다.
        # try/except로 잡지 않으면 프로그램이 그 자리에서 죽는다.
        try:
            number = int(raw)
        except ValueError:
            print(f"⚠️ 잘못된 입력입니다. {low}-{high} 사이의 숫자를 입력하세요.")
            continue

        if not low <= number <= high:
            print(f"⚠️ {low}-{high} 범위를 벗어났습니다. 다시 입력하세요.")
            continue

        # 세 관문을 모두 통과했을 때만 여기 도달한다.
        return number


def ask_text(prompt, allow_empty=False):
    """문자열을 입력받아 앞뒤 공백을 없앤 뒤 반환한다.

        prompt      : 화면에 보여줄 질문 문구
        allow_empty : 빈 입력을 허용할지 여부

    allow_empty에는 기본값 False를 줬다. 기본값이 있으면 호출하는 쪽에서
    생략할 수 있어서, 대부분을 차지하는 "필수 입력"은 짧게 쓰고
    힌트나 해설처럼 건너뛸 수 있는 항목만 True를 넘기면 된다.

        ask_text("문제를 입력하세요: ")                     -> 비면 다시 묻는다
        ask_text("힌트 (없으면 Enter): ", allow_empty=True) -> 비면 "" 을 반환
    """
    while True:
        # 한글은 NFC와 NFD 두 방식으로 저장될 수 있어, 겉보기가 같아도
        # 다른 문자열이 된다. 붙여넣기로 NFD가 들어올 수 있으므로
        # 받는 자리에서 한 방식으로 모아 둔다.
        raw = unicodedata.normalize("NFC", input(prompt)).strip()

        if not raw:
            if allow_empty:
                # 건너뛰겠다는 의사 표시이므로 되묻지 않고 빈 문자열을 돌려준다.
                return ""
            print("⚠️ 입력이 비어 있습니다. 내용을 입력해 주세요.")
            continue

        if len(raw) > config.MAX_TEXT_LENGTH:
            print(f"⚠️ 너무 깁니다. {config.MAX_TEXT_LENGTH}자 이내로 입력해 주세요.")
            continue

        return raw


def ask_yes_no(prompt):
    """예/아니오를 입력받아 True 또는 False로 반환한다.

    입력은 문자열이지만 돌려주는 값은 참/거짓(bool)이다.
    호출하는 쪽에서 if 문에 바로 넣어 쓸 수 있게 하기 위해서다.

        if ask_yes_no("계속할까요? (y/n): "):
            ...
    """
    while True:
        # lower()로 소문자로 맞춰두면 Y와 y를 따로 검사하지 않아도 된다.
        raw = input(prompt).strip().lower()

        if raw in ("y", "yes", "ㅇ", "네"):
            return True
        if raw in ("n", "no", "ㄴ", "아니오"):
            return False

        print("⚠️ y(예) 또는 n(아니오)으로 입력해 주세요.")
