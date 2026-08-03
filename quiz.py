"""퀴즈 한 문제를 표현하는 클래스들.

문제 유형마다 답하는 방식이 다르다.
    선택형   : 선택지 중 몇 번째인지 번호로 답한다
    O/X     : O 또는 X로 답한다
    주관식   : 정답을 직접 입력한다

공통된 부분(문제 문장, 난이도, 힌트, 점수 계산)은 Quiz 클래스에 한 번만 두고,
유형마다 달라지는 부분(화면 출력, 입력 검증, 정답 비교)만 하위 클래스에서 덮어쓴다.
이렇게 해두면 나중에 새 유형을 추가할 때 클래스 하나만 만들면 되고,
게임 진행 코드(QuizGame)는 손대지 않아도 된다.

정답 표현 규칙
    선택형·O/X : answer는 choices의 순번(1부터). O/X는 choices가 ["O", "X"]이므로 O=1, X=2.
    주관식      : answer는 허용 답안들을 담은 리스트.
"""

# 선택지 개수의 허용 범위. 2개 미만은 문제가 성립하지 않고,
# 너무 많으면 터미널 화면에서 한눈에 읽기 어렵다.
MIN_CHOICES = 2
MAX_CHOICES = 6


def normalize(text):
    """비교하기 좋게 문자열을 다듬는다.

    주관식 채점에서 띄어쓰기나 대소문자 차이 때문에 틀리는 것을 막는다.
        " 서울 특별시 "  ->  "서울특별시"
        "Seoul"        ->  "seoul"
    맞춤법 오타까지 봐주지는 않는다. 비슷한 답을 정답으로 인정하면
    연승 기록을 믿을 수 없게 되므로, 허용 답안은 문제를 만들 때 직접 등록한다.
    """
    return text.strip().lower().replace(" ", "")


class Quiz:
    """모든 문제 유형의 공통 뼈대."""

    # 클래스 속성. self가 아니라 클래스에 붙어 있어서 모든 객체가 함께 쓴다.
    # 하위 클래스에서 같은 이름을 다시 정의하면 그 값이 우선한다.
    TYPE = "base"
    TYPE_LABEL = "기본"
    BASE_POINT = 1

    # 난이도 배수를 담은 딕셔너리(dict).
    # 리스트가 "순서로 꺼내는" 자료형이라면, 딕셔너리는 "이름표로 꺼내는" 자료형이다.
    # WEIGHT[2]가 아니라 WEIGHT["hard"]라고 쓸 수 있어서 코드가 읽힌다.
    WEIGHT = {"easy": 1, "normal": 2, "hard": 3}
    DIFFICULTY_LABEL = {"easy": "쉬움", "normal": "보통", "hard": "어려움"}

    def __init__(self, question, choices, answer,
                 difficulty="normal", hint="", explanation="", quiz_id=0):
        # --- 복구할 수 없는 오류는 여기서 막는다 ---
        # 문제 문장이 없으면 출제 자체가 불가능하다.
        # ValueError를 일으키면 이 퀴즈를 만들려던 쪽(Storage)이 받아서
        # "이 문제만 건너뛰기"로 처리할 수 있다.
        if not question or not str(question).strip():
            raise ValueError("문제 문장이 비어 있습니다.")

        # --- 복구할 수 있는 오류는 알려주고 고쳐 쓴다 ---
        # state.json은 사람이 직접 열어 고칠 수 있는 파일이라
        # "어려움"이나 "Hard" 같은 값이 들어올 수 있다.
        # 여기서 한 번 걸러두면 이후 모든 코드는 difficulty가 정상이라고 믿어도 된다.
        if difficulty not in self.WEIGHT:
            print(f"⚠️ 알 수 없는 난이도 '{difficulty}' → 'normal'로 처리합니다. "
                  f"(사용 가능: {', '.join(self.WEIGHT)})")
            difficulty = "normal"

        self.quiz_id = quiz_id
        self.question = str(question).strip()
        self.choices = list(choices) if choices else []
        self.answer = answer
        self.difficulty = difficulty
        self.hint = str(hint).strip()
        self.explanation = str(explanation).strip()

    # ---------- 점수 ----------

    def get_point(self, used_hint=False):
        """이 문제를 맞혔을 때 얻는 점수를 계산한다.

        self.BASE_POINT라고 쓰면 파이썬은 '이 객체의 실제 클래스'에서 값을 찾는다.
        그래서 이 메서드 한 벌이 유형마다 다른 점수를 만들어낸다.
        힌트를 쓰면 절반(내림)이므로 1점짜리는 0점이 되는데, 의도된 동작이다.
        연승을 잇는 대가로 점수를 포기하는 선택이 되도록 한 것이다.
        """
        point = self.BASE_POINT * self.WEIGHT[self.difficulty]
        if used_hint:
            return point // 2
        return point

    def difficulty_label(self):
        """난이도를 화면에 보여줄 한글 이름으로 바꾼다."""
        return self.DIFFICULTY_LABEL[self.difficulty]

    # ---------- 화면 출력 ----------

    def display(self, number):
        """문제를 화면에 출력한다. number는 이번 판에서 몇 번째로 나온 문제인지."""
        print(f"[문제 {number}] ({self.TYPE_LABEL} · {self.difficulty_label()} · {self.get_point()}점)")
        print(self.question)

    def prompt(self):
        """정답을 입력받을 때 보여줄 문구."""
        return "정답 입력: "

    def input_guide(self):
        """입력이 형식에 맞지 않을 때 보여줄 안내 문구."""
        return "정답을 입력해 주세요."

    def answer_text(self):
        """정답을 사람이 읽는 형태로 돌려준다."""
        return str(self.answer)

    def show_explanation(self):
        """해설을 출력한다. 해설이 없는 문제도 있으므로 있을 때만 보여준다.

        정답 판정(check)과 분리해 둔 이유는, 오답일 때뿐 아니라
        게임이 끝난 뒤 '전체 해설 보기'에서도 같은 코드를 쓰기 위해서다.
        """
        if self.explanation:
            print(f"💡 {self.explanation}")

    # ---------- 정답 확인 ----------

    def is_valid(self, raw):
        """입력이 이 유형에서 답으로 받아들일 수 있는 형식인지 확인한다.

        형식이 틀린 것과 답이 틀린 것은 다르다.
        연승전에서 형식 오류를 오답으로 처리해 게임을 끝내면 억울하므로,
        형식이 틀리면 오답 판정 없이 다시 입력받는다.
        """
        return bool(raw.strip())

    def check(self, raw):
        """입력이 정답인지 판정해 True/False를 돌려준다."""
        raise NotImplementedError

    # ---------- 저장 ----------

    def to_dict(self):
        """JSON에 저장할 수 있도록 딕셔너리로 바꾼다.

        JSON은 문자열·숫자·참거짓·리스트·딕셔너리만 담을 수 있고
        파이썬 객체는 그대로 넣을 수 없다. 그래서 저장 직전에 이 형태로 바꾼다.
        """
        return {
            "id": self.quiz_id,
            "type": self.TYPE,
            "difficulty": self.difficulty,
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
            "explanation": self.explanation,
        }


