#!/usr/bin/python

from PIL import Image, ImageDraw, ImageFont
import subprocess, re, os, sys
from tqdm import tqdm

def get_padding(string, box_width, font):
    _, _, space_len, _ = font.getbbox(" ")
    _, _, len_of_string_pixels, _ = font.getbbox(string)
    padding = (box_width - len_of_string_pixels)//space_len//2
    return padding

def add_watermark(image_path, output_path, name, border_color, text_color):
    original_image = Image.open(image_path)
    img_width, img_height = original_image.size
    watermark_layer = Image.new('RGBA', original_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_layer)
    box_width = 300 # img_width//5
    box_height = 70 # img_height//10
    # position = (img_width - box_width - 10, 10)
    position = (img_width - box_width - 10, img_height - box_height - 10)
    border_width = 2
    draw.rectangle([position[0] - border_width, position[1] - border_width,
                    position[0] + box_width + border_width,
                    position[1] + box_height + border_width],
                    outline=border_color, width=border_width) # only border
    
    watermark_layer.save("watermark_layer.png", "PNG")
    
    """
    Windows command will be (hopefully, I tried it on my lil windows 10)
    subprocess.check_output( ['powershell', '-Command', '(Get-Item "./Screenshot (1).png" ).CreationTime '] ).decode() # HAHA FINALLLY GOT IT
    """
    date_string = subprocess.check_output(['exiftool', '-CreationTime', image_path]).decode()
    # if len(date_string) < 4:
    # #     date_string = subprocess.check_output(['exiftool', '-FileModifyDate', image_path]).decode()
    if len(date_string) > 4:
        date_string = date_string[date_string.index(":")+1:].strip()
        
        datee = date_string.split()
        timee = re.search(r"[0-9]+:[0-9]+:[0-9]+", date_string)[0].split(':')
        d, m, y, H, M = datee[1], datee[2], datee[3], timee[0], timee[1]
        date = f"{y}/{m}/{d} - {H}:{M}"
        # print(date)
    else:
        date_string = subprocess.check_output(['exiftool', '-FileModifyDate', image_path]).decode()
        date_string = date_string[date_string.index(":")+1:].strip()
        datee = date_string.split(':')
        timee = re.search(r"[0-9]+:[0-9]+:[0-9]+", date_string.split()[1])[0].split(':')
        d, m, y, H, M = datee[2].split()[0], datee[1], datee[0], timee[0], timee[1]
        date = f"{y}/{m}/{d} - {H}:{M}"
        # print(date)
    
    font_size = 28 # 10 #(img_width**2 + img_height**2) //3033
    font = ImageFont.truetype("Arial.ttf", font_size)
    
    padding_name = get_padding(name, box_width, font)
    padding_date = get_padding(date, box_width, font)
    
    name_text = f"{' '*padding_name}{name}{' '*(padding_name-1)}\n"
    date_text = f"{' '*padding_date}{date}{' '*(padding_date-1)}\n" # f"{' '*padding_date}{'other info '}{' '*(padding_date-1)}\n"
    text = name_text + date_text
    draw.text(position, text, font=font, fill=text_color)
    print("hi --> ", date)
    end_result = Image.alpha_composite(original_image.convert("RGBA"), watermark_layer)
    end_result.save(output_path, "PNG")

# add_watermark('car.png', "car2.png", "Mark Pierro", 'red', 'red')

def add_watermark_middle_trans(image_path, output_path, name, color):
    original_image = Image.open(image_path)
    img_width, img_height = original_image.size
    watermark_layer = Image.new('RGBA', original_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_layer)
    
if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    def get_all_images_filenames(dir_name):
        # print(os.listdir(dir_name))
        return os.listdir(dir_name)
    dest = sys.argv[1]
    text = sys.argv[2]
    subprocess.check_call(["mkdir", '-p',  "sandbox"])
    subprocess.check_call(["mkdir", '-p',  "output"])
    subprocess.check_call(f"unzip -oq {dest} -d sandbox".split())
    
    dest_images = f"sandbox/word/media/"
    images = get_all_images_filenames(dest_images)
    print("Watermarking", len(images), "images\n")
    for img in tqdm(images):
        add_watermark(dest_images + img, dest_images + img, text, "red", "red")
    os.system(f"cd sandbox && zip output.docx -r * && mv output.docx ../output/output.docx")
    os.system("rm -rf sandbox")

    # os.system(f"rm -rf sandbox/*")
    print("\nYour watermarked document is output/output.docx --- Enjoy!\n")
