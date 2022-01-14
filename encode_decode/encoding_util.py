import base64

if __name__ == '__main__':
    print('Enter encoded text:')
    encoded_texts = []
    while True:
        data = input()
        if data.upper() in ('STOP', 'EXIT', '', '\n'):
            break
        encoded_texts.append(data)

    for encoded_text in encoded_texts:
        print(encoded_text, '::'.join(map(lambda _: base64.b64decode(_).decode('utf-8'), encoded_text.split('::'))))