class ChoiceQuiz(Quiz):
    """선택지 여러 개 중 하나를 번호로 고르는 문제."""

    TYPE = "choice"
    TYPE_LABEL = "선택형"
    BASE_POINT = 2

    def __init__(self, question, choices, answer, **kwargs):
        super().__init__(question, choices, answer, **kwargs)

        # 선택지 개수와 정답 번호는 문제의 뼈대라, 잘못되면 출제할 수 없다.
        # 난이도와 달리 임의로 고쳐 쓸 수 없으므로 오류를 일으켜 건너뛰게 한다.
        if not MIN_CHOICES <= len(self.choices) <= MAX_CHOICES:
            raise ValueError(
                f"선택지는 {MIN_CHOICES}~{MAX_CHOICES}개여야 합니다. "
                f"(현재 {len(self.choices)}개)"
            )
        if not isinstance(self.answer, int) or not 1 <= self.answer <= len(self.choices):
            raise ValueError(
                f"정답 번호는 1~{len(self.choices)} 사이여야 합니다. (현재 {self.answer!r})"
            )

    def display(self, number):
        # 베이스 클래스가 하던 일(머리말 + 문제 문장)을 그대로 쓰고,
        # 이 유형에만 필요한 선택지 출력을 뒤에 덧붙인다.
        super().display(number)
        print()
        for index, choice in enumerate(self.choices, start=1):
            print(f"  {index}. {choice}")

    def prompt(self):
        return f"정답 입력 (1-{len(self.choices)}): "

    def input_guide(self):
        return f"1-{len(self.choices)} 사이의 숫자를 입력하세요."

    def is_valid(self, raw):
        raw = raw.strip()
        # isdigit()으로 먼저 걸러야 "-1"이나 "3.5" 같은 입력에서 예외가 나지 않는다.
        if not raw.isdigit():
            return False
        return 1 <= int(raw) <= len(self.choices)

    def check(self, raw):
        return int(raw.strip()) == self.answer

    def answer_text(self):
        # answer가 '몇 번째'인지를 가리키므로 1을 빼야 리스트 위치가 된다.
        return self.choices[self.answer - 1]


