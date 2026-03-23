def paginate_items(items: list, page: int, per_page: int = 8):
    start = page * per_page
    end = start + per_page
    return items[start:end]


def filter_items(
    items: list, min_price: int | None = None, max_price: int | None = None
):
    if min_price is not None:
        items = [i for i in items if i["price"] >= min_price]
    if max_price is not None:
        items = [i for i in items if i["price"] <= max_price]
    return items
