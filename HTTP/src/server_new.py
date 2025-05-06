# -*- coding: utf8 -*-
import json
import pickle
from base64 import b64decode, b64encode

import requests

SCF_TOKEN = "Token"  # 请替换为你自己的 token


def handler(environ: dict, start_response):
    try:
        token = environ.get("HTTP_SCF_TOKEN")
        if token != SCF_TOKEN:
            raise ValueError("Invalid token")
    except Exception as e:
        status = '403 Forbidden'
        response_headers = [('Content-Type', 'application/json')]
        start_response(status, response_headers)
        return [json.dumps({"error": "Forbidden", "detail": str(e)}).encode()]

    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)

    try:
        kwargs = json.loads(request_body.decode("utf-8"))
        kwargs['data'] = b64decode(kwargs['data'])

        # 发起真实请求（不自动跳转，避免污染）
        r = requests.request(**kwargs, verify=False, allow_redirects=False)

        # 序列化原始 Response 对象
        serialized_resp = pickle.dumps(r)

        status = '200 OK'
        response_headers = [('Content-Type', 'text/json')]
        start_response(status, response_headers)
        return [b64encode(serialized_resp)]
    except Exception as e:
        status = '500 Internal Server Error'
        response_headers = [('Content-Type', 'application/json')]
        start_response(status, response_headers)
        return [json.dumps({"error": "Internal Error", "detail": str(e)}).encode()]
