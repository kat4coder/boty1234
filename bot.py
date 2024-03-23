import websocket
import json
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from telegram import Bot
import telebot

cc = 'btcusd'
interval = '1m'

socket = f'wss://stream.binance.com:9443/ws/{cc}t@kline_{interval}'

# تهيئة مصادقة OAuth2 للوصول إلى جوجل شيت
scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict({
  "type": "service_account",
  "project_id": "toark4",
  "private_key_id": "0b33351e9486a4bbe1e02eccbf0d47c3843d0c3e",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDQvStoqqnAi4Af\nvMHDxwKd33Mbv1M4WD/7ma+g21uOj4UOnwVYefhIWddvInQ9kPkbb4Kd/6qm/j1M\nM/EZNcL4rmHyjvJ0s7BbecT0tPmYyPZESPuM2b/tpIpLnFBXdVTNdwnFuTKgBl4s\nl8xCXp8mUlffOC7CPp9vQss2yDxkXEHc0KWNVwsWQhd426yuy7OqPsQ8Hm7CnmVK\nKMmWWX/ILf6HTo3m2zRtH8JQzEqwd80PQ2xr+tCOdwTwUIwUX5qjZVlO1GSUR9HP\ne5qfCXNhlo6RLl9uTsNVlq5eehgfECMVC353Vx698H4E4K/Sg7YtEbJBHBXFJj5+\n3bBWluBTAgMBAAECggEABD75o8XnV3ee+Hl/wx2iHUr/AOv9FqxsFMNocdznn/hy\nzCLXWkuuc+5PHKW2eDNVCRLu6CVCUX/ioerjXYNp8i895jZN+UPxQB/m4TsDLr5V\nWa5wXrBmBo2Uk8gotdBSesfdAFNT+jK9XKpAnE/N0sFvClpB6gj/3j5qFGgYGzFG\noA2T+x72q0m6sgLffBwrTMN/+eyh7+qHWHo5dNR0jqaL0I6RAE2Tg3FXEaKYEAcn\nL68K9TfpEGT+i3JR8r1TinNKZxK2+1rowJ2RvaYuEKUMwSpuwRIv6v8O5iiu1uFK\n6k+tPC0QcxhDeYHaTOc9qkVrMyQ1EI158JfTcn8heQKBgQDpR5AtVO7Icv7zJ9gB\nle3G0msISp9Oz1BZERFy/qSMAaeIQDPEQNQq1jERv0/h2uY4qZEyma9DqbUaEi+X\naBlxaXDObP+mzF+9swCGalbsnAnL+DvOonCjzEPtX/2oW9edELfjtRvjWBT9phyP\nuRhrw/wBQU+cucT1OcvMwltrWwKBgQDlEbo2X0kYXHqfofZrNfgFSFvb7nXz9yIF\nk9UyBNtD8snQnBozT7GKepjeH5kUn5DY43j96hgboZeV8UzpytnH8lcB1bDviuYx\n972Wq4ErzPWhPPwuwzLyUM/17zkNZA/e8mlQi/tlJ2LpA9BRbAYnEvEJqzThXWPD\nz/SE8McIaQKBgQCM5kyPFN2k9NBIzagKTSRxEmbTez79uvos0cJYUrXQWq91/FFI\nGGAN/5FjxsnZAP5M+x5YEbtqgvZ/6LwWFypG9gjMpclEVez+B0Ap79DQ2O6R5D07\ncaHXTWk51uC+77orhA2N27YcevcyvUJDDOlTLezoVSpg31O3SlFuO3Y8QQKBgHlX\ndqiuuO2qr1o4VWxdXlCOD/rkyp69XsxNjzW71NqdlcJnrolXwdh1MN0ZJ+IA1J3P\ngZwfkT2xz7ah5/hAeDSubuCN7fg2P9JgRZG2r+of3E3ZHE05IZeyrza7ziEFzFJx\nXtBIFpdy0bZVStiWvHueUQiqJIztB5gGZKS3VvdhAoGAehy19qE97KRf3BfY6M1E\nBpmcqL4fzgDH4QlAGEM7zL9k3rT3QcgFj5iviiVKrVO7aEs5ieS1CXQZkMsfB/wP\nclcwzNfG9nwsk0N0Nz1NmkNT6BSQo9DxkcbPKxOXc0GHoCJadg7mFf27SBZbGvmN\nt+AIB1q2ivB6kjHRRzW0f4w=\n-----END PRIVATE KEY-----\n",
  "client_email": "toarkpy3@toark4.iam.gserviceaccount.com",
  "client_id": "110685802050878413404",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/toarkpy3%40toark4.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}, scope)
