from flask import blueprints, jsonify, request
from whoosh.qparser import QueryParser

from server.models import Books, BookFactory

book_list = Books()

bp = blueprints.Blueprint("book", __name__, url_prefix="/book")


@bp.route("/", methods=["GET", "POST"])
def book():
    if request.method == "GET":
        return jsonify({"code": 0, "msg": "success", "data": book_list.list_books()})

    elif request.method == "POST":
        # 上传书目

        # 获取二进制文件
        file = request.files.get("book", None)
        if file is None:
            return jsonify({"code": 1, "msg": "book is empty", "data": {}})

        name = str(file.filename).split(".")[0]

        # 创建 book 对象
        aBook = BookFactory.create_book(name, file.read())

        if aBook:
            book_list.add_book(aBook)

            return jsonify(
                {"code": 0, "msg": "success", "data": {"book_id": aBook.book_id}}
            )
        else:
            return jsonify({"code": 1, "msg": "fail to create book", "data": {}})

    # return 使用的请求方法不对
    return jsonify({"code": 1, "msg": "unsupported method", "data": {}})


@bp.route("/<book_id>", methods=["GET"])
def search_by_id(book_id: str):
    prompt = request.args.get("prompt", "")
    if prompt == "":
        return jsonify({"code": 1, "msg": "prompt is empty", "data": {}})

    # 在 books 中查找 book_id 对应的 ix
    aBook = book_list.get_book_by_id(book_id)
    if aBook is None:
        return jsonify({"code": 1, "msg": "book not found", "data": {}})

    # 在 ix 中查找
    ix = aBook.ix
    results = []

    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(prompt)
        _results = searcher.search(query)
        if len(_results) == 0:
            results.append("No results found.")
        else:
            for result in _results:
                results.append(result["content"])

    return jsonify({"code": 0, "msg": "success", "data": {"results": results}})
