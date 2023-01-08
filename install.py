import json


def main():
    token = input('Введите токен группы: ')
    admin_id = input('Введите айди человека, которому будут приходить сообщения от пользователей: ')
    group_id = input('Введите айди группы: ')

    data = {
        "token": token,
        "admin_id": int(admin_id),
        "group_id": int(group_id)
    }

    with open('settings.json', 'w') as f:
        json.dump(data, f)

    with open('DB.json', 'w') as f:
        f.write('{}')

    print('Установка завершена. Чтобы запустить бота, введите python3 main.py')


if __name__ == '__main__':
    main()
