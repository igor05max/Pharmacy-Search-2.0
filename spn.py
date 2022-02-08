def spn_(cor, json_response):

    t = json_response["geometry"]["coordinates"]
    delta, delta2 = t
    cor = list(map(float, cor.split(",")))

    return f"{max(abs(delta - cor[0]),abs(delta2 - cor[1]))},{max(abs(delta - cor[0]), abs(delta2 - cor[1]))}"
