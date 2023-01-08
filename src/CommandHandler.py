import json
import os.path

from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from .UserPosition import UserPosition

main_menu_keyboard = VkKeyboard(one_time=True)
main_menu_keyboard.add_button('Заказать стикеры', color=VkKeyboardColor.POSITIVE)
main_menu_keyboard.add_button('Обратиться к администраторам', color=VkKeyboardColor.PRIMARY)

order_stickers_keyboard = VkKeyboard(one_time=True)
order_stickers_keyboard.add_button('Выбрать из товаров', color=VkKeyboardColor.POSITIVE)
order_stickers_keyboard.add_button('Собственный стикерпак', color=VkKeyboardColor.PRIMARY)
order_stickers_keyboard.add_line()
order_stickers_keyboard.add_button('Вернуться в главное меню', color=VkKeyboardColor.SECONDARY)

chose_stickers_facture_keyboard = VkKeyboard(one_time=True)
chose_stickers_facture_keyboard.add_button('Глянцевая', color=VkKeyboardColor.POSITIVE)
chose_stickers_facture_keyboard.add_button('Матовая', color=VkKeyboardColor.POSITIVE)
chose_stickers_facture_keyboard.add_button('Своя', color=VkKeyboardColor.POSITIVE)
chose_stickers_facture_keyboard.add_line()
chose_stickers_facture_keyboard.add_button('Вернуться в главное меню', VkKeyboardColor.SECONDARY)

count_strickers_keyboard = VkKeyboard(one_time=True)
count_strickers_keyboard.add_button('Вернуться в главное меню', VkKeyboardColor.SECONDARY)

chose_city_keyboard = VkKeyboard(one_time=True)
chose_city_keyboard.add_location_button()

go_back_to_menu_keyboard = VkKeyboard(one_time=True)
go_back_to_menu_keyboard.add_button('Вернуться в главное меню')

ABSPATH = os.path.abspath('CommandHandler.py').replace('CommandHandler.py', '')


def get_settings(index):
    with open('settings.json', 'r') as f:
        data = json.load(f)
    return data[index]


ADMIN_ID = get_settings('admin_id')


