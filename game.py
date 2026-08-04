"""게임 전체 흐름을 관리하는 QuizGame 클래스."""

import random
from enum import Enum

import config
from inputs import ask_int, ask_text, ask_yes_no
from quiz import QUIZ_TYPES, create_quiz
from storage import Storage

# 화면에 반복해서 쓰이는 값은 상수로 빼둔다.
# 값이 한 군데에만 있으면 디자인을 바꿀 때 한 줄만 고치면 된다.
LINE_WIDTH = 44
LINE = "=" * LINE_WIDTH  # 화면을 크게 나누는 줄
SUB_LINE = "-" * LINE_WIDTH  # 문제와 문제 사이를 나누는 줄
TITLE = "🗺️  대한민국 지역 퀴즈 게임  🗺️"


class Ending(Enum):
    """한 판이 끝난 방식.

    정해진 몇 가지 중 하나뿐인 값은 Enum으로 두면 오타를 바로 잡아낸다.
    문자열을 그대로 쓰면 "cleard"라고 잘못 적어도 프로그램이 조용히 지나가고,
    조건문이 어긋난 채로 엉뚱한 결과가 나온다.
    Ending.CLEARD라고 쓰면 그 줄에서 AttributeError가 난다.

    괄호 안의 값은 기록 파일에 저장할 이름이다. Enum 자체는 JSON에 담을 수 없어
    저장할 때는 .value로 문자열을 꺼낸다.
    """

    CLEARED = "cleared"  # 도전한 문제를 모두 맞힘
    WRONG = "wrong"  # 틀려서 멈춤
    GAVE_UP = "gave_up"  # 진행 중에 그만둠

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

# 게임 규칙 값(힌트 개수, 점수 배수 등)은 config.py에 모여 있다.



