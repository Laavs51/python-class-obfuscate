import techniques


def main():
    with open('../tests/source.py', encoding='utf-8') as file:
        code = file.read()

    obfuscated = techniques.obfuscate(code)

    with open('../tests/result.py', 'w', encoding='utf-8') as file:
        file.write(obfuscated)


if __name__ == '__main__':
    main()
