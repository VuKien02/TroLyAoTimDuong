import datetime, time
import requests
import speech_recognition as sr
import webbrowser as wb
import os
import playsound
from gtts import gTTS
from playsound import playsound
import os
import openai
import wikipedia
from youtube_search import YoutubeSearch
import webbrowser
from geopy.geocoders import Nominatim

wikipedia.set_lang('vi')
language = 'vi'

def speak(audio):
    tts = gTTS(text =audio,lang='vi')
    tts.save("audio.mp3")
    file_path = os.path.join(".", "audio.mp3")
    playsound(file_path, True)
    os.remove(file_path)

def get_audio(): 
    c=sr.Recognizer()
    while True:
        with sr.Microphone() as microphone:
            c.pause_threshold = 1
            audio = c.listen(microphone)
        try:
            query = c.recognize_google(audio, language="vi-VN")
            return query.lower()
        except sr.UnknownValueError:
            speak("Xin lỗi tôi không thể nghe rõ bạn nói gì, bạn hãy nói lại giúp tôi!")

def get_coordinates(start_location, end_location):
    geolocator = Nominatim(user_agent="my-custom-application")

    start_result = geolocator.geocode(start_location)
    end_result = geolocator.geocode(end_location)
    
    if start_result and end_result:
        start_coords = (start_result.latitude, start_result.longitude)
        end_coords = (end_result.latitude, end_result.longitude)
        return start_coords, end_coords
    else:
        return None, None

def get_vehicle():
    print("Chọn phương tiện di chuyển của bạn:")
    speak("Chọn phương tiện di chuyển của bạn:")
    print("1. Xe máy")
    print("2. Ô tô")
    print("3. Xe đạp")
    print("4. Đi bộ")
    # Lấy lựa chọn của người dùng
    choice = get_audio()
    # Xác định loại phương tiện
    if "xe máy" in choice or "xe gắn máy" in choice:
        vehicle_type = 'scooter'
    elif "ô tô" in choice or "xe hơi" in choice:
        vehicle_type = 'car'
    elif "xe đạp" in choice:
        vehicle_type = 'bike'
    elif "đi bộ" in choice:
        vehicle_type = 'foot'
    else:
        speak("Chưa xác định được phương tiện. Phương tiện mặc định là ô tô")
        vehicle_type = 'car'

    return vehicle_type

