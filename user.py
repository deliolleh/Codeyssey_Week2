"""게임을 하는 사람 한 명을 표현하는 User 클래스.

최고 점수만 숫자로 남기면 "언제, 어떤 조건에서 낸 기록인지"를 알 수 없다.
같은 47점이라도 50문제에 도전해 12연승으로 낸 것과 10문제를 완주해서 낸 것은
전혀 다른 기록이다. 그래서 판이 끝날 때마다 그때의 상황을 함께 남긴다.

Quiz가 '문제 하나'를 맡듯 User는 '사람 하나'를 맡는다.
파일을 어떻게 저장하는지, 게임을 어떻게 진행하는지는 알지 못한다.
닉네임과 기록을 들고 있고, 기록을 더하는 방법만 안다.

사용자를 구분하는 값은 실명일 이유가 없어 '닉네임'이라고 부른다.
화면·코드·저장 파일이 모두 같은 단어를 쓰도록 맞췄다.
"""

import unicodedata
from datetime import datetime

import config


class User:
    """닉네임과 게임 기록을 가진 사용자."""

    def __init__(self, nickname, best_score=0, history=None):
        # 닉네임은 사용자를 구분하는 기준이므로 앞뒤 공백을 없애 통일한다.
        # " 재혁 "과 "재혁"이 다른 사람으로 취급되면 기록이 갈라진다.
        # 실명일 필요가 없어 '이름'이 아니라 '닉네임'이라고 부른다.
        # 한글은 NFC와 NFD 두 방식으로 저장될 수 있어 겉보기가 같아도
        # 다른 문자열이 된다. 한쪽으로 모아야 같은 사람으로 인식된다.
        self.nickname = unicodedata.normalize("NFC", str(nickname)).strip()
        if not self.nickname:
            raise ValueError("닉네임이 비어 있습니다.")

        self.best_score = best_score if isinstance(best_score, int) and best_score >= 0 else 0
        # history를 그대로 받지 않고 list()로 감싸는 이유는,
        # 밖에서 넘긴 리스트를 이 객체가 계속 공유하면
        # 한쪽을 고칠 때 다른 쪽까지 바뀌기 때문이다.
        self.history = list(history) if history else []

    # ---------- 기록 ----------

    def add_record(self, score, streak, total, hints_used, ending):
        """한 판의 결과를 기록에 더하고, 최고 점수를 갱신했는지 알려준다.

        시각은 이 안에서 찍는다. 부르는 쪽이 매번 현재 시각을 만들어 넘기게 하면
        깜빡하고 빠뜨리기 쉽고, 기록마다 형식이 달라질 수 있다.
        """
        self.history.append({
            "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": score,
            "streak": streak,
            "total": total,
            "hints_used": hints_used,
            "ending": ending,
        })

        # 오래된 기록부터 잘라내 파일이 끝없이 커지는 것을 막는다.
        # [-N:] 은 리스트의 뒤에서 N개만 남긴다는 뜻이다.
        if len(self.history) > config.MAX_HISTORY:
            self.history = self.history[-config.MAX_HISTORY:]

        if score > self.best_score:
            self.best_score = score
            return True
        return False

    def recent_records(self, limit=None):
        """최근 기록을 새 것부터 돌려준다."""
        if limit is None:
            limit = config.RECENT_HISTORY_COUNT
        # [::-1] 은 리스트를 뒤집는다. 기록은 뒤에 붙으므로 뒤가 최신이다.
        return self.history[::-1][:limit]

    def play_count(self):
        """지금까지 몇 판을 했는지."""
        return len(self.history)

    # ---------- 저장 ----------

    def to_dict(self):
        """JSON에 담을 수 있는 딕셔너리로 바꾼다."""
        return {
            "nickname": self.nickname,
            "best_score": self.best_score,
            "history": self.history,
        }


def create_user(data):
    """딕셔너리 하나를 User 객체로 만든다.

    형식이 잘못됐으면 ValueError를 일으켜 부르는 쪽이 판단하게 한다.
    Quiz의 create_quiz와 같은 역할이다.
    """
    if not isinstance(data, dict):
        raise ValueError("사용자 자료의 형태가 올바르지 않습니다.")

    history = data.get("history")
    if not isinstance(history, list):
        history = []

    return User(
        nickname=data.get("nickname", ""),
        best_score=data.get("best_score", 0),
        history=[record for record in history if isinstance(record, dict)],
    )