client = gspread.authorize(creds)

# فتح ورقة العمل والحصول على جدول
sheet = client.open('pytoarka').sheet1
sheet_name = 'OffResult'  # اسم ورقة العمل المطلوبة
OffResult = client.open('pytoarka').worksheet(sheet_name)

# تعيين متغير لتتبع حالة الاتصال
connected = False

bot = Bot(token='7010021442:AAGCPqTOUK4M4iy5HXANnjxYK5K69gidLPA')
CHANNEL_ID = '@ToarkStrategy'

def send_telegram_message(message):
    bot.send_message(chat_id=CHANNEL_ID, text=message)

def check_decimal_parity(number):
    # Determine whether the decimal number is even or odd
    decimal_part = str(number).split('.')[1]
    last_two_digits = int(decimal_part[-2:])  # Get the last two decimal digits as an integer
    if last_two_digits % 2 == 0 or last_two_digits  in [10, 30, 50, 70, 90]:  # Treat multiples of 10 as odd
        return "even"
    else:
        return "odd"
def on_message(ws, message, news=None):
    global connected
    json_message = json.loads(message)
    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']
    close_formatted = '{:.2f}'.format(float(close))  # تنسيق السعر برقمين فقط بعد الفاصلة
    close_time = datetime.utcfromtimestamp(candle['t'] / 1000).strftime('%Y%m%d%H%M')
    next_minute_time = (datetime.utcfromtimestamp(candle['t'] / 1000) + timedelta(minutes=1)).strftime('%Y%m%d%H%M')
    last_decimal_digit = int(float(close) * 100) % 100  # الحصول على الرقم العشري الأخير كرقم صحيح
    decimal_parity = check_decimal_parity(float(close))
    typ = "even" if decimal_parity == "odd" else "odd"

    if is_candle_closed:
        print("--------------------------------")
        c_b3 = OffResult.cell(3, 2).value
        c_c5 = OffResult.cell(6, 3).value
        c_h1 = OffResult.cell(1, 8).value
        time.sleep(1)
        OffResult.update(range_name='G1', values=[[close_formatted]])
        time.sleep(1)
        c_c1 = OffResult.cell(1, 3).value
        c_e3=OffResult.cell(3, 5).value
        print("wave 1 :",c_e3)
