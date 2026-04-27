from src.parsing import ConfigParser


def main() -> None:

    try:
        print(ConfigParser().parse('truc.json'))
    except Exception as e:
        print(f"{type(e).__name__} error occured while parsing: {e}")


if __name__ == '__main__':
    main()
