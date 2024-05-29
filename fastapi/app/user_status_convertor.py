def convertor(data):
    
    status = {
        "정지": 1,
        "도보": 2,
        "차량": 3,
        "지하철": 4
    }.get(data, None)

    return status
    