import pygame

from inventory import Item
from room import Room, RoomObject
from ui import apply_ui
from utils import load_image
from typing import Tuple, Union
from pygame.surface import SurfaceType


class QuestRoom(Room):
    """Основная комната"""

    def __init__(self):
        """Создание комнаты"""

        super().__init__()

        # Применение интерфейса к комнате
        apply_ui(self)

        # Добавление тестовых объектов
        self.apply_objects()

    def apply_objects(self):
        """Добавление объектов"""

        # Загружаем картинки
        paper_image = load_image("paper.png")
        paper_image = pygame.transform.scale(paper_image, (24, 24))

        tea_image = load_image("tea.png")
        tea_image = pygame.transform.scale(tea_image, (100, 67))

        cup_image = load_image("cup.png")
        cup_image = pygame.transform.scale(cup_image, (100, 72))

        book1_image = load_image("alyonka.png")
        book1_image = pygame.transform.scale(book1_image, (25, 67))

        book2_image = load_image("alyonka.png")
        book2_image = pygame.transform.scale(book2_image, (50, 70))

        book3_image = load_image("alyonka.png")
        book3_image = pygame.transform.scale(book3_image, (33, 65))

        solved_book_image = load_image("alyonka_solved.png")
        solved_book_image = pygame.transform.scale(solved_book_image, (150, 80))

        matryoshka_top_image = load_image("matryoshka_top.png")
        matryoshka_top_image = pygame.transform.scale(matryoshka_top_image, (32, 32))

        matryoshka_bottom_image = load_image("matryoshka_bottom.png")
        matryoshka_bottom_image = pygame.transform.scale(matryoshka_bottom_image, (32, 32))

        # Создаем объект чая и привязываем к нему функцию по клику
        tea_object = RoomObject(tea_image, (400, 320))
        tea_object.click_hook = self.click_tea

        # Создаем кусочек картинки 3
        paper_piece3 = RoomObject(pygame.transform.rotate(paper_image, 90), (720, 220))
        paper_piece3.update_hook = self.update_piece
        paper_piece3.click_hook = self.get_piece_click_handler(3)

        # Добавляем объекты в комнату на стену 0 (переднюю)
        self.add_objects(tea_object, paper_piece3, wall=0)

        # Создаем кусочек картинки 4
        paper_piece4 = RoomObject(pygame.transform.rotate(paper_image, 90), (100, 400))
        paper_piece4.update_hook = self.update_piece
        paper_piece4.click_hook = self.get_piece_click_handler(4)

        # Добавляем объекты в комнату на стену 1 (правую)
        self.add_objects(paper_piece4, wall=1)

        # Создаем лампу
        lamp = RoomObject(load_image("lamp_off.png"), (400, 300))
        lamp.click_hook = self.click_lamp

        # Добавляем объекты на стену 2 по часовой стрелке (заднюю)
        self.add_objects(lamp, wall=2)

        # Создаем объект чашки и привязываем к нему функцию по клику
        cup_object = RoomObject(cup_image, (400, 370))
        cup_object.click_hook = self.click_cup

        # Создаем объект книг
        book_puzzle = BookPuzzle([
            (1, book1_image),
            (2, book2_image),
            (0, book3_image),
        ], solved_book_image, (260, 280))

        # Создаем объекты матрешки
        matryoshka_top = RoomObject(matryoshka_top_image, (400, 185))
        matryoshka_bottom = RoomObject(matryoshka_bottom_image, (400, 185 + matryoshka_top_image.get_height()))
        paper_piece2 = RoomObject(paper_image, (400, 200))

        matryoshka_top.click_hook = self.click_matryoshka_top
        matryoshka_top.update_hook = self.update_matryoshka_top
        paper_piece2.update_hook = self.update_piece
        paper_piece2.click_hook = self.get_piece_click_handler(2)

        self.add_objects(cup_object, book_puzzle, paper_piece2, matryoshka_top, matryoshka_bottom, wall=3)

    def click_tea(self, obj, *_):
        """Обработчик клика по чаю"""

        # Проверяем брали ли мы уже чай
        if 'used' in obj.storage:
            # Если да, то ничего не делаем
            return

        # Добавляем чай в инвентарь
        self.inventory.add(Item("tea", "Чай", load_image("tea.png")))

        # Удаляем картинку чая
        obj.image = pygame.Surface((0, 0))

        # Добавляем в хранилище объекта информацию о том, что чай уже брали
        obj.storage['used'] = True

    def click_cup(self, obj, *_):
        """Обработчик клика по чашке"""

        # Проверяем выделен ли какой-то предмет в инвентаре и является ли он чаем
        if self.inventory.get_selected() is not None and self.inventory.get_selected().uid == "tea":
            # Если да, то удаляем чай из инвентаря
            self.inventory.remove_selected()
            print("Чай налит в чашку")
            # И сохраняем информацию о том, что чай налит в чашку
            obj.storage['has_tea'] = True

    def click_lamp(self, obj, pos):
        """Обработчик клика по лампе"""

        # Сохраняем в переменную информацию о том, была ли лампа включена
        lamp_on = 'on' in obj.storage and obj.storage['on']

        # Если мы нажали на верёвку лампы, то включаем/выключаем лампу
        if 415 < pos[0] < 425 and 315 < pos[1] < 335:
            if lamp_on:
                obj.image = load_image("lamp_off.png")
                obj.storage['on'] = False
            else:
                obj.image = load_image("lamp_on_empty.png" if 'piece_taken' in obj.storage else "lamp_on.png")
                obj.storage['on'] = True

        # Если лампа включена и был нажат кусок картинки, то берём его
        if lamp_on and 'piece_taken' not in obj.storage and 400 < pos[0] < 430 and 300 < pos[1] < 315:
            self.inventory.add(Item("piece_1", "Кусочек картинки", load_image("paper.png")))
            obj.storage['piece_taken'] = True
            obj.image = load_image("lamp_on_empty.png")

    def click_matryoshka_top(self, obj, *_):
        """Обработчик клика по верхней части матрёшки"""

        # Если верхняя часть матрёшки открыта, то ничего не делаем
        if 'opened' in obj.storage:
            return

        # Добавляем в хранилище объекта информацию о том, что матрёшка начала открытие
        obj.storage['opened'] = False

    def update_matryoshka_top(self, obj, dt):
        """Обновление верхней части матрёшки"""

        if 'opened' in obj.storage:
            y_target = 100

            # Если анимация не началась, начинаем её
            if not obj.storage['opened']:
                obj.rect.y -= 10
            else:
                obj.image = pygame.Surface((0, 0))

            # Если верхняя часть матрёшки достигла цели, то сохраняем информацию о том, что она открыта
            if obj.rect.y <= y_target:
                obj.storage['opened'] = True

    def get_piece_click_handler(self, piece: int):
        """Возвращает обработчик клика по куску картинки"""

        def click_piece(obj, *_):
            # Если кусок картинки взят, то ничего не делаем
            if 'taken' in obj.storage:
                return

            # Добавляем в хранилище объекта информацию о том, что кусок картинки взят
            obj.storage['taken'] = True

            # Добавляем кусок картинки в инвентарь
            self.inventory.add(Item(f"piece_{piece}", "Кусочек картинки", load_image("paper.png")))

        return click_piece

    def update_piece(self, obj, dt):
        """Обновление куска картинки"""

        # Если кусок картинки брали, то удаляем его
        if 'taken' in obj.storage:
            obj.image = pygame.Surface((0, 0))


