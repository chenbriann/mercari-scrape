import re
from database_interface import DatabaseInterface
import asyncio

CONCURRENT_LIM = 3
continue_scraping = False


def extract_id_from_link(link: str) -> int:
    """
    Get the item id integer from link
    :param link: item link
    :return: item id
    """
    return int((link.split('/')[-1])[1:])


def split_text(text: str, chunk_size: int):
    """
    Split text into chunks
    :param text:
    :param chunk_size:
    :return:
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


async def match_keyword(item_name: str, db_handler: DatabaseInterface) -> str:
    models_list = db_handler.get_all_from_table("catalog")

    # remove whitespace and dashes
    item_name_processed = (re.sub(r'[-\s]', '', item_name)).lower()

    async def check_match(model) -> str:
        model_processed = (re.sub(r'[-\s]', '', model[0])).lower()
        return model_processed if model_processed in item_name_processed else "No Match"

    matches = await asyncio.gather(*(check_match(model) for model in models_list))
    matches = [model for model in matches if model != "No Match"]

    if matches:
        return matches[0]
    else:
        return "No Match"
