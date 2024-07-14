import time
import json
import requests
import hashlib
import hmac
import base64

domain = "https://sandbox-api-pay.line.me" # 測試用的環境
channel_id = "1656916733"
channel_secret = "dd45aa16318c92bd392fb40347fa958c"
nonce = str(round(time.time() * 1000))  # nonce = str(uuid.uuid4())
transaction_id = ''
money = 200

headers = {
    'Content-Type': 'application/json',
    'X-LINE-ChannelId': channel_id,
    'X-LINE-Authorization-Nonce': nonce,
}


def get_auth_signature(secret, uri, body, nonce):
    """
    用於製作密鑰
    :param secret: your channel secret
    :param uri: uri
    :param body: request body
    :param nonce: uuid or timestamp(時間戳)
    :return:
    """
    str_sign = secret + uri + body + nonce
    return base64.b64encode(
        hmac.new(str.encode(secret), str.encode(str_sign), digestmod=hashlib.sha256).digest()).decode("utf-8")


def do_request_payment():
    '''此api僅使用文檔中必填的資料'''

    uri = "/v3/payments/request"
    request_options = {
        "amount": money,
        "currency": 'TWD',
        "orderId": nonce,
        "packages": [{
            "id": nonce,
            "amount": int(money),
            "name": 'NADI',
            "products": [{
                "name": 'NADI商品名稱需提供',
                # "quantity": 1, # 可不填
                "price": int(money)
            }]
        }],
        "redirectUrls": {
            "confirmUrl": 'https://fastapi.tiangolo.com/zh/tutorial/bigger-applications/',
            "cancelUrl": 'https://fastapi.tiangolo.com/zh/tutorial/bigger-applications/'
        }
    }

    json_body = json.dumps(request_options)

    # headers['X-LINE-Authorization-Nonce'] = nonce
    headers['X-LINE-Authorization'] = get_auth_signature(channel_secret, uri, json_body, nonce)
    response = requests.post(domain + uri, headers=headers, data=json_body)
    print(response.text)
    dict_response = json.loads(response.text)

    if dict_response.get('returnCode') == "0000":
        info = dict_response.get('info')
        web_url = info.get('paymentUrl').get('web')
        transaction_id = str(info.get('transactionId'))
        print(f"付款web_url:{web_url}")
        print(f"交易序號:{transaction_id} (測試用, 付款完成後請手動儲存)")


def do_checkout(transaction_id):
    checkout_url = f"/v3/payments/requests/{transaction_id}/check"
    conf_data = """{"amount": 200, "currency": "TWD"}"""
    headers['X-LINE-Authorization'] = get_auth_signature(channel_secret, checkout_url, conf_data, nonce)
    response = requests.get(domain + checkout_url, headers=headers, data=conf_data)
    response = json.loads(response.text)
    print(f'checkout response{response}')
    if str(response.get('returnCode')) == "0110":
        return True
    return False


def do_confirm(transaction_id):
    confirm_url = f"/v3/payments/{transaction_id}/confirm"
    conf_data = """{"amount": 200, "currency": "TWD"}"""
    headers['X-LINE-Authorization'] = get_auth_signature(channel_secret, confirm_url, conf_data, nonce)
    response = requests.post(domain + confirm_url, headers=headers, data=conf_data)
    response = json.loads(response.text)
    print(f'confirm response{response}')
    return response.get('returnMessage')


if __name__ == "__main__":
    do_request_payment()  # 向linepay請求付款

    # 填入已付款後的交易序號
    transaction_id = "2022041200710449310"  # ex: transaction_id = 2022031400707390210
    status = do_checkout(transaction_id)  # 檢查訂單狀態
    if status == True:
        print(f'confirm result:{do_confirm(transaction_id)}')  # 確認訂單
