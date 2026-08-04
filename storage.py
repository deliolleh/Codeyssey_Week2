"""퀴즈와 점수를 state.json에 저장하고 불러오는 일을 맡는다.

JSON(JavaScript Object Notation)은 자료를 글자로 적어 두는 형식이다.
파이썬의 딕셔너리·리스트와 모양이 거의 같아서, 메모리에 있는 자료를
거의 그대로 파일에 적었다가 다시 읽어올 수 있다.

    파이썬  {"question": "...", "choices": ["가", "나"], "answer": 1}
    JSON    {"question": "...", "choices": ["가", "나"], "answer": 1}

다만 JSON이 담을 수 있는 것은 문자열·숫자·참거짓·리스트·딕셔너리뿐이라
Quiz 객체를 그대로 넣을 수는 없다. 그래서 저장할 때는 to_dict()로 딕셔너리를
만들고, 불러올 때는 create_quiz()로 다시 객체를 만든다.

파일을 다루는 일은 실패할 수 있다. 파일이 없을 수도, 내용이 깨졌을 수도,
권한이 없어 못 쓸 수도 있다. 어느 경우에도 프로그램이 죽지 않도록
try/except로 감싸고, 문제가 있으면 기본 퀴즈로 되돌린다.
"""

import json
from pathlib import Path

from default_data import DEFAULT_BEST_SCORE, DEFAULT_QUIZZES
from quiz import create_quiz
from user import create_user

# 저장 파일은 프로젝트 루트에 둔다.
# __file__은 이 파일의 경로이고, 그 부모 디렉터리가 곧 프로젝트 루트다.
# 현재 작업 디렉터리를 기준으로 하면 다른 폴더에서 실행했을 때
# 엉뚱한 자리에 파일이 생기므로, 이 파일의 위치를 기준으로 잡는다.
STATE_FILE = Path(__file__).resolve().parent / "state.json"

# JSON은 주석을 지원하지 않으므로, 규칙 설명을 키로 넣어 파일 맨 위에 보이게 한다.
# 앞의 밑줄은 "자료가 아니라 설명"이라는 뜻으로 붙인 관례적인 표시다.
SCHEMA_NOTE = "answer는 choices의 순번(1부터). O/X 문제는 O=1, X=2. 주관식은 허용 답안 목록."