class BookPuzzle(RoomObject):
    """Головоломка с книгами"""

    def __init__(
            self,
            books: list[Tuple[int, Union[pygame.Surface, SurfaceType]]],
            solved_image: pygame.Surface, pos: Tuple[int, int]
    ):
        """Создание объекта"""

        # Находим ширину и высоту объекта
        width = sum(book[1].get_width() for book in books)
        height = max(book[1].get_height() for book in books)

        super().__init__(pygame.Surface((width, height), pygame.SRCALPHA, 32), pos)

        # Инициализируем книги
        x = 0
        self.books = pygame.sprite.Group()
        for book in books:
            # Создаём спрайт книги
            book_sprite = pygame.sprite.Sprite()
            book_sprite.right_x = book[0]
            book_sprite.image = book[1]
            book_sprite.rect = book_sprite.image.get_rect()
            book_sprite.rect.x = x
            book_sprite.rect.y = self.rect.height - book_sprite.rect.height

            # Добавляем книгу в группу
            self.books.add(book_sprite)
            x += book_sprite.rect.width

        # Сохраняем информацию о том, что книги не перемещались
        self.grabbed_book = None
        self.grabbed_book_offset = None

        # Сохраняем изображение, которое будет отображаться, когда книги будут расставлены правильно
        self.solved_image = solved_image

    def get_book_key(self, book: pygame.sprite.Sprite):
        """Получение ключа книги для сортировки"""

        if book is self.grabbed_book:
            return pygame.mouse.get_pos()[0] - self.rect.x - self.grabbed_book_offset
        return book.rect.x

    def update(self, delta_time: float):
        # Если головоломка не решена, то обрабатываем перемещение книг
        if 'solved' not in self.storage or not self.storage['solved']:
            self.handle_drag()
            sorted_books = sorted(self.books, key=self.get_book_key)

            # Проверяем стоят ли книги на своих местах
            if all(book.right_x == i for i, book in enumerate(sorted_books)):
                self.storage['solved'] = True
                self.grabbed_book = None
                self.grabbed_book_offset = None
                sorted_books[0].image = self.solved_image

            # Обновляем позиции книг на основе их порядка
            x = 0
            for book in sorted_books:
                if book != self.grabbed_book:
                    book.rect.x = x
                x += book.rect.width

        # Очищаем поверхность прозрачным цветом
        self.image.fill((0, 0, 0, 0))

        # Отрисовываем книги
        self.books.draw(self.image)

        # Вызываем метод родителя
        super().update(delta_time)

    def handle_drag(self):
        """Обработка перетаскивания объекта"""

        # Если мышь нажата и не была нажата раньше
        if pygame.mouse.get_pressed()[0] and self.grabbed_book is None:
            # Получаем какую книгу мы хотим перетащить
            for book in self.books:
                if book.rect.collidepoint(
                        (pygame.mouse.get_pos()[0] - self.rect.x, pygame.mouse.get_pos()[1] - self.rect.y)
                ):
                    self.grabbed_book = book
                    self.grabbed_book_offset = pygame.mouse.get_pos()[0] - self.rect.x - book.rect.x
                    break

        # Если мышь отпущена
        if not pygame.mouse.get_pressed()[0]:
            # Сбрасываем информацию о том, что мы перетаскиваем книгу
            self.grabbed_book = None

        # Если книга перетаскивается
        if self.grabbed_book is not None:
            # Перемещаем книгу под мышь
            target_x = pygame.mouse.get_pos()[0] - self.rect.x - self.grabbed_book_offset
            self.grabbed_book.rect.x = target_x
            if self.grabbed_book.rect.x < 0:
                self.grabbed_book.rect.x = 0
            if self.grabbed_book.rect.x > self.rect.width - self.grabbed_book.rect.width:
                self.grabbed_book.rect.x = self.rect.width - self.grabbed_book.rect.width
