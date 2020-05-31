from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


# def index(request):
#     return render(request, 'index.html')


# class PingAPIView(APIView):
#     permission_classes = (AllowAny, )

#     def post(self, request):
#         return Response('pong')

#     def get(self, request):
#         return Response('pong')

# def buy(request):
#     if request.method == 'GET':
#         token_response = requests.post(
#             url="http://localhost:9000/api/v1/users/username_signin/",
#             headers={
#                 "Content-Type": "application/json; charset=utf-8",
#             },
#             data=json.dumps({
#                 "username": "lsdvincent",
#                 "password": "cj15051251378"
#             })
#         )
#         jwt = token_response.json()['token']
#         transaction_response = requests.post(
#             url="http://localhost:9000/api/v1/transactions/",
#             headers={
#                 "Authorization": "JWT " + jwt,
#                 "Content-Type": "application/json; charset=utf-8",
#             },
#             data=json.dumps({
#                 "address": "1",
#                 "payment": "1",
#                 "note": "string",
#                 "name": "djshop_transactions_test_" + datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
#                 "products": [
#                     {
#                         "product_spec": "1",
#                         "nums": 1
#                     }
#                 ]
#             })
#         )
#         if transaction_response.status_code == 201:
#             transaction_data = transaction_response.json()
#             alipay_response = requests.post(
#                 url="http://localhost:9000/api/v1/transactions/" +
#                     str(transaction_data['id']) + "/alipay_desktop_web/",
#                 headers={
#                     "Authorization": "JWT " + jwt,
#                     "Content-Type": "application/json; charset=utf-8",
#                         })
#             if alipay_response.status_code == 200:
#                 return redirect(alipay_response.json()['alipay_redirect'])


# def alipay_return(request):
#     messages.success(request, '购买成功')
#     return HttpResponseRedirect('/')
