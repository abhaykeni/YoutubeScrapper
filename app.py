from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
from selenium import webdriver
from bs4 import BeautifulSoup
import mysql.connector as conn
import requests
import os
import base64
import pymongo
from pytube import YouTube

app = Flask(__name__)

@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review', methods=['POST', 'GET']) # route to show the review comments in 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a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            search_url = request.form['content'].replace(" ", "")

            mydb = conn.connect(port="3308", host="localhost", user='root', password="root", )
            cursor = mydb.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS PROJECT")
            cursor.execute("CREATE TABLE IF NOT EXISTS PROJECT.YOUTUBE_DATA(YT_NAME VARCHAR(30),TITLE LONGTEXT,VIEWS VARCHAR(30),TIME VARCHAR(30),V_URL LONGTEXT,I_URL LONGTEXT,VI_PATH LONGTEXT)")
            print("MySql Done")

            client = pymongo.MongoClient("mongodb+srv://root:root@cluster0.klhye8n.mongodb.net/?retryWrites=true&w=majority")
            db = client.test
            print(db)

            database = client['Project']
            collection = database["Youtube_Data"]
            print("MongoDb Done")

            driver = webdriver.Chrome(executable_path=r'G:\Assignments\chromedriver.exe')
            driver.get(search_url)
            content = driver.page_source.encode('utf-8').strip()

            soup = BeautifulSoup(content, 'html.parser')
            print("---------------------------------------------------------------------------------------------")
            youtuber_name = soup.findAll('div', id="text-container")
            titles = soup.findAll('a', id='video-title-link')
            views = soup.findAll('span', class_='inline-metadata-item style-scope ytd-video-meta-block')
            video_urls = soup.findAll('a', id='video-title-link')
            print(video_urls)
            images = soup.findAll('img', id="img")

            print('Channel: {}'.format(search_url))
            i = 0  # views and time
            j = 0  # urls

            yt_name = youtuber_name[0].text
            title_list = []
            view_list = []
            video_url_list = []
            image_list = []
            time_span_list = []

            for title in titles[:4]:
                title_list.append(title.text)
                view_list.append(views[i].text)
                time_span_list.append(views[i + 1].text)
                video_url_list.append(video_urls[j].get('href'))
                if(images[i + 7].get('src') == None):
                    image_list.append(images[i + 6].get('src'))
                else:
                    image_list.append(images[i + 7].get('src'))
                print('\n{}\t{}\t{}\thttps://www.youtube.com{}'.format(title.text, views[i].text, views[i + 1].text, video_urls[j].get('href')))
                i += 2
                j += 1

            url = "https://www.youtube.com"
            save_path = "G:\Assignments\Videos/"
            folder_path = "G:\Assignments\Pics"

            print(image_list)

            for count in range(0, len(image_list)):

                image_content = requests.get(image_list[count]).content

                image_file = open(os.path.join(folder_path, 'jpg' + "_" + str(count) + ".jpg"), 'wb')
                image_file.write(image_content)
                image_file.close()

                image_file = open(os.path.join(folder_path, 'jpg' + "_" + str(count) + ".jpg"), 'rb')
                converted_string = base64.b64encode(image_file.read())
                image_file.close()

                data = {"Title": title_list[count], "Istring": converted_string}
                collection.insert_one(data)

                image_file = open(os.path.join(folder_path, 'jpg' + "_" + str(count) + ".bin"), 'wb')
                image_file.write(converted_string)
                image_file.close()

                print(f"SUCCESS - saved {image_list[count]} - as {folder_path}")

                download_link = url + video_url_list[count]
                #yt = YouTube(download_link)
                #stream = yt.streams.first()
                #stream.download(save_path)


            dir_list = os.listdir(save_path)
            dir_list_path = []

            final_result = []

            for st in range(0, len(dir_list)):
                dir_list_path.append(os.path.join(save_path + dir_list[st]))

            for tc in range(0,len(title_list)):
                cursor.execute("INSERT INTO PROJECT.YOUTUBE_DATA VALUES(%s,%s,%s,%s,%s,%s,%s)", (yt_name, title_list[tc], view_list[tc], time_span_list[tc], video_url_list[tc], image_list[tc],dir_list_path[tc]))
                mydb.commit()
                mydict = {"Youtuber_Name": yt_name, "Title": title_list[tc], "View_Count": view_list[tc],
                          "Duration": time_span_list[tc],"Video_Link": video_url_list[tc],
                          "Thumbnail_Link": image_list[tc],"Video_Path":dir_list_path}
                final_result.append(mydict)
            return render_template('result.html', reviews=final_result[0:(len(final_result))])

        except Exception as e:
            print(e)

if __name__ == "__main__":
    app.run(port=5002, debug=True)