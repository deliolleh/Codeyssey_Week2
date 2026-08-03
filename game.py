"""게임 전체 흐름을 관리하는 QuizGame 클래스."""

from inputs import ask_int

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
        self.quizzes = []  # list: 퀴즈 객체들을 순서대로 담을 자리
        self.best_score = 0  # int: 최고 점수
        self.running = True  # bool: 게임 루프를 계속 돌릴지 여부

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

    def play(self):
        print("\n📝 퀴즈 풀기는 아직 준비 중입니다.")

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
