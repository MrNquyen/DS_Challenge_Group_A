import json
with open('save\\viem_gan_ruby\\viem_gan_ruby.json', 'r', encoding='utf-8') as file:
    img_json = json.load(file)
    print(img_json)