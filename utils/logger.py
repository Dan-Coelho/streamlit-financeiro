import logging
from colorama import Fore, Style, init

# Inicializa o Colorama
init(autoreset=True)


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return log_color + message + Style.RESET_ALL


# Configura o logger
logger = logging.getLogger("meu_logger")
handler = logging.StreamHandler()

formatter = ColorFormatter("[%(asctime)s] [%(levelname)s] [%(filename)s] — %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
