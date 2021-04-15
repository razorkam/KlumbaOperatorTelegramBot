import logging
import source.TelegramWorker as TgWorker
import source.StorageWorker as StorageWorker
from source import config as cfg

# journalctl logging when running via systemctl
logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT)


def main():
    StorageWorker.maintain_storage()
    TgWorker.run()


main()