class OXQuiz(Quiz):
    """O 또는 X로 답하는 문제. 선택지가 2개인 특수한 경우다."""

    TYPE = "ox"
    TYPE_LABEL = "O/X"
    BASE_POINT = 1

    def __init__(self, question, choices=None, answer=1, **kwargs):
        # O/X는 선택지가 항상 같으므로 값이 없거나 이상하면 채워 넣는다.
        # 그래도 choices를 저장해 두는 이유는 answer가 '순번'이라는 규칙을
        # 다른 유형과 똑같이 유지하기 위해서다. answer 1 -> choices[0] -> "O".
        if not choices or len(choices) != 2:
            choices = ["O", "X"]
        super().__init__(question, choices, answer, **kwargs)

        if self.answer not in (1, 2):
            raise ValueError(f"O/X 문제의 정답은 1(O) 또는 2(X)여야 합니다. (현재 {self.answer!r})")

    def display(self, number):
        # 답을 O/X로 받으므로 "1. O  2. X"를 보여주면 오히려 헷갈린다.
        # 그래서 선택지는 출력하지 않고 문제 문장만 보여준다.
        super().display(number)

    def prompt(self):
        return "정답 입력 (O/X): "

    def input_guide(self):
        return "O 또는 X를 입력하세요."

    def is_valid(self, raw):
        return normalize(raw) in ("o", "x")

    def check(self, raw):
        # 입력한 글자를 순번으로 바꿔서 answer와 비교한다.
        entered = 1 if normalize(raw) == "o" else 2
        return entered == self.answer

    def answer_text(self):
        return self.choices[self.answer - 1]


class ShortAnswerQuiz(Quiz):
    """정답을 직접 입력하는 주관식 문제."""

    TYPE = "short"
    TYPE_LABEL = "주관식"
    BASE_POINT = 3

    def __init__(self, question, choices=None, answer=None, **kwargs):
        # 주관식은 고를 선택지가 없다.
        super().__init__(question, [], answer, **kwargs)

        # 허용 답안은 여러 개일 수 있으므로 리스트로 다룬다.
        # 손으로 편집하다 문자열 하나만 적어두는 경우가 흔해서 리스트로 감싸준다.
        if isinstance(self.answer, str):
            self.answer = [self.answer]
        if not self.answer or not isinstance(self.answer, list):
            raise ValueError("주관식 문제에는 허용 답안 목록이 필요합니다.")

        self.answer = [str(a).strip() for a in self.answer if str(a).strip()]
        if not self.answer:
            raise ValueError("주관식 문제의 허용 답안이 모두 비어 있습니다.")

    def prompt(self):
        return "정답 입력: "

    def input_guide(self):
        return "정답을 입력해 주세요."

    def check(self, raw):
        # 입력과 허용 답안을 같은 방식으로 다듬은 뒤 비교한다.
        # in 연산자는 리스트 안에 같은 값이 있는지 확인해 True/False를 준다.
        return normalize(raw) in [normalize(a) for a in self.answer]

    def answer_text(self):
        # 여러 답안 중 첫 번째를 대표 정답으로 보여준다.
        return self.answer[0]


# 유형 이름과 클래스를 짝지어 둔 딕셔너리.
# if/elif를 길게 늘어놓는 대신 이름표로 바로 꺼낼 수 있고,
# 새 유형을 추가할 때 이 표에 한 줄만 넣으면 된다.
QUIZ_TYPES = {
    ChoiceQuiz.TYPE: ChoiceQuiz,
    OXQuiz.TYPE: OXQuiz,
    ShortAnswerQuiz.TYPE: ShortAnswerQuiz,
}


def create_quiz(data):
    """딕셔너리 한 개를 알맞은 Quiz 객체로 만들어 돌려준다.

    JSON에서 읽은 자료는 전부 딕셔너리 형태라, 이를 객체로 바꿔주는 통로가 필요하다.
    형식이 잘못됐으면 ValueError를 일으켜 부르는 쪽이 판단하게 한다.
    """
    quiz_type = data.get("type", ChoiceQuiz.TYPE)
    if quiz_type not in QUIZ_TYPES:
        raise ValueError(f"알 수 없는 문제 유형입니다: {quiz_type!r}")

    quiz_class = QUIZ_TYPES[quiz_type]
    return quiz_class(
        question=data.get("question", ""),
        choices=data.get("choices"),
        answer=data.get("answer"),
        difficulty=data.get("difficulty", "normal"),
        hint=data.get("hint", ""),
        explanation=data.get("explanation", ""),
        quiz_id=data.get("id", 0),
    )
