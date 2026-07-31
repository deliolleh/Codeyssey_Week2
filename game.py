"""게임 전체 흐름을 관리하는 QuizGame 클래스."""

LINE = "=" * 44
TITLE = "🗺️  대한민국 지역 퀴즈 게임  🗺️"


class QuizGame:
    """메뉴를 보여주고, 사용자가 고른 기능을 실행하는 게임 본체."""

    def __init__(self):
        self.quizzes = []
        self.best_score = 0
        self.running = True

    # ---------- 메뉴 ----------

    def show_menu(self):
        """메인 메뉴를 출력한다."""
        print()
        print(LINE)
        print(f"       {TITLE}")
        print(LINE)
        print("1. 퀴즈 풀기 (연승전)")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print(LINE)

    def select_menu(self):
        """올바른 메뉴 번호를 입력할 때까지 반복해서 묻는다."""
        while True:
            raw = input("선택: ").strip()
            if not raw:
                print("⚠️ 입력이 비어 있습니다. 1-5 사이의 숫자를 입력하세요.")
                continue
            try:
                number = int(raw)
            except ValueError:
                print("⚠️ 잘못된 입력입니다. 1-5 사이의 숫자를 입력하세요.")
                continue
            if not 1 <= number <= 5:
                print("⚠️ 잘못된 입력입니다. 1-5 사이의 숫자를 입력하세요.")
                continue
            return number

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
        print("\n👋 안녕히 가세요!")
        self.running = False
