import json
from datetime import datetime
import aiohttp
from starlette.responses import PlainTextResponse
from npay_data.enum_data import ResponseStatusResult
from npay_function import ecpay_payment_sdk
from npay_function.ecpay_payment_sdk import ECPayPaymentSdk
from npay_function.pay_handler import PayHandler

"""
#2 ECPay
"""
UNIT = "d"


class Pay(PayHandler):

    def do(self):
        money = self.pay.get_money()
        tp_state = int(self.pay.get_tp_state())
        mer_state = int(self.pay.get_mer_state())
        channel_secret = self.pay.get_mer_key()
        tp_expansion_url = self.pay.get_tp_expansion_url()
        res = dict(state=ResponseStatusResult.error.value,
                   resulet='error',
                   message='')
        if tp_state == 0 or mer_state == 0:
            res = dict(
                resulet='error',
                message='不支持的支付通道'
            )
            return res
        order_params = {
            'MerchantTradeNo': datetime.now().strftime("NO%Y%m%d%H%M%S"),
            'StoreID': '',
            'MerchantTradeDate': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            'PaymentType': 'aio',
            'TotalAmount': money,
            'TradeDesc': '訂單測試',
            'ItemName': '商品1#商品2',
            # 'ReturnURL': 'https://www.ecpay.com.tw/return_url.php',
            'ReturnURL': self.pay.get_notify_url(),
            'ChoosePayment': 'ALL',
            # 'ClientBackURL': 'https://www.ecpay.com.tw/client_back_url.php',
            # 'ClientBackURL': 'https://3504-220-128-216-143.ngrok.io/ecpay/client',
            'ItemURL': 'https://www.ecpay.com.tw/item_url.php',
            # 'Remark': '交易備註',
            'ChooseSubPayment': '',
            # 'OrderResultURL': 'https://3504-220-128-216-143.ngrok.io/ecpay',
            # 'NeedExtraPaidInfo': 'Y',
            'DeviceSource': '',
            # 'IgnorePayment': 'BARCODE', # 隱藏的支付方式
            'PlatformID': '',
            # 'InvoiceMark': 'N', # 電子發票
            'CustomField1': '',
            'CustomField2': '',
            'CustomField3': '',
            'CustomField4': '',
            'EncryptType': 1,
        }
        extend_params_1 = {
            'ExpireDate': 7,
            'PaymentInfoURL': 'https://www.ecpay.com.tw/payment_info_url.php',
            'ClientRedirectURL': '',
        }

        extend_params_2 = {
            'StoreExpireDate': 15,
            'Desc_1': '',
            'Desc_2': '',
            'Desc_3': '',
            'Desc_4': '',
            'PaymentInfoURL': 'https://www.ecpay.com.tw/payment_info_url.php',
            'ClientRedirectURL': '',
        }

        extend_params_3 = {
            'BindingCard': 0,
            'MerchantMemberID': '',
        }

        extend_params_4 = {
            'Redeem': 'N',
            'UnionPay': 0,
        }
        ecpay_payment_sdk = ECPayPaymentSdk(
            MerchantID='2000132',
            HashKey='5294y06JbISpM5x9',
            HashIV='v77hoKGq4kWxNNIS'
        )
        try:
            # 產生綠界訂單所需參數
            final_order_params = ecpay_payment_sdk.create_order(order_params)

            # 產生 html 的 form 格式
            action_url = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 測試環境
            # action_url = 'https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5' # 正式環境
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(self.pay.get_tp_pay_test_url(), data=final_order_params) as resp:
            #         print(resp)
            #         html = await resp.json()

            html = ecpay_payment_sdk.gen_html_post_form(self.pay.get_tp_pay_test_url(), final_order_params)
            print(html)
            with open("ECPay.html", "w", encoding='utf-8') as f:
                f.write(html)

            res['state'] = ResponseStatusResult.ok.value
            res['resulet'] = 'success'
            res['message'] = 'respond web url'
            text = PlainTextResponse(html)
            res['data'] = dict(url=text)
            return PlainTextResponse(json.dumps(res))

            # return html
        except Exception as error:
            print('An exception happened: ' + str(error))
