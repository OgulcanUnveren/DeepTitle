import sys
import telebot
import pysrt
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import whisper
import json

class SubtitleChef:
    def __init__(self):
        self.bot_token=''
        self.mp4filename=""
        self.jsonfile = ""
        self.srtfilename=""        
    def time_to_seconds(self,time_obj):
        return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000


    def create_subtitle_clips(self,subtitles, videosize,fontsize=24, font='Arial', color='yellow', debug = False):
        subtitle_clips = []

        for subtitle in subtitles:
            start_time = self.time_to_seconds(subtitle.start)
            end_time = self.time_to_seconds(subtitle.end)
            duration = end_time - start_time

            video_width, video_height = videosize

            text_clip = TextClip(subtitle.text, fontsize=fontsize, font=font, color=color, bg_color = 'black',size=(video_width*3/4, None), method='caption').set_start(start_time).set_duration(duration)
            subtitle_x_position = 'center'
            subtitle_y_position = video_height* 4 / 5 

            text_position = (subtitle_x_position, subtitle_y_position)                    
            subtitle_clips.append(text_clip.set_position(text_position))

        return subtitle_clips
    def whispertranscribe(self,file,jsonf):
        model = whisper.load_model("medium",download_root="/home/th3d1gger/models")
        print(file)
        text = model.transcribe(file)
    #printing the transcribe
    #print(text)
        with open(jsonf,"w") as jsontext:
            print(text['text'])
            jsontext.write(json.dumps(text,indent=4))
            jsontext.close()
    def create_srt(self,file,srt):
        file= open(file)
        ro_be_iterated = json.load(file)
        timestring = "00:00:0"
        srtfile = open(srt,"w")
        if ro_be_iterated['segments'] is not None:
            i=1
            for segment in ro_be_iterated['segments']:
                if segment['start'] >= 10:
                    timestring = "00:00:"  
                srt_line = "\n"+str(i)+"\n"+str(timestring)+str(segment['start'])+"0 --> "+str(timestring)+str(segment['end'])+"0"
                srtfile.write(srt_line+"\n")
                srtfile.write(segment['text']+"\n")
                i+=1  
            srtfile.close()

    def main(self,mp4filename,bot_token,jsonfile,srtfilename):
        #bot = telebot.TeleBot(bot_token)
        print("Started to Transcribe:")
        self.whispertranscribe(mp4filename,jsonfile)
        print("Started to create srtfile:")
        self.create_srt(jsonfile,srtfilename)
        print("Started burning:")
        # Load video and SRT file
        video = VideoFileClip(mp4filename)
        subtitles = pysrt.open(srtfilename)

        begin,end= mp4filename.split(".mp4")
        output_video_file = begin+'_subtitled'+".mp4"

        print ("Output file name: ",output_video_file)

        # Create subtitle clips
        subtitle_clips = self.create_subtitle_clips(subtitles,video.size)

        # Add subtitles to the video
        final_video = CompositeVideoClip([video] + subtitle_clips)

        # Write output video file
        final_video.write_videofile(output_video_file)
        print("Done.")
        return output_video_file

BOT_TOKEN = ""
bot = telebot.TeleBot(BOT_TOKEN)
print("Initialized...")
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
        bot.reply_to(message, "Bot is active! Send me an mp4")

@bot.message_handler(content_types=['document', 'photo', 'audio', 'video', 'voice']) # list relevant content types
def addfile(message):
    raw = message.video.file_id
    path = raw+".mp4"
    file_info = bot.get_file(raw)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(path,'wb') as new_file:
        new_file.write(downloaded_file)
    new_file.close()
    subtitle = SubtitleChef()
    subtitled_video = subtitle.main(bot_token=BOT_TOKEN,mp4filename=path,srtfilename="example.srt",jsonfile="example.json")
    bot.send_video(message.chat.id,video=open(subtitled_video, 'rb'))  
bot.infinity_polling()