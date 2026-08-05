"""연승전 한 판의 진행 상태를 담는 Round 클래스.

한 판이 진행되는 동안 따라다녀야 하는 값이 여덟 개나 된다.
점수, 연승 수, 답한 문제 수, 힌트 사용 횟수, 남은 힌트, 힌트를 쓴 문제 목록,
출제 대상, 기록의 주인. 이걸 지역 변수로 두면 메서드를 부를 때마다
필요한 것을 골라 넘겨야 하고, 값이 하나 늘 때마다 함수 시그니처가 길어진다.

    record_result(player, score, streak, answered, count, hints_used, ending)
    record_result(round)

한 덩어리로 묶으면 "이 판"이라는 하나의 대상이 생기고,
점수를 더하거나 힌트를 쓰는 규칙도 그 안에 함께 둘 수 있다.
"""

from enum import Enum

import config


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


class Round:
    """연승전 한 판."""

    def __init__(self, quizzes, player):
        self.quizzes = quizzes  # 이번 판에 출제할 문제들
        self.player = player  # 기록을 남길 사람
        self.score = 0
        self.streak = 0  # 연속으로 맞힌 수
        self.answered = 0  # 답을 제출한 문제 수
        self.hints_used = 0  # 맞혔든 틀렸든 힌트를 본 횟수
        self.hints_left = config.STARTING_HINTS
        self.hinted = []  # 힌트를 써서 맞힌 문제. 판이 끝난 뒤 복습용
        self.ending = None  # 어떻게 끝났는지. 세 갈래 중 하나로 정해진다

    @property
    def total(self):
        """이번 판에 도전한 문제 수."""
        return len(self.quizzes)

    def can_use_hint(self, quiz):
        """지금 이 문제에서 힌트를 쓸 수 있는지."""
        return self.hints_left > 0 and bool(quiz.hint)

    def spend_hint(self):
        """힌트를 하나 쓴다."""
        self.hints_left -= 1
        self.hints_used += 1

    def submit(self, quiz, raw, used_hint):
        """답을 제출한 결과를 반영하고, 맞았는지와 얻은 점수를 돌려준다."""
        self.answered += 1

        if not quiz.check(raw):
            self.ending = Ending.WRONG
            return False, 0

        point = quiz.get_point(used_hint)
        self.score += point
        self.streak += 1
        if used_hint:
            self.hinted.append(quiz)
        return True, point

    def grant_hint_if_due(self):
        """연승 보상 조건을 채웠으면 힌트를 하나 더 준다. 줬으면 True."""
        # 오답이면 그 자리에서 판이 끝나므로,
        # 연승이 끊겨서 준 힌트를 되돌려야 하는 경우는 없다.
        if self.streak > 0 and self.streak % config.HINT_REWARD_STREAK == 0:
            self.hints_left += 1
            return True
        return False

    def is_recordable(self):
        """기록으로 남길 만한 판인지.

        한 문제도 답하지 않고 나간 판은 남기지 않는다.
        시작하자마자 그만둔 것까지 쌓이면 "총 12판" 같은 숫자가 의미를 잃는다.
        """
        return self.answered > 0