class Storage:
    """state.json 한 개를 읽고 쓰는 담당자."""

    def __init__(self, path=STATE_FILE):
        self.path = path

    # ---------- 불러오기 ----------

    def load(self):
        """저장된 자료를 읽어 딕셔너리로 돌려준다.

        돌려주는 항목이 여럿이라 순서대로 나열하면 부르는 쪽에서 헷갈리기 쉽다.
        이름표로 꺼내 쓸 수 있게 딕셔너리로 묶고, JSON의 키 이름과 맞춰 두었다.
            quizzes / best_score / users

        파일이 없거나 망가졌으면 기본 퀴즈로 되돌린다.
        어떤 경우에도 예외를 밖으로 내보내지 않는다.
        불러오기가 실패했다고 게임을 못 하게 만들 이유가 없기 때문이다.
        """
        if not self.path.exists():
            print("📂 저장된 데이터가 없어 기본 퀴즈로 시작합니다.")
            return self.recover(quiet=True)

        try:
            with open(self.path, encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            # 파일은 있지만 JSON 형식이 깨진 경우다.
            # 중괄호가 빠졌거나 편집하다 만 상태일 수 있다.
            print(f"⚠️ {self.path.name}의 형식이 올바르지 않습니다. ({error})")
            return self.recover()
        except OSError as error:
            # 권한이 없거나 읽는 도중 문제가 생긴 경우다.
            print(f"⚠️ {self.path.name}을 읽지 못했습니다. ({error})")
            return self.recover()

        if not isinstance(data, dict):
            print(f"⚠️ {self.path.name}의 구조가 올바르지 않습니다.")
            return self.recover()

        quizzes = self.read_quizzes(data)
        best_score = self.read_best_score(data)
        users = self.read_users(data)

        summary = f"퀴즈 {len(quizzes)}개, 최고 점수 {best_score}점"
        if users:
            summary += f", 사용자 {len(users)}명"
        print(f"📂 저장된 데이터를 불러왔습니다. ({summary})")

        return {"quizzes": quizzes, "best_score": best_score, "users": users}

    def read_quizzes(self, data):
        """자료에서 퀴즈 목록을 꺼낸다. 쓸 만한 게 없으면 기본 퀴즈로 채운다."""
        raw = data.get("quizzes")
        if not isinstance(raw, list):
            print("⚠️ 퀴즈 목록을 찾을 수 없어 기본 퀴즈로 채웁니다.")
            return self.build_quizzes(DEFAULT_QUIZZES)

        quizzes = self.build_quizzes(raw)
        if not quizzes:
            print("⚠️ 사용할 수 있는 퀴즈가 하나도 없어 기본 퀴즈로 채웁니다.")
            return self.build_quizzes(DEFAULT_QUIZZES)
        return quizzes

    def read_best_score(self, data):
        """자료에서 최고 점수를 꺼낸다. 값이 이상하면 0으로 되돌린다."""
        best_score = data.get("best_score", DEFAULT_BEST_SCORE)
        # bool은 파이썬에서 int의 한 종류라 isinstance(True, int)가 참이 된다.
        # true가 점수로 들어오는 것을 막으려면 따로 걸러야 한다.
        if isinstance(best_score, bool) or not isinstance(best_score, int) or best_score < 0:
            print(f"⚠️ 최고 점수 값이 올바르지 않아 {DEFAULT_BEST_SCORE}으로 되돌립니다.")
            return DEFAULT_BEST_SCORE
        return best_score

    def read_users(self, data):
        """자료에서 사용자 목록을 꺼낸다.

        사용자 기록이 없거나 깨져 있어도 게임 자체는 할 수 있으므로,
        퀴즈와 달리 기본값으로 되돌리지 않고 빈 목록으로 시작한다.
        """
        raw = data.get("users")
        if raw is None:
            # users 키가 아예 없는 경우다.
            # 사용자 기능이 생기기 전에 만들어진 파일도 그대로 읽히게 한다.
            return []
        if not isinstance(raw, list):
            print("⚠️ 사용자 목록의 형태가 올바르지 않아 비우고 시작합니다.")
            return []

        users = []
        seen = set()
        for index, item in enumerate(raw, start=1):
            try:
                user = create_user(item)
            except ValueError as error:
                print(f"⚠️ {index}번째 사용자를 건너뜁니다: {error}")
                continue

            # 파일을 손으로 고치다 같은 이름이 두 번 들어갈 수 있다.
            # 그대로 두면 기록이 갈라지므로 먼저 온 쪽만 남긴다.
            key = user.nickname.lower()
            if key in seen:
                print(f"⚠️ 닉네임이 겹치는 사용자 '{user.nickname}'을 건너뜁니다.")
                continue
            seen.add(key)
            users.append(user)
        return users

    def build_quizzes(self, raw_list):
        """딕셔너리 목록을 Quiz 객체 목록으로 바꾼다.

        형식이 잘못된 문제는 건너뛰고 나머지는 살린다.
        한 문제가 망가졌다고 나머지 49문제까지 버릴 이유가 없다.
        """
        quizzes = []
        for index, raw in enumerate(raw_list, start=1):
            try:
                quizzes.append(create_quiz(raw))
            except (ValueError, AttributeError, TypeError) as error:
                print(f"⚠️ {index}번째 문제를 건너뜁니다: {error}")
        return quizzes

    def recover(self, quiet=False):
        """읽기에 실패했거나 파일이 없을 때 기본 상태를 돌려준다."""
        if not quiet:
            print("   기본 퀴즈로 복구합니다. 저장하면 기존 파일을 덮어씁니다.")
        return {
            "quizzes": self.build_quizzes(DEFAULT_QUIZZES),
            "best_score": DEFAULT_BEST_SCORE,
            "users": [],
        }

    # ---------- 저장하기 ----------

    def save(self, quizzes, best_score, users=()):
        """지금 상태를 state.json에 쓴다. 성공 여부를 돌려준다."""
        data = {
            "_note": SCHEMA_NOTE,
            # 퀴즈 풀기가 목록을 제자리에서 섞기 때문에, 저장할 때 id 순으로 되돌린다.
            # 이렇게 해두면 사람이 파일을 열어볼 때 순서가 늘 같고,
            # 점수만 바뀐 경우에 파일 전체가 뒤바뀌는 일도 없다.
            "quizzes": [quiz.to_dict() for quiz in sorted(quizzes, key=lambda q: q.quiz_id)],
            "best_score": best_score,
            # 사용자도 닉네임 순으로 정렬해 둔다. 접속 순서대로 쌓이면
            # 새로 접속할 때마다 파일에서 위치가 바뀌어 변경 내역이 지저분해진다.
            "users": [
                user.to_dict() for user in sorted(users, key=lambda u: u.nickname.lower())
            ],
        }

        try:
            with open(self.path, "w", encoding="utf-8") as file:
                # ensure_ascii=False 를 빼면 한글이 \uXXXX 로 저장돼 사람이 읽을 수 없다.
                # indent=2 는 줄바꿈과 들여쓰기를 넣어 보기 좋게 만든다.
                json.dump(data, file, ensure_ascii=False, indent=2)
            return True
        except OSError as error:
            print(f"⚠️ 저장하지 못했습니다. ({error})")
            return False
