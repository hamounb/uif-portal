import requests
from random import randint


def send_sms(id, mobile, args):
    data = {'bodyId': id, 'to': mobile, 'args': args}
    response = requests.post('https://console.melipayamak.com/api/send/shared/8265f04cef6145c3be077c6f34e656c1', json=data)
    print(response.json())

# def send_token(mobile:str):
#     data = {'to': mobile}
#     response = requests.post('https://console.melipayamak.com/api/send/otp/8265f04cef6145c3be077c6f34e656c1', json=data)
#     return response.json()

def send_token(number):
    code = randint(100000, 999999)
    args = [str(code)]
    data = {'bodyId': 238612, 'to': number, 'args': args}
    response = requests.post('https://console.melipayamak.com/api/send/shared/8265f04cef6145c3be077c6f34e656c1', json=data)
    x = response.json()
    return {"code":str(code), "status":x["status"], "recid":x["recId"]}