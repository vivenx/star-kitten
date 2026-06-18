class IntroSceneModel:
    FRAMES = (
        (
            "Мир заражается",
            "На мир обрушилась темная болезнь.\n"
            "Леса, пещеры и звезды начали гаснуть.",
        ),
        (
            "Друг заболел",
            "Лучший друг котенка тоже заразился.\n"
            "С каждым днем его свет становился слабее.",
        ),
        (
            "Поиск ответа",
            "Котенок не сдался.\n"
            "Он прочитал все книги в старой библиотеке.",
        ),
        (
            "Легенда о звезде",
            "В одной книге он нашел древнюю легенду.\n"
            "Где-то в лесу давно упала звезда, исполняющая желания.",
        ),
        (
            "Решение героя",
            "Котенок взял карту и отправился в путь.\n"
            "Его цель — найти звезду и спасти друга.",
        ),
        (
            "Начало игры",
            "Путь начинается в зараженном лесу.\n"
            "Темная болезнь уже ждет его.",
        ),
    )

    def __init__(self):
        self.frame_index = 0

    @property
    def title(self):
        return self.FRAMES[self.frame_index][0]

    @property
    def text(self):
        return self.FRAMES[self.frame_index][1]

    @property
    def is_last_frame(self):
        return self.frame_index == len(self.FRAMES) - 1

    def advance(self):
        if self.is_last_frame:
            return False
        self.frame_index += 1
        return True
