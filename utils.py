import re
from database_interface import DatabaseInterface

CONCURRENT_LIM = 3
continue_scraping = False


def extract_id_from_link(link: str) -> int:
    """
    Get the item id integer from link
    :param link: item link
    :return: item id
    """
    return int((link.split('/')[-1])[1:])


def check_price_drop(id_num: int, new_price: int, db_handler: DatabaseInterface):
    """
    Check watched item for price change

    :param id_num: item id
    :param new_price: new item price
    :param db_handler: old item price
    :return: None
    """
    old_price = db_handler.search_watchlist(id_num)[2]
    if old_price != new_price:
        db_handler.update_watchlist_entry(id_num, new_price)
        # TODO notify price change


def match_keyword(item_name: str, db_handler: DatabaseInterface) -> str:
    models_list = db_handler.get_all_from_table("catalog")

    # remove whitespace and dashes
    item_name_processed = (re.sub(r'[-\s]', '', item_name)).lower()
    for model in models_list:

        model_processed = (re.sub(r'[-\s]', '', model[0])).lower()

        if model_processed in item_name_processed:
            return model_processed
    return "No Match"
