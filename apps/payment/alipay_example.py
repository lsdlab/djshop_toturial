from alipay import AliPay

app_private_key_string = open("/Users/chenjian/Python/app_private_key.pem").read()
alipay_public_key_string = open("/Users/chenjian/Python/alipay_public_key.pem").read()

alipay = AliPay(
    appid="2018102261772341",
    app_notify_url=None,
    app_private_key_string=app_private_key_string,
    alipay_public_key_string=alipay_public_key_string,
    sign_type="RSA2",
    debug=False
)

order_string = alipay.api_alipay_trade_page_pay(
    out_trade_no="20161113",
    total_amount=0.01,
    subject='测试订单',
    return_url="https://example.com",
    notify_url="https://example.com/notify"
)

alipay_redirect = "https://openapi.alipay.com/gateway.do?" + order_string
print(alipay_redirect)