# def send_shete_wave():
        c_c1 = OffResult.cell(1, 3).value
        c_c2 = OffResult.cell(2, 3).value
        c_d1 = OffResult.cell(1, 4).value
        c_e1 = OffResult.cell(1, 5).value
        c_b2 = OffResult.cell(1, 2).value

        if decimal_parity == "odd":
            ref= OffResult.cell(5, 1).value
            print("O1: ",ref)
            ref2 = OffResult.cell(6, 1).value
            print("O2 : ", ref2)
            ref3 = OffResult.cell(6, 2).value
            print("O3 : ", ref3)
            ref4 = OffResult.cell(16, 4).value
            print("O4 : ", ref4)
            ref5 = OffResult.cell(16, 5).value
            print("O5 : ", ref5)

        else:
            ref=OffResult.cell(5, 2).value
            print("E1 : ", ref)
            ref2 = OffResult.cell(6, 2).value
            print("E2 : ", ref2)
            ref3 = OffResult.cell(6, 1).value
            print("E3 : ", ref3)
            ref4 = OffResult.cell(16, 5).value
            print("E4 : ", ref4)
            ref5 = OffResult.cell(16, 4).value
            print("E5 : ", ref5)





        print("wave 2 :", c_c1)



        if c_b3 == decimal_parity:
            rslt = (f"\n\n X {c_c2} 🎉 Previous Result: Won!🎉")
        else:
            rslt = (f"\n\n X {c_c2} 😔 Previous Result: Lost!😔")

        if c_h1 == "yes":
            send_telegram_message(f"{rslt}\n\n🕒 {close_time} 🕒\n\n💰Price: {close_formatted}")

        if int(c_e3) > 30  and int(c_c1) == 1 and int(c_c5)<30 and int(ref5)>0 :
            print("next")
            rdy = (f" Next {typ} \n\n invest {decimal_parity}")
            send_telegram_message(rdy)

        # if int(c_e3) > 30:
        #     print("تحققت الشروط بنجاح")  # التحقق من أن الشروط تمت المطابقة
        #     rdy = f"التالي {typ}\n\n استثمر {decimal_parity}\n\n{c_e3}"  # التأكد من التنسيق الصحيح للرسالة
        #     try:
        #         send_telegram_message(rdy)  # استدعاء الدالة لإرسال الرسالة
        #         print("تم إرسال الرسالة بنجاح إلى التليجرام")
        #     except Exception as e:
        #         print("حدث خطأ أثناء إرسال الرسالة:", e)  # التعامل مع الأخطاء في حالة فشل إرسال الرسالة
        # else:
        #     print("لم تتحقق الشروط")  # إرسال رسالة في حالة عدم تطابق الشروط

        # if c_b3 == decimal_parity:
        #     news = f"📈 Last Invest ! {c_b3}\n\n🕒 Investment Period: {close_time}\n\n💰 Price: {close_formatted}\n\n🔢 Parity: {decimal_parity}"
        #
        #     news += "\n\n🎉 Previous Result: Won!🎉"
        # else:
        #     news += "\n\n😔🎉🎉🎉 Previous Result: Lost!😔"
        # print("XXXXXXXXXX Last Invest XXXXXXXX")
        # time.sleep(5)
        #
        print("ref :", c_c5)

        if int(ref) > 30 and int(ref2) < 30 and int(c_c1) < 3 and int(ref4)>0:
            OffResult.update(range_name='H1', values=[["yes"]])
            print("send : yes")
        else :
            OffResult.update(range_name='H1', values=[["no"]])
            print("send : no")


        if int(ref) > 30 and int(ref2) < 30 and int(c_c1) < 3 and int(ref4)>0:
            message = f" X {c_c1} 📈 Invest Now! {typ}\n\n🕒 Investment Period: {next_minute_time} "
        # if c_b3 == decimal_parity:
        #     message += "\n\n🎉 Previous Result: Won!🎉"
        # else:
        #     message += "\n\n😔 Previous Result: Lost!😔"

            send_telegram_message(message)

        if int(c_d1) > 0:
            if decimal_parity == "odd":

                OffResult.update([[OffResult.cell(14, 2).value]], 'B15')

                OffResult.update([[OffResult.cell(13, 2).value]], 'B14')

                OffResult.update([[OffResult.cell(12, 2).value]], 'B13')

                OffResult.update([[OffResult.cell(11, 2).value]], 'B12')

                OffResult.update([[OffResult.cell(10, 2).value]], 'B11')

                OffResult.update([[OffResult.cell(9, 2).value]], 'B10')

                OffResult.update([[OffResult.cell(8, 2).value]], 'B9')

                OffResult.update([[OffResult.cell(7, 2).value]], 'B8')

                OffResult.update([[OffResult.cell(6, 2).value]], 'B7')
                OffResult.update([[OffResult.cell(5, 2).value]], 'B6')

                OffResult.update([[OffResult.cell(3, 5).value]], 'B5')
            else:
                OffResult.update([[OffResult.cell(14, 1).value]], 'A15')

                OffResult.update([[OffResult.cell(13, 1).value]], 'A14')

                OffResult.update([[OffResult.cell(12, 1).value]], 'A13')

                OffResult.update([[OffResult.cell(11, 1).value]], 'A12')

                OffResult.update([[OffResult.cell(10, 1).value]], 'A11')

                OffResult.update([[OffResult.cell(9, 1).value]], 'A10')

                OffResult.update([[OffResult.cell(8, 1).value]], 'A9')

                OffResult.update([[OffResult.cell(7, 1).value]], 'A8')

                OffResult.update([[OffResult.cell(6, 1).value]], 'A7')
                OffResult.update([[OffResult.cell(5, 1).value]], 'A6')

                OffResult.update([[OffResult.cell(3, 5).value]], 'A5')
                time.sleep(1)
        # OffResult.update([[OffResult.cell(3, 5).value]], 'B5')
        # time.sleep(1)
        #
        # OffResult.update([[OffResult.cell(3, 5).value]], 'A5')
        # time.sleep(1)



        print("lstinv:", c_b3)
        print(decimal_parity)


        print("********** Invest Now! **************")



        print(close_time)
        print(close_formatted)
        print(last_decimal_digit)
        print(decimal_parity)


        OffResult.update([[OffResult.cell(1, 5).value]], 'E2')
        time.sleep(1)


        OffResult.update(range_name='G2', values=[[close_time]])

        c_g3 = OffResult.cell(1, 3).value
        if int(c_g3) == 1:
            time.sleep(1)
            OffResult.update([[OffResult.cell(3, 4).value]], 'D4')
            time.sleep(1)
            OffResult.update([[OffResult.cell(2, 4).value]], 'D3')
            time.sleep(1)
            OffResult.update([[OffResult.cell(1, 4).value]], 'D2')

            c_b2 = OffResult.cell(1, 3).value
            c_d1 = OffResult.cell(1, 3).value

            # if c_c1 ==1:
            #     if decimal_parity == "odd":
            #         time.sleep(1)
            #         OffResult.update([[OffResult.cell(3, 5).value]], 'B5')
            #         time.sleep(1)
            #     else:
            #         OffResult.update([[OffResult.cell(3, 5).value]], 'A5')
            #         time.sleep(1)

        c_b3 = OffResult.cell(3, 2).value
        c_g1 = OffResult.cell(1, 7).value




        # if c_b3 == decimal_parity:
        #     news = f"📈 Last Invest ! {c_b3}\n\n🕒 Investment Period: {close_time}\n\n💰 Price: {close_formatted}\n\n🔢 Parity: {decimal_parity}"
        #
        #     news += "\n\n🎉 Previous Result: Won!🎉"
        # else:
        #     news += "\n\n😔 Previous Result: Lost!😔"
        #
        # send_telegram_message(news)


        print(typ)
        OffResult.update(range_name='B3', values=[[typ]])
        OffResult.update([[OffResult.cell(1, 3).value]], 'C2')
        OffResult.update([[OffResult.cell(1, 1).value]], 'A2')

        print("--------------------------------")

def on_close(ws, close_status_code, close_msg):
    global connected
    connected = False
    print("### تم الإغلاق ###")

def on_open(ws):
    global connected
    connected = True

# دالة لإعادة الاتصال بعد انقطاع الاتصال
def reconnect(ws):
    while True:
        if not connected:
            print("### جاري إعادة الاتصال ###")
            ws.run_forever()
            time.sleep(5)
        else:
            time.sleep(5)

# إعادة الاتصال تلقائيًا بعد انقطاع الاتصال
while True:
    ws = websocket.WebSocketApp(socket, on_message=on_message, on_close=on_close, on_open=on_open)
    reconnect(ws)
