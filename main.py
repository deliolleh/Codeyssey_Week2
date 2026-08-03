"""프로그램 진입점. 실행: python main.py"""

# 이 검사보다 위에서는 3.10 이상 전용 문법을 쓰지 않는다.
# 구버전 파이썬에서 문법 오류로 죽어버리면 안내 메시지 자체를 띄울 수 없기 때문이다.
import sys

if sys.version_info < (3, 10):
    print("⚠️ 이 프로그램은 Python 3.10 이상이 필요합니다.")
    print(f"   현재 버전: {sys.version.split()[0]}")
    sys.exit(1)

from game import QuizGame
from inputs import ask_yes_no


def main():
    game = QuizGame()

    # 종료 경로가 세 가지(메뉴에서 5 선택 / Ctrl+C / 입력 종료)라서
    # 루프로 감싸두고, 마무리 인사는 루프를 빠져나온 뒤 한 번만 한다.
    while True:
        try:
            game.run()

        except KeyboardInterrupt:
            # Ctrl+C는 실수로 눌릴 수 있으므로 바로 끝내지 않고 한 번 확인한다.
            # 다만 예외가 여기까지 올라온 시점에는 run()이 이미 중단된 뒤라,
            # 계속하기를 골라도 하던 자리가 아니라 메인 메뉴부터 다시 시작한다.
            try:
                print()
                if not ask_yes_no("⚠️ 정말 종료할까요? (y/n): "):
                    print("계속합니다.")
                    continue
            except (KeyboardInterrupt, EOFError):
                # 확인하는 중에 또 Ctrl+C를 누르거나 입력이 끊기면
                # 붙잡지 않고 종료한다. 안 그러면 빠져나갈 방법이 없어진다.
                print()

        except EOFError:
            # 입력 스트림이 끝났다는 뜻이라 되물을 수단이 없다.
            # 여기서 확인을 하면 답을 받지 못한 채 무한히 반복된다.
            print("\n⚠️ 입력이 중단되었습니다.")

        break

    print("👋 안녕히 가세요!")


if __name__ == "__main__":
    main()