def get_directions(start_location, end_location, vehicle):
    start_coords, end_coords = get_coordinates(start_location, end_location)
    if start_coords and end_coords:
        url = 'https://graphhopper.com/api/1/route'
        params = {
            'key': 'e467ab05-6785-498b-b6f4-b0ce012d93d9',
            'point': [f"{start_coords[0]},{start_coords[1]}", f"{end_coords[0]},{end_coords[1]}"],
            'profile': vehicle,
            'locale': 'vi',
            'optimize': 'true',
            'instructions': 'true',
            'calc_points': 'true',
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            distance = data['paths'][0]['distance'] / 1000
            time_seconds = data['paths'][0]['time'] / 1000
            hours = int(time_seconds // 3600)
            minutes = int((time_seconds % 3600) // 60)
            seconds = int(time_seconds % 60)
            map_url = f"https://graphhopper.com/maps/?point={start_coords[0]},{start_coords[1]}&point={end_coords[0]},{end_coords[1]}&locale=vi&vehicle={vehicle}&debug=true&points_encoded=false&instructions=true&elevation=false&optimize=true&details=max_speed&details=road_class"
            webbrowser.open(map_url)
            print(f"Độ dài quãng đường: {round(distance, 2)} km")
            speak(f"Độ dài quãng đường: {round(distance, 2)} kilômét")
            print(f"Thời gian di chuyển: {hours} giờ {minutes} phút {seconds} giây")
            speak(f"Thời gian di chuyển: {hours} giờ {minutes} phút {seconds} giây")
            instructions = data['paths'][0]['instructions']
            print("Chỉ dẫn:")
            for instruction in instructions:
                text = instruction['text']
                print(text)
                speak(text)
        else:
            print("Yêu cầu API không thành công. Mã lỗi:", response.status_code)
    else:
        print("Không thể lấy được tọa độ cho ít nhất một địa điểm.")
    
def the_end (): 
    speak("Hẹn gặp lại bạn lần sau nhé!")
    
def welcome():
        hour=datetime.datetime.now().hour
        if hour >= 6 and hour<12:
            speak("Xin chào buổi sáng, tôi có thể gọi bạn là gì nhỉ?")
        elif hour>=12 and hour<18:
            speak("Xin chào buổi chiều, tôi có thể gọi bạn là gì nhỉ?")
        elif hour>=18 and hour<24:
            speak("Xin chào buổi tối, tôi có thể gọi bạn là gì nhỉ?")
        name_user = get_audio().split("là") 
        print(name_user)
        speak(f"Xin chào {name_user[0] if len(name_user) == 1 else name_user[1]}, tôi có thể giúp gì cho bạn!") 
        
def google_search(keyword):
    base_url = "https://www.google.com/search?q="
    speak("Okay!")
    wb.get().open(f"{base_url}{keyword}")
    speak(f"Kết quả tìm kiếm cho từ khóa {keyword} trên google!")

def get_time(query):
    now = datetime.datetime.now()
    if "giờ" in query or "thời gian" in query:
        speak("Bây giờ là %d giờ %d phút" % (now.hour, now.minute))
    elif "ngày" in query:
        speak("Hôm nay là ngày %d tháng %d năm %d" % (now.day, now.month, now.year))
    else:
        speak("Tôi không nghe rõ bạn nói, bạn có thể nói lại được không")

def weather():
    speak("Bạn muốn tìm kiếm thời tiết ở khu vực nào ?")
    ow_url = "http://api.openweathermap.org/data/2.5/weather?"
    city = get_audio()
    if not city:
        pass
    api_key = "fe8d8c65cf345889139d8e545f57819a"
    call_url = ow_url + "appid=" + api_key + "&q=" + city + "&units=metric"
    response = requests.get(call_url)
    data = response.json()
    if data["cod"] != "404":
        city_res = data["main"]
        current_temperature = city_res["temp"]
        current_pressure = city_res["pressure"]
        current_humidity = city_res["humidity"]
        suntime = data["sys"]
        sunrise = datetime.datetime.fromtimestamp(suntime["sunrise"])
        sunset = datetime.datetime.fromtimestamp(suntime["sunset"])
        wthr = data["weather"]
        weather_description = wthr[0]["description"]
        now = datetime.datetime.now()
        content = """
        Hôm nay là ngày {day} tháng {month} năm {year}
        Mặt trời mọc vào {hourrise} giờ {minrise} phút
        Mặt trời lặn vào {hourset} giờ {minset} phút
        Nhiệt độ trung bình là {temp} độ C
        Áp suất không khí là {pressure} héc tơ Pascal
        Độ ẩm là {humidity}%
        Trời hôm nay quang mây. Dự báo mưa rải rác ở một số nơi.""".format(day = now.day,month = now.month, year= now.year, hourrise = sunrise.hour, minrise = sunrise.minute,
                                                                           hourset = sunset.hour, minset = sunset.minute, 
                                                                           temp = current_temperature, pressure = current_pressure, humidity = current_humidity)
        speak(content)
        time.sleep(30)
    else:
        speak("Không tìm thấy địa chỉ của bạn")

def tell_me_about(theory):
    try:
        contents = wikipedia.summary(theory).split("\n")
        print(contents)
        speak(contents[0])
        if(len(contents) > 1):
            time.sleep(3)
            speak("Bạn muốn nghe thêm không")
            load_more = get_audio()
            if("có" in load_more or "nghe thêm" in load_more):
                for content in contents[1:]:
                    speak(content)
                    time.sleep(5)
        speak('Cảm ơn bạn đã lắng nghe!!!')
    except:
        speak("Bot không định nghĩa được thuật ngữ của bạn. Xin mời bạn nói lại")

def visits_website(domain):
    wb.get().open(f"https://{domain}")
    speak("Trang web bạn yêu cầu đã được mở!")
    
def open_application(text):
    if "google" in text:
        speak("Mở Google Chrome")
        os.startfile("C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk")
    elif "word" in text:
        speak("Mở Microsoft Word")
        os.startfile(
            'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Word.lnk')
    elif "excel" in text:
        speak("Mở Microsoft Excel")
        os.startfile(
            'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Excel.lnk')
    else:
        speak("Ứng dụng chưa được cài đặt. bạn có muốn tìm kiếm trên cửa hàng không?")
        user_should_use = get_audio()
        if("có" in user_should_use):
            base_url = "https://apps.microsoft.com/search?query="
            filter_query = "mở"
            if("ứng dụng" in text):
                filter_query = "ứng dụng"
            app_search = text.split(filter_query)[1]
            wb.get().open(f"{base_url}{app_search}")
        else:
            speak("Cảm ơn bạn đã sử dụng tôi!")
            

def play_music(mysong):
    while True:
        result = YoutubeSearch(mysong, max_results=10).to_dict() 
        if result:
            break
        
    url = 'https://www.youtube.com' + result[0]['url_suffix']
    print(result[0])
    print(url)
    wb.get().open(url)
    speak("Video bạn yêu cầu đã được mở.")



# main
def __main__():
    welcome()
    i = 0
    while True:
        if(i > 0):
            speak("Bạn có muốn tôi làm gì nữa không?")
        query = get_audio()
        if("mở" in query):
            if("bật google" in query or "tìm kiếm" in query or "search" in query):
                filter_query = query.split("tìm kiếm")[1]
                if(filter_query != ""):
                    google_search(filter_query)
                else:
                    speak("Bạn muốn tìm gì?")
                    query_search = get_audio()
                    google_search(query_search)
            elif ("bài hát" in query or "video" in query):
                filter_query = "là"
                if("hát" in query):
                    filter_query = "hát"
                mysong = query.split(filter_query)
                if("video" in query):
                    filter_query = "video"
                mysong = query.split(filter_query)
                if(len(mysong) > 0): {
                    play_music(mysong[1])
                }
                else:
                    speak("Bạn hãy nói tên bài hát muốn nghe!")
                    mysong = get_audio()
                    play_music(mysong)
            else:
                open_application(query)
        elif ("chỉ đường" in query):
            if "từ" in query and ("đến" in query or "tới" in query or "đi" in query):
                if "tới" in query:
                    keyword_filter = "tới"
                elif "đi" in query:
                    keyword_filter = "đi"
                else:
                    keyword_filter = "đến"
                
                array_locations = query.split("từ")[1].split(keyword_filter)
                start_location = array_locations[0].strip()
                end_location = array_locations[1].strip()
                print(start_location,"đến",end_location)
                vehicle = get_vehicle()
                get_directions(start_location,end_location,vehicle)
            else:
                speak("Bạn hãy nói điểm bắt đầu của bạn!")
                start_location = get_audio().strip()
                speak("Điểm kết thúc của bạn ở đâu?")
                end_location = get_audio().strip()
                print(start_location,"đến",end_location)
                vehicle = get_vehicle()
                get_directions(start_location, end_location,vehicle)
        elif "ngày" in query or "giờ" in query or "thời gian" in query:
            get_time(query)
        elif("lý thuyết" in query or "định nghĩa" in query or "tôi muốn biết" in query):
            filter_query = "về"
            theory = query.split(filter_query)
            tell_me_about(theory)
        elif("thời tiết" in query):
            weather()
        elif ("hẹn gặp lại" in query or "dừng chương trình" in query or "dừng lại" in query):
            the_end()
            break
        time.sleep(3)
        i += 1
    
__main__()
