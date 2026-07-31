"""프로그램 진입점. 실행: python main.py"""

# 이 검사보다 위에서는 3.10 이상 전용 문법을 쓰지 않는다.
# 구버전 파이썬에서 문법 오류로 죽어버리면 안내 메시지 자체를 띄울 수 없기 때문이다.
import sys

if sys.version_info < (3, 10):
    print("⚠️ 이 프로그램은 Python 3.10 이상이 필요합니다.")
    print(f"   현재 버전: {sys.version.split()[0]}")
    sys.exit(1)

from game import QuizGame


def main():
    game = QuizGame()
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C 또는 입력 스트림 종료(EOF)로도 비정상 종료하지 않는다.
        print("\n\n⚠️ 입력이 중단되었습니다. 프로그램을 종료합니다.")
        print("👋 안녕히 가세요!")


if __name__ == "__main__":
    main()