class QuizGame:
    """메뉴를 보여주고, 사용자가 고른 기능을 실행하는 게임 본체."""

    def __init__(self, storage=None):
        # __init__은 객체가 만들어질 때 자동으로 한 번 실행되는 메서드다.
        # self는 "지금 만들어지고 있는 바로 그 객체"를 가리키고,
        # self.___ 형태로 붙인 값이 그 객체의 속성(attribute)이 된다.
        # 메서드 안의 지역 변수와 달리 객체가 사는 동안 계속 유지된다.
        #
        # storage를 밖에서 받을 수 있게 해 두면 다른 파일을 쓰게 하거나
        # 시험 삼아 임시 파일로 돌려보기가 쉬워진다.
        self.storage = storage or Storage()
        self.quizzes, self.best_score = self.storage.load()
        self.running = True  # bool: 게임 루프를 계속 돌릴지 여부

    def save(self):
        """지금 상태를 파일에 저장한다."""
        return self.storage.save(self.quizzes, self.best_score)

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
        hints_left = config.STARTING_HINTS
        hinted = []  # 힌트를 써서 맞힌 문제. 완주 후 복습용으로 모아 둔다.

        # 문제 수만큼만 돌면 되므로 for를 쓴다.
        for number, quiz in enumerate(self.quizzes, start=1):
            print()
            print(SUB_LINE)
            quiz.display(number)
            print()

            answer = self.ask_answer_or_quit(quiz, hints_left, number)
            if answer is None:
                # 그만두기를 선택했다. 지금까지 쌓은 점수와 연승은 그대로 살린다.
                self.show_result(score, streak, Ending.GAVE_UP)
                break
            raw, used_hint, hints_left = answer

            if not quiz.check(raw):
                print(f"❌ 오답입니다. 정답은 '{quiz.answer_text()}'입니다.")
                # 연승전은 오답이 곧 게임 종료라, 여기가 그 문제에 대해
                # 무언가를 배울 수 있는 마지막 기회다. 그래서 해설을 붙인다.
                quiz.show_explanation()
                self.show_result(score, streak, Ending.WRONG)
                break

            point = quiz.get_point(used_hint)
            score += point
            streak += 1
            if used_hint:
                hinted.append(quiz)
            note = " · 힌트 사용" if used_hint else ""
            print(f"✅ 정답입니다! (+{point}점{note}) — 현재 {streak}연승, 총 {score}점")

            # 5연승마다 힌트를 하나씩 더 준다. 오답이면 게임이 끝나므로
            # 연승이 끊겨서 되돌려야 하는 경우는 없다.
            if streak % config.HINT_REWARD_STREAK == 0:
                hints_left += 1
                print(f"🎁 {streak}연승 달성! 힌트 +1 (보유 {hints_left}개)")
        else:
            # for의 else는 break 없이 반복이 끝났을 때만 실행된다.
            # 여기서는 "한 문제도 틀리지 않고 전 문항을 통과했다"는 뜻이 된다.
            # if의 else와 뜻이 다르므로 헷갈리기 쉽지만, 종료 조건이 두 가지인
            # 연승전에서는 두 결말을 각자의 자리에 둘 수 있어 잘 맞는다.
            self.show_result(score, streak, Ending.CLEARED)

        # break로 빠져나와도, else를 지나 끝나도 결국 이 줄로 온다.
        # 덕분에 두 결말 모두에서 같은 복습 절차를 거치게 된다.
        self.review_hinted(hinted)

    def review_hinted(self, hinted):
        """판이 끝났을 때, 힌트를 쓴 문제만 다시 짚어 준다.

        전 문항 해설을 한 번에 쏟으면 50문항 기준 200줄이 넘어가 읽을 수가 없다.
        힌트를 썼다는 것은 확신이 없었다는 뜻이므로 그 문제만 남긴다.
        힌트를 한 번도 쓰지 않았다면 물어보지도 않는다.

        틀린 문제의 해설은 그 자리에서 이미 보여줬으므로 여기에 포함하지 않는다.
        """
        if not hinted:
            return
        if not ask_yes_no(f"\n힌트를 사용한 {len(hinted)}문제의 해설을 볼까요? (y/n): "):
            return

        for number, quiz in enumerate(hinted, start=1):
            print()
            print(f"[{number}] {quiz.question}")
            print(f"    정답: {quiz.answer_text()}")
            quiz.show_explanation()

    def ask_answer_or_quit(self, quiz, hints_left, number):
        """답을 받되, 진행 중에 Ctrl+C가 오면 그만둘지 물어본다.

        여기서 잡지 않으면 예외가 main까지 올라가면서 판이 통째로 사라지고,
        쌓아 둔 연승과 점수도 함께 날아간다. 진행 상황을 알고 있는 곳이
        play()뿐이라, 기록을 살리려면 이 층에서 받아야 한다.

        반환: (답, 힌트 사용 여부, 남은 힌트) 또는 그만두기를 고르면 None

        확인하는 도중에 다시 Ctrl+C가 오거나 입력이 끊기면 그대로 위로 올려보낸다.
        그만두겠다는 신호를 두 번 보냈으면 붙잡지 않는 것이 맞고,
        입력 스트림이 끝난 경우에는 되물어도 답을 받을 수 없기 때문이다.
        """
        while True:
            try:
                return self.ask_answer(quiz, hints_left)
            except KeyboardInterrupt:
                print()
                if ask_yes_no("⚠️ 지금까지 기록을 남기고 그만둘까요? (y/n): "):
                    return None
                # 화면이 안내 문구로 밀려났으므로 문제를 다시 띄워 준다.
                print("계속합니다.")
                print()
                quiz.display(number)
                print()

    def ask_answer(self, quiz, hints_left):
        """형식에 맞는 답이 들어올 때까지 되묻고, 그 입력을 돌려준다.

        형식 오류와 오답은 다르다. 형식이 틀렸다고 게임을 끝내면 억울하므로
        여기서는 판정하지 않고 형식만 확인한다.
        무엇이 올바른 형식인지는 문제 유형마다 다르므로 Quiz 객체에게 물어본다.

        반환값이 세 개다. 힌트를 썼는지는 점수 계산에 필요하고,
        남은 힌트 수는 다음 문제로 이어져야 하기 때문이다.
            (입력한 답, 힌트를 썼는지, 남은 힌트 수)
        """
        used_hint = False
        while True:
            can_hint = hints_left > 0 and bool(quiz.hint) and not used_hint
            guide = f" [h: 힌트 {hints_left}개]" if can_hint else ""
            raw = input(f"{quiz.prompt()}{guide}: ").strip()

            # 'h'는 힌트 요청으로 먼저 가로챈다.
            # 이 검사를 건너뛰면 주관식에서 'h'가 답으로 처리돼
            # 힌트를 보려다 오답으로 게임이 끝나 버린다.
            if raw.lower() == "h":
                if used_hint:
                    print("⚠️ 이 문제의 힌트는 이미 봤습니다.")
                elif not quiz.hint:
                    print("⚠️ 이 문제에는 힌트가 없습니다.")
                elif hints_left <= 0:
                    print("⚠️ 남은 힌트가 없습니다.")
                else:
                    used_hint, hints_left = self.use_hint(quiz, hints_left)
                continue

            if quiz.is_valid(raw):
                return raw, used_hint, hints_left
            print(f"⚠️ {quiz.input_guide()}")

    def use_hint(self, quiz, hints_left):
        """힌트를 보여줄지 확인하고, 승낙하면 보여준 뒤 결과를 돌려준다.

        점수가 얼마나 깎이는지 먼저 알려주고 묻는다.
        1점짜리 문제는 0점이 되는데, 연승을 잇는 대가로 점수를 포기하는
        선택이 되도록 의도한 것이다.
        """
        full = quiz.get_point()
        reduced = quiz.get_point(used_hint=True)
        print(f"⚠️ 힌트를 보면 이 문제는 {full}점 → {reduced}점이 되고, "
              f"남은 힌트는 {hints_left - 1}개가 됩니다.")

        if not ask_yes_no("계속할까요? (y/n): "):
            return False, hints_left

        print(f"💡 {quiz.hint}")
        return True, hints_left - 1

    def show_result(self, score, streak, ending):
        """한 판이 끝났을 때 결과를 보여주고 최고 점수를 갱신한다.

        ending은 Ending 중 하나다. 끝나는 방식이 세 가지라
        참/거짓 두 갈래로는 담을 수 없다.
        """
        print()
        print(LINE)
        if ending is Ending.CLEARED:
            print(f"🎉 등록된 {streak}문제를 모두 맞혔습니다!")
        elif ending is Ending.GAVE_UP:
            print(f"🚪 중단했습니다 — {streak}연승까지 기록됩니다.")
        else:
            print(f"💀 Game Over — {streak}연승에서 멈췄습니다.")
        print(f"🏆 획득 점수: {score}점")

        if score > self.best_score:
            print(f"🎉 새로운 최고 점수입니다! (이전 {self.best_score}점)")
            self.best_score = score
            self.save()
        else:
            print(f"   최고 점수: {self.best_score}점")
        print(LINE)

    # ---------- 퀴즈 추가 ----------

    def add_quiz(self):
        """새 퀴즈를 입력받아 목록에 추가한다."""
        print()
        print(LINE)
        print("📌 새로운 퀴즈를 추가합니다.")
        print(LINE)

        quiz_type = self.ask_quiz_type()
        question = ask_text("\n문제를 입력하세요: ")
        choices, answer = self.ask_choices_and_answer(quiz_type)
        difficulty = self.ask_difficulty()

        # 힌트와 해설은 없어도 되는 항목이라 빈 입력을 허용한다.
        hint = ask_text("힌트 (없으면 Enter): ", allow_empty=True)
        explanation = ask_text("해설 (없으면 Enter): ", allow_empty=True)

        data = {
            "id": self.next_quiz_id(),
            "type": quiz_type,
            "difficulty": difficulty,
            "question": question,
            "choices": choices,
            "answer": answer,
            "hint": hint,
            "explanation": explanation,
        }

        # 입력을 하나하나 검증했더라도 Quiz 클래스의 규칙을 마지막으로 통과시킨다.
        # 검증 기준이 두 군데로 갈라지지 않도록, 판단은 언제나 Quiz가 한다.
        try:
            quiz = create_quiz(data)
        except ValueError as error:
            print(f"\n⚠️ 퀴즈를 만들 수 없습니다: {error}")
            return

        self.quizzes.append(quiz)
        print(f"\n✅ 퀴즈가 추가되었습니다! (총 {len(self.quizzes)}문항)")
        print(f"   {quiz.TYPE_LABEL} · {quiz.difficulty_label()} · {quiz.get_point()}점 "
              f"· 정답 '{quiz.answer_text()}'")

        # 추가하자마자 저장한다. 나중에 한 번에 저장하면
        # 그 전에 프로그램이 멈췄을 때 입력한 내용이 사라진다.
        if self.save():
            print("   저장했습니다.")

    def next_quiz_id(self):
        """다음에 쓸 퀴즈 번호를 정한다.

        개수 + 1이 아니라 '가장 큰 번호 + 1'로 정한다.
        중간의 퀴즈를 지운 뒤에도 이미 쓴 번호와 겹치지 않게 하기 위해서다.
        """
        if not self.quizzes:
            return 1
        return max(quiz.quiz_id for quiz in self.quizzes) + 1

    def ask_quiz_type(self):
        """어떤 유형의 문제를 만들지 고르게 한다."""
        print("\n문제 유형을 고르세요.")
        # 유형 목록을 여기서 다시 적지 않고 QUIZ_TYPES에서 꺼내 쓴다.
        # 목록을 복사해 두면 유형을 추가할 때 quiz.py와 이 파일을 모두 고쳐야 하고,
        # 한쪽을 놓치면 화면마다 다른 이름이 나온다.
        types = list(QUIZ_TYPES.items())
        for number, (_, quiz_class) in enumerate(types, start=1):
            print(f"  {number}. {quiz_class.TYPE_LABEL} — {quiz_class.TYPE_HELP}")

        picked = ask_int("유형 선택: ", 1, len(types))
        return types[picked - 1][0]

    def ask_choices_and_answer(self, quiz_type):
        """유형에 따라 선택지와 정답을 입력받는다.

        유형마다 물어볼 내용이 달라서 분기가 필요하다.
        반환값의 모양은 셋 다 같게 맞춰 두어, 부르는 쪽은 신경 쓰지 않아도 된다.
            (선택지 목록, 정답)
        """
        if quiz_type == "ox":
            # O/X도 선택지를 갖는다. answer가 '선택지의 몇 번째'라는 규칙을
            # 다른 유형과 똑같이 유지하기 위해서다. (O=1, X=2)
            print("\n  1. O")
            print("  2. X")
            return ["O", "X"], ask_int("정답 선택 (1-2): ", 1, 2)

        if quiz_type == "short":
            # 표기가 여러 가지인 답이 많다. (무안 / 무안군)
            # 띄어쓰기와 대소문자는 채점할 때 알아서 무시되므로 등록할 필요가 없다.
            answers = [ask_text("정답을 입력하세요: ")]
            while ask_yes_no("다른 표기도 정답으로 인정할까요? (y/n): "):
                answers.append(ask_text(f"추가 정답 {len(answers) + 1}: "))
            return [], answers

        count = ask_int(
            f"\n선택지 개수 ({config.MIN_CHOICES}-{config.MAX_CHOICES}): ",
            config.MIN_CHOICES, config.MAX_CHOICES,
        )
        choices = []
        for number in range(1, count + 1):
            choices.append(ask_text(f"  선택지 {number}: "))
        return choices, ask_int(f"정답 번호 (1-{count}): ", 1, count)

    def ask_difficulty(self):
        """난이도를 고르게 한다."""
        print("\n난이도를 고르세요.")
        levels = list(config.DIFFICULTY_WEIGHT)
        for number, level in enumerate(levels, start=1):
            print(f"  {number}. {config.DIFFICULTY_LABEL[level]} "
                  f"(점수 {config.DIFFICULTY_WEIGHT[level]}배)")

        picked = ask_int("난이도 선택: ", 1, len(levels))
        return levels[picked - 1]

    # ---------- 퀴즈 목록 ----------

    def list_quizzes(self):
        """등록된 퀴즈를 번호 순으로 훑어볼 수 있게 보여준다.

        정답은 일부러 보여주지 않는다. 목록에서 답이 보이면
        퀴즈를 풀 이유가 사라지기 때문이다.
        """
        if not self.quizzes:
            print("\n⚠️ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        print()
        print(LINE)
        print(f"📋 등록된 퀴즈 (총 {len(self.quizzes)}문항)")
        print(LINE)

        # 퀴즈 풀기가 목록을 제자리에서 섞기 때문에, 볼 때마다 순서가 달라진다.
        # 번호 순으로 정렬해 보여줘야 어제 본 목록과 오늘 본 목록이 같아진다.
        for quiz in sorted(self.quizzes, key=lambda q: q.quiz_id):
            # 칸을 맞추지 않고 · 로 구분한다. 공백으로 채워 정렬하면
            # 한글을 영문의 두 배 폭으로 그리지 않는 폰트에서 줄이 어긋난다.
            # 문제 문장도 자르지 않는다. 정렬을 하지 않으니 줄이 넘어가도
            # 다음 줄과 어긋날 일이 없고, 잘라 놓으면 무엇을 묻는지 알 수 없다.
            print(f"[{quiz.quiz_id:>3}] {quiz.TYPE_LABEL} · {quiz.difficulty_label()} · "
                  f"{quiz.get_point()}점 · {quiz.question}")

        print(LINE)
        self.show_quiz_summary()

    def show_quiz_summary(self):
        """유형과 난이도가 어떻게 분포돼 있는지 한 줄로 요약한다."""
        types = {}
        levels = {}
        for quiz in self.quizzes:
            # dict.get(키, 기본값)은 키가 없을 때 기본값을 돌려준다.
            # 덕분에 "처음 보는 유형인가"를 따로 확인하지 않아도 된다.
            types[quiz.TYPE_LABEL] = types.get(quiz.TYPE_LABEL, 0) + 1
            levels[quiz.difficulty_label()] = levels.get(quiz.difficulty_label(), 0) + 1

        print("유형   " + " · ".join(f"{name} {count}" for name, count in types.items()))
        print("난이도 " + " · ".join(f"{name} {count}" for name, count in levels.items()))
        print(f"전 문항 정답 시 {sum(quiz.get_point() for quiz in self.quizzes)}점")

    # ---------- 점수 확인 ----------

    def show_score(self):
        """최고 점수와 점수 계산 방식을 보여준다."""
        print()
        print(LINE)
        print("🏆 점수 확인")
        print(LINE)

        if self.best_score <= 0:
            # 최고 점수가 0이면 아직 한 판도 마치지 않았다고 본다.
            print("아직 퀴즈를 푼 기록이 없습니다.")
            print("메뉴에서 '퀴즈 풀기'를 골라 도전해 보세요.")
            print(LINE)
            return

        print(f"최고 점수: {self.best_score}점")

        total = sum(quiz.get_point() for quiz in self.quizzes)
        if total > 0:
            achieved = self.best_score / total * 100
            print(f"등록된 {len(self.quizzes)}문항을 전부 맞히면 {total}점 "
                  f"(현재 {achieved:.1f}% 달성)")

        print()
        self.show_score_rule()
        print(LINE)

    def show_score_rule(self):
        """점수가 어떻게 매겨지는지 설명한다.

        연승전은 문제 수가 아니라 가중치 합계로 점수를 내기 때문에,
        '몇 문제 맞혔는지'만으로는 점수를 짐작할 수 없다.
        규칙을 config에서 그대로 읽어 오므로 설정을 바꾸면 설명도 함께 바뀐다.
        """
        print("점수 = 유형 기본점 × 난이도 배수 (힌트를 쓰면 절반, 내림)")

        # 유형 이름도 QUIZ_TYPES에서 꺼낸다.
        types = " · ".join(
            f"{QUIZ_TYPES[key].TYPE_LABEL} {point}점"
            for key, point in config.TYPE_BASE_POINT.items()
        )
        levels = " · ".join(
            f"{config.DIFFICULTY_LABEL[key]} ×{weight}"
            for key, weight in config.DIFFICULTY_WEIGHT.items()
        )
        print(f"  유형   {types}")
        print(f"  난이도 {levels}")

    def quit(self):
        """게임 루프를 멈춘다."""
        # run()의 while 조건을 False로 바꾸는 방식이라,
        # 나중에 다른 메서드에서도 종료를 요청할 수 있다.
        # 마무리 인사는 main()이 한 번만 출력한다.
        # 종료 경로가 여러 개인데 각자 인사하면 메시지가 중복되기 때문이다.
        self.running = False