class CommandHandler:

    def __init__(self, vk, vk_session, group_id):
        self.vk = vk
        self.vk_session = vk_session
        self.ORDERS = {}
        self.group_id = group_id

    def send_message(self, user_id, message, keyboard=None, attachment=None):
        self.vk.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message=message,
            keyboard=keyboard,
            attachment=attachment
        )

    def get_user_pos(self, user_id):
        with open(f'{ABSPATH}/DB.json', 'r') as f:
            data = json.load(f)
        try:
            return data[str(user_id)]
        except KeyError:
            self.update_user_pos(user_id, UserPosition.START)
            with open(f'{ABSPATH}/DB.json', 'r') as f:
                data = json.load(f)
            return data[str(user_id)]

    @staticmethod
    def update_user_pos(user_id, new_pos):
        with open(f'{ABSPATH}/DB.json', 'r') as f:
            temp = json.load(f)
            temp[str(user_id)] = new_pos
        with open(f'{ABSPATH}/DB.json', 'w') as file:
            file.write(json.dumps(temp))

    def command_executor(self, user_id, message):
        user_pos = self.get_user_pos(user_id)
        if user_pos == UserPosition.START:
            self.ORDERS[user_id] = {}
            self.send_message(user_id, """Доброго времени суток!\nДавай определимся, за чем вы пришли. =)""",
                              main_menu_keyboard.get_keyboard())
            self.update_user_pos(user_id, UserPosition.MAIN_MENU)
        elif user_pos == UserPosition.MAIN_MENU:
            if message == 'заказать стикеры':
                self.send_message(user_id, 'Давайте определимся с желаемыми наклейками. =)',
                                  order_stickers_keyboard.get_keyboard())
                self.update_user_pos(user_id, UserPosition.ORDER_STICKERS)
            elif message == 'обратиться к администраторам':
                self.update_user_pos(user_id, UserPosition.CONNECT_TO_ADMIN)
                self.send_message(user_id, 'Напишите свой вопрос')
        elif user_pos == UserPosition.ORDER_STICKERS:
            self.ORDERS[user_id] = {}
            if message == 'выбрать из товаров':
                self.send_message(user_id, message='Вот наш список стикеров: ', attachment=
                f'https://vk.com/market-{self.group_id}', keyboard=order_stickers_keyboard.get_keyboard())
            elif message == 'собственный стикерпак':
                self.send_message(user_id, 'Хорошо, выберете, на которой будут печататься стикеры',
                                  chose_stickers_facture_keyboard.get_keyboard())
                self.update_user_pos(user_id, UserPosition.CHOSE_FACTURE)
            elif message in ['вернуться в главное меню', 'меню']:
                self.send_message(user_id, """Доброго времени суток!\nДавай определимся, за чем вы пришли. =)""",
                                  main_menu_keyboard.get_keyboard())
                self.update_user_pos(user_id, UserPosition.MAIN_MENU)
            else:
                self.not_matched_text(user_id)
        elif user_pos == UserPosition.CONNECT_TO_ADMIN:
            text = f"У пользователя @id{user_id} появился вопрос:\n\n{message}\n\nНужно ответить!"
            self.send_message(ADMIN_ID, text)
            self.send_message(user_id, 'Администрация скоро свяжется с вами, ожидайте',
                              main_menu_keyboard.get_keyboard())
            self.update_user_pos(user_id, UserPosition.MAIN_MENU)
        elif user_pos == UserPosition.CHOSE_FACTURE:
            if message in ['глянцевая', 'матовая']:
                self.ORDERS[user_id]['facture'] = message
                self.send_message(user_id, 'Пожалуйста, напишите, сколько стикеров вы хотите заказать')
                self.update_user_pos(user_id, UserPosition.CHOSE_AMOUNT)
            elif message == 'своя':
                self.send_message(user_id, 'Напишите, на какой бумаге вы хотите стикеры?')
                self.update_user_pos(user_id, UserPosition.CHOSE_OTHER_FACTURE)
        elif user_pos == UserPosition.CHOSE_AMOUNT:
            self.ORDERS[user_id]['amount'] = message
            self.send_message(user_id,
                              'Теперь, пожалуйста, напишите куда доставить ваши стикеры (Доставка работает по РФ)')
            self.update_user_pos(user_id, UserPosition.CHOSE_CITY)
        elif user_pos == UserPosition.CHOSE_CITY:
            self.ORDERS[user_id]['city'] = message
            self.send_message(user_id, 'Отлично! Заказ сформирован, с вами скоро свяжутся для уточнения деталей',
                              main_menu_keyboard.get_keyboard())
            self.update_user_pos(user_id, UserPosition.MAIN_MENU)
            order_message = f"""
                    Новый заказ от @id{user_id}!\n\nФактура: {self.ORDERS[user_id]['facture']}\nКол-во стикеров: {self.ORDERS[user_id]['amount']}\nКуда доставить: {self.ORDERS[user_id]['city']}\n\nСвяжитесь с покупателелем для уточнения заказа! 
                    """
            self.send_message(ADMIN_ID, order_message)
            self.ORDERS[user_id].clear()
        elif user_pos == UserPosition.CHOSE_OTHER_FACTURE:
            self.ORDERS[user_id]['facture'] = message
            self.send_message(user_id, 'Хорошо, теперь, пожалуйста, напишите, сколько стикеров вы хотите заказать')
            self.update_user_pos(user_id, UserPosition.CHOSE_AMOUNT)

    def not_matched_text(self, user_id):
        self.send_message(user_id, 'Простите, я вас не понимаю... Напишите "меню", чтобы выйти в главное меню',
                          go_back_to_menu_keyboard.get_keyboard())
