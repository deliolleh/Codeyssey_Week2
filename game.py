"""게임 전체 흐름을 관리하는 QuizGame 클래스."""

import random

from default_data import DEFAULT_BEST_SCORE, DEFAULT_QUIZZES
from inputs import ask_int
from quiz import create_quiz

# 화면에 반복해서 쓰이는 값은 상수로 빼둔다.
# 값이 한 군데에만 있으면 디자인을 바꿀 때 한 줄만 고치면 된다.
LINE = "=" * 44
TITLE = "🗺️  대한민국 지역 퀴즈 게임  🗺️"

# 메뉴 항목은 리스트(list)로 관리한다.
# 리스트는 "순서가 있는 여러 개의 값"을 담는 자료형이고,
# 메뉴는 화면에 보여줄 순서가 곧 데이터의 순서이므로 리스트가 잘 맞는다.
# 항목을 추가하려면 이 리스트에만 넣으면 되고, 출력과 입력 허용 범위는 따라온다.
MENU_ITEMS = [
    "퀴즈 풀기 (연승전)",
    "퀴즈 추가",
    "퀴즈 목록",
    "점수 확인",
    "종료",
]


class QuizGame:
    """메뉴를 보여주고, 사용자가 고른 기능을 실행하는 게임 본체."""

    def __init__(self):
        # __init__은 객체가 만들어질 때 자동으로 한 번 실행되는 메서드다.
        # self는 "지금 만들어지고 있는 바로 그 객체"를 가리키고,
        # self.___ 형태로 붙인 값이 그 객체의 속성(attribute)이 된다.
        # 메서드 안의 지역 변수와 달리 객체가 사는 동안 계속 유지된다.
        self.quizzes = self.load_default_quizzes()  # list: Quiz 객체들
        self.best_score = DEFAULT_BEST_SCORE  # int: 최고 점수
        self.running = True  # bool: 게임 루프를 계속 돌릴지 여부

    def load_default_quizzes(self):
        """기본 퀴즈 데이터를 Quiz 객체 목록으로 바꾼다.

        형식이 잘못된 문제는 건너뛰고 나머지는 살린다.
        한 문제가 잘못됐다고 게임 전체를 못 하게 만들 이유가 없기 때문이다.
        """
        quizzes = []
        for data in DEFAULT_QUIZZES:
            try:
                quizzes.append(create_quiz(data))
            except ValueError as error:
                print(f"⚠️ {data.get('id', '?')}번 문제를 건너뜁니다: {error}")
        return quizzes

    # ---------- 메뉴 ----------

    def show_menu(self):
        """메인 메뉴를 출력한다."""
        print()
        print(LINE)
        print(f"       {TITLE}")
        print(LINE)
        # for는 반복 횟수가 이미 정해져 있을 때 쓴다.
        # 여기서는 "리스트에 든 항목 수"만큼만 돌면 되므로 for가 맞다.
        # enumerate(..., start=1)은 (번호, 값)을 함께 꺼내주므로
        # 번호를 세는 변수를 따로 만들고 1씩 더할 필요가 없다.
        for number, name in enumerate(MENU_ITEMS, start=1):
            print(f"{number}. {name}")
        print(LINE)

    def select_menu(self):
        """올바른 메뉴 번호를 입력할 때까지 되묻고, 그 번호를 반환한다."""
        # 검증 규칙은 ask_int가 전부 처리하므로 여기서는 "무엇을 묻는지"만 정한다.
        # 메뉴가 늘어나도 len(MENU_ITEMS)가 허용 범위를 자동으로 맞춰준다.
        return ask_int("선택: ", 1, len(MENU_ITEMS))

    def run(self):
        """종료를 고를 때까지 메뉴를 반복해서 보여준다."""
        while self.running:
            self.show_menu()
            choice = self.select_menu()
            if choice == 1:
                self.play()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.list_quizzes()
            elif choice == 4:
                self.show_score()
            elif choice == 5:
                self.quit()

    # ---------- 각 기능 (이후 커밋에서 구현) ----------

    # ---------- 퀴즈 풀기 (연승전) ----------

    def play(self):
        """연승전을 진행한다. 한 문제라도 틀리면 그 자리에서 끝난다."""
        if not self.quizzes:
            print("\n⚠️ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        # 목록을 그 자리에서 섞는다. 섞기용 목록을 따로 만들지 않으므로
        # 메모리를 더 쓰지 않는다. 문제는 리스트 위치가 아니라 id로 식별하므로
        # 순서가 바뀌어도 참조가 깨지지 않는다.
        # 대신 사람이 보는 자리(퀴즈 목록 화면, state.json 저장)에서는
        # id 순으로 정렬해 순서가 일정하게 유지되도록 한다.
        random.shuffle(self.quizzes)

        print()
        print(LINE)
        print(f"📝 연승전을 시작합니다! (등록된 문제 {len(self.quizzes)}개)")
        print("   한 문제라도 틀리면 그 자리에서 끝납니다.")
        print(LINE)

        score = 0
        streak = 0

        # 문제 수만큼만 돌면 되므로 for를 쓴다.
        for number, quiz in enumerate(self.quizzes, start=1):
            print()
            print("-" * 44)
            quiz.display(number)
            print()

            raw = self.ask_answer(quiz)

            if not quiz.check(raw):
                print(f"❌ 오답입니다. 정답은 '{quiz.answer_text()}'입니다.")
                self.show_result(score, streak, cleared=False)
                break

            point = quiz.get_point()
            score += point
            streak += 1
            print(f"✅ 정답입니다! (+{point}점) — 현재 {streak}연승, 총 {score}점")
        else:
            # for의 else는 break 없이 반복이 끝났을 때만 실행된다.
            # 여기서는 "한 문제도 틀리지 않고 전 문항을 통과했다"는 뜻이 된다.
            # if의 else와 뜻이 다르므로 헷갈리기 쉽지만, 종료 조건이 두 가지인
            # 연승전에서는 두 결말을 각자의 자리에 둘 수 있어 잘 맞는다.
            self.show_result(score, streak, cleared=True)

    def ask_answer(self, quiz):
        """형식에 맞는 답이 들어올 때까지 되묻고, 그 입력을 돌려준다.

        형식 오류와 오답은 다르다. 형식이 틀렸다고 게임을 끝내면 억울하므로
        여기서는 판정하지 않고 형식만 확인한다.
        무엇이 올바른 형식인지는 문제 유형마다 다르므로 Quiz 객체에게 물어본다.
        """
        while True:
            raw = input(quiz.prompt()).strip()
            if quiz.is_valid(raw):
                return raw
            print(f"⚠️ {quiz.input_guide()}")

    def show_result(self, score, streak, cleared):
        """한 판이 끝났을 때 결과를 보여주고 최고 점수를 갱신한다."""
        print()
        print(LINE)
        if cleared:
            print(f"🎉 등록된 {streak}문제를 모두 맞혔습니다!")
        else:
            print(f"💀 Game Over — {streak}연승에서 멈췄습니다.")
        print(f"🏆 획득 점수: {score}점")

        if score > self.best_score:
            print(f"🎉 새로운 최고 점수입니다! (이전 {self.best_score}점)")
            self.best_score = score
        else:
            print(f"   최고 점수: {self.best_score}점")
        print(LINE)

    def add_quiz(self):
        print("\n📌 퀴즈 추가는 아직 준비 중입니다.")

    def list_quizzes(self):
        print("\n📋 퀴즈 목록은 아직 준비 중입니다.")

    def show_score(self):
        print("\n🏆 점수 확인은 아직 준비 중입니다.")

    def quit(self):
        """게임 루프를 멈춘다."""
        # run()의 while 조건을 False로 바꾸는 방식이라,
        # 나중에 다른 메서드에서도 종료를 요청할 수 있다.
        # 마무리 인사는 main()이 한 번만 출력한다.
        # 종료 경로가 여러 개인데 각자 인사하면 메시지가 중복되기 때문이다.
        self.running = False
