# settings‚©‚ç“Ç‚İæ‚Á‚½’l‚ğŠî‚ÉACreator‚Éİ’è‚·‚émode‚Ì®”’l‚ğ¶¬

from .viewCreator import MODE_WHITE, MODE_DARK

class ViewModeCalculator:
    def __init__(self, is_dark=False, is_word_wrap=True):
        self.is_dark = is_dark
        self.is_word_wrap = is_word_wrap

    def getMode(self):
        mode = 0
        if self.is_dark:
            mode += MODE_DARK
        if self.is_word_wrap:
            mode += MODE_WRAPPING
        return mode
