import json
from flask import Flask, render_template, request, jsonify
import random
import base64
import string
from vercel_storage import blob
from dotenv import load_dotenv
import requests
import time
from threading import Thread

load_dotenv()
app = Flask(__name__)
items = json.load(open('isaacle_c.json'))
selected_items = []

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        
def random_by_colors(items, num):
    if num == 16:
        cols = ['Transparent', 'Yellow', 'Green', 'Gray', 'Purple', 'Orange', 'Red', 'Black', 'Pink', 'Brown', 'Blue', 'White']
    elif num == 25:
        cols = ['Transparent', 'Yellow', 'Green', 'Gray', 'Purple', 'Red', 'Black', 'Pink', 'Brown', 'Blue', 'White']
    elif num == 36:
        cols = ['Yellow', 'Green', 'Gray', 'Purple', 'Red', 'Black', 'Pink', 'Brown', 'Blue', 'White']
    elif num == 49:
        cols = ['Yellow', 'Gray', 'Red', 'Black', 'Pink', 'Brown', 'Blue', 'White']
    elif num == 64:
        cols = ['Yellow', 'Gray', 'Red', 'Black', 'Pink', 'Brown', 'Blue', 'White']
    
    items_color = []
    color = random.choice(cols)
    for i in items:
        for cols in i['Colors']:
            if color in cols:
                items_color.append(i)
                break
    res = random.sample(items_color, num)
    return(res, color)

def random_by_release(items, num):
    dlc_list = ['Repentance', 'Afterbirth+', 'Rebirth', 'Flash', 'Afterbirth']
    items_dlc = []
    dlc = random.choice(dlc_list)
    for i in items:
        currentdlc = i['Release']
        if currentdlc == dlc:
            items_dlc.append(i)
                
    res = random.sample(items_dlc, num)
    return(res, dlc)

def random_by_type(items, num):
    type_list = ['Active', 'Passive']
    items_typ = []
    typ = random.choice(type_list)
    for i in items:
        currenttyp = i['Type']
        if currenttyp == typ:
            items_typ.append(i)
    res = random.sample(items_typ, num)
    return(res, typ)

def random_by_quality(items, num):
    if num == 16:
        qual_list = [0, 1, 2, 3, 4]
    elif num == 25:
        qual_list = [0, 1, 2, 3, 4]
    elif num == 36:
        qual_list = [0, 1, 2, 3, 4]
    elif num == 49:
        qual_list = [0, 1, 2, 3]
    elif num == 64:
        qual_list = [1, 2, 3]
    
    items_qual = []
    qual = random.choice(qual_list)
    for i in items:
        currentqual = i['Quality']
        if currentqual == qual:
            items_qual.append(i)
                
    res = random.sample(items_qual, num)
    return(res, f"Qual {qual}")

def random_by_pool(items, num):
    if num == 16:
        pool_list = ['Secret Room', 'Angel Room', 'Curse Room', 'Golden Chest', 'Baby Shop', 'Item Room', 'Boss Room', 'Crane Game', 'Shop', 'Devil Room', 'UltraSecretRoom']
    elif num == 25:
        pool_list = ['Secret Room', 'Angel Room', 'Curse Room', 'Golden Chest', 'Baby Shop', 'Item Room', 'Boss Room', 'Crane Game', 'Shop', 'Devil Room', 'UltraSecretRoom']
    elif num == 36:
        pool_list = ['Secret Room', 'Angel Room', 'Baby Shop', 'Item Room', 'Boss Room', 'Crane Game', 'Shop', 'Devil Room', 'UltraSecretRoom']
    elif num == 49:
        pool_list = ['Secret Room', 'Angel Room', 'Baby Shop', 'Item Room', 'Boss Room', 'Crane Game', 'Shop', 'Devil Room', 'UltraSecretRoom']
    elif num == 64:
        pool_list = ['Angel Room', 'Baby Shop', 'Item Room', 'Crane Game', 'Shop', 'Devil Room', 'UltraSecretRoom']
    
    items_pool = []
    pool = random.choice(pool_list)
    for i in items:
        for pools in i['Item Pool']:
            if pool in pools:
                items_pool.append(i)
                break
    res = random.sample(items_pool, num)
    return(res, pool)

def sel_by_colors(items, color, num):
    items_color = []
    for i in items:
        for cols in i['Colors']:
            if color in cols:
                items_color.append(i)
                break
    res = random.sample(items_color, num)
    return(res, color)

def sel_by_release(items, dlc, num):
    items_dlc = []
    for i in items:
        currentdlc = i['Release']
        if currentdlc == dlc:
            items_dlc.append(i)
                
    res = random.sample(items_dlc, num)
    return(res, dlc)

def sel_by_quality(items, qual, num):
    qual = int(qual)
    items_qual = []
    for i in items:
        currentqual = i['Quality']
        if currentqual == qual:
            items_qual.append(i)
                
    res = random.sample(items_qual, num)
    return(res, f"Qual {qual}")

def sel_by_pool(items, pool, num):
    items_pool = []
    for i in items:
        for pools in i['Item Pool']:
            if pool in pools:
                items_pool.append(i)
                break
    res = random.sample(items_pool, num)
    return(res, pool)


def sel_by_type(items, typ, num):
    items_typ = []
    for i in items:
        currenttyp = i['Type']
        if currenttyp == typ:
            items_typ.append(i)
    res = random.sample(items_typ, num)
    return(res, typ)

def full_random(items, num):
    res = random.sample(items, num)
    return(res, "Random")

def backup():
    files = blob.list(options={})
    file = ""
    
    for file in files['blobs']:
        if file['pathname'] == "gamecodes.json":
            file = file['url']
            break
    res = blob.copy(file, f"backup/{time.time()}-gamecodes.json", options={})
    return f"Backup done {res['pathname']}"

def easycode(code):
    files = blob.list(options={})
    file = ""
    
    for file in files['blobs']:
        if file['pathname'] == "gamecodes.json":
            file = file['url']
            break
    response = requests.get(file)
    codes = response.json()
    # codes = json.load(f)
    if code in codes:
        return(codes[code])
    else:
        return("Code not found")

def get_key_from_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None

def backup_auto():
    while True:
        print(backup())
        time.sleep(43200)

def createeasycode(code):
    files = blob.list(options={})
    file = ""
    for file in files['blobs']:
        if file['pathname'] == "gamecodes.json":
            file = file['url']
            break
    response = requests.get(file)
    codes = response.json()

    if code in codes.values():
        return(get_key_from_value(codes, code))
    else:
        random_string = ''.join([random.choice(string.ascii_letters + string.digits ) for n in range(8)])
        codes[random_string] = code
        try:
            blob.put("gamecodes.json",json.dumps(codes, indent=4), options={})
            blob.delete(file, options={})
            return random_string
        except:
            print("Error when uploading.")
            return code

        

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/back')
def back():
    res = backup()
    return render_template('index.html', help=res)

@app.route('/rand', methods=['POST'])
def rand():
    grid_side = int(request.form.get('gridsizesel'))
    rules = request.form.get('rulessel')
    if rules == " ":
        return render_template('index.html', help="Please set random criteria")
    grid_size = grid_side * grid_side
    item_thumb = []
    item_name = []
    code = [grid_side]
    if rules == "colors":
        lst, rf = random_by_colors(items, grid_size)
    elif rules == "release":
        lst, rf = random_by_release(items, grid_size)
    elif rules == "quality":
        lst, rf = random_by_quality(items, grid_size)
    elif rules == "rnd":
        lst, rf = full_random(items, grid_size)
    elif rules == "type":
        lst, rf = random_by_type(items, grid_size)
    elif rules == "pool":
        lst, rf = random_by_pool(items, grid_size)

    code.append(rf)
    for i in lst:
        item_thumb.append(i['Thumb'])
        item_name.append(i['Name'])
        code.append(hex(i['ID'])[2:])
    code = json.dumps(code, separators=(',', ':')).replace('"','')[1:-1]
    enc_code = base64.b64encode(code.encode()).decode()
    enc_code = createeasycode(enc_code)
    global selected_items
    selected_items=item_name
    return render_template('game.html', item_thumb=item_thumb, item_name=item_name, code=enc_code, grid_size=grid_size, grid_side=grid_side, rf=rf)

@app.route('/custom', methods=['POST'])
def custom():
    grid_side = int(request.form.get('gridsizesel'))
    grid_size = grid_side * grid_side
    item_thumb = []
    item_name = []
    code = [grid_side]
    lst, rf = random_by_colors(items, grid_size)
    code.append(rf)
    for i in lst:
        item_thumb.append(i['Thumb'])
        item_name.append(i['Name'])
        code.append(hex(i['ID'])[2:])
    code = json.dumps(code, separators=(',', ':')).replace('"','')[1:-1]
    enc_code = base64.b64encode(code.encode()).decode()
    enc_code = createeasycode(enc_code)
    global selected_items
    selected_items=item_name
    return render_template('custom.html', item_thumb=item_thumb, item_name=item_name, code=enc_code, grid_size=grid_size, grid_side=grid_side, rf=rf)

@app.route('/code', methods=['POST'])
def code():
    item_thumb = []
    item_name = []
    old = False
    try:
        ezkod = False
        code = request.form.get('code')
        if len(code) == 8:
            ezkod = code
            code = easycode(code)

        if code[:2] == 'ch' and code[-2:] == 'og':
            numid_list = base64.b64decode(code[2:-2]).decode()
            old = True
        else:
            numid_list = base64.b64decode(code).decode()
            numid_list = '["' + numid_list.replace(",",'","') + '"]'


        numid_list = json.loads(numid_list)
        
        grid_side = int(numid_list[0])
        rf = numid_list[1]
        numid_list = numid_list[2:]
        grid_size = grid_side * grid_side

        if not old:
            numid_list = [int(i, 16) for i in numid_list]
        
        new_code = [grid_side]
        new_code.append(rf)

        for i in numid_list:
            for item in items:
                if item['ID'] == i:
                    item_thumb.append(item['Thumb'])
                    item_name.append(item['Name'])
                    new_code.append(hex(i)[2:])
        if not ezkod:
            new_code = json.dumps(new_code, separators=(',', ':')).replace('"','')[1:-1]
            enc_code = base64.b64encode(new_code.encode()).decode()
            enc_code = createeasycode(enc_code)
        else:
            enc_code = ezkod
        global selected_items
        selected_items=item_name
        return render_template('game.html', item_thumb=item_thumb, item_name=item_name, code=enc_code, grid_size=grid_size, grid_side=grid_side, rf=rf)
    except ValueError:
        return render_template('index.html', help="Invalid code")
    except Exception as e:
        return render_template('index.html', help=f"Error code: {e}")

@app.route('/mode', methods=['POST'])
def mode():
    grid_side = int(request.form.get('gridsizesel'))
    rules = request.form.get('rulessel')
    opts = request.form.get('options')
    grid_size = grid_side * grid_side
    item_thumb = []
    item_name = []
    code = [grid_side]
    if rules == " ":
        return render_template('index.html', help="Please set mode")
    
    if rules == "colors":
        lst, rf = sel_by_colors(items, opts, grid_size)
    elif rules == "release":
        lst, rf = sel_by_release(items, opts, grid_size)
    elif rules == "quality":
        if opts == '0' and grid_size == 64:
            return render_template('index.html', help="Not enough items with selected quality for that grid")
        elif opts == '4' and grid_size == 49:
            return render_template('index.html', help="Not enough items with selected quality for that grid")
        elif opts == '4' and grid_size == 64:
            return render_template('index.html', help="Not enough items with selected quality for that grid")
        lst, rf = sel_by_quality(items, opts, grid_size)
    elif rules == "pool":
        num = grid_size
        if num == 16:
            pool_list = ['Secret Room', 'Angel Room', 'Curse Room', 'Golden Chest', 'Baby Shop', 'Item Room', 'Boss Room', 'Crane Game', 'Shop', 'Devil Room', 'UltraSecretRoom']
        elif num == 25:
            pool_list = ['Secret Room', 'Angel Room', 'Curse Room', 'Golden Chest', 'Baby Shop', 'Item Room', 'Boss Room', 'Crane Game', 'Shop', 'Devil Room', 'UltraSecretRoom']
        elif num == 36:
            pool_list = ['Secret Room', 'Angel Room', 'Baby Shop', 'Item Room', 'Boss Room', 'Crane Game', 'Shop', 'Devil Room', 'UltraSecretRoom']
        elif num == 49:
            pool_list = ['Secret Room', 'Angel Room', 'Baby Shop', 'Item Room', 'Boss Room', 'Crane Game', 'Shop', 'Devil Room', 'UltraSecretRoom']
        elif num == 64:
            pool_list = ['Angel Room', 'Baby Shop', 'Item Room', 'Crane Game', 'Shop', 'Devil Room', 'UltraSecretRoom']

        if opts in pool_list:
            lst, rf = sel_by_pool(items, opts, grid_size)
        else:
            return render_template('index.html', help="Not enough items with selected quality for that grid")

    elif rules == "type":
        lst, rf = sel_by_type(items, opts, grid_size)


    code.append(rf)
    for i in lst:
        item_thumb.append(i['Thumb'])
        item_name.append(i['Name'])
        code.append(hex(i['ID'])[2:])
    code = json.dumps(code, separators=(',', ':')).replace('"','')[1:-1]
    enc_code = base64.b64encode(code.encode()).decode()
    enc_code = createeasycode(enc_code)
    global selected_items
    selected_items=item_name
    return render_template('game.html', item_thumb=item_thumb, item_name=item_name, code=enc_code, grid_size=grid_size, grid_side=grid_side, rf=rf)


@app.route('/update_selected_option', methods=['POST'])
def update_selected_option():
    selected_option = request.form.get('selected_option')
    return render_template('index.html', selected_rule=selected_option)

@app.route('/edit', methods=['POST'])
def edit():
    new_item = request.form.get('newName')

    for i in items:
        if i['Name'] == new_item:
            new_url = i['Thumb']
            break
    if new_url is None:
        return 0
    return jsonify({'newName': new_item, 'newUrl': new_url})

@app.route('/donecustom', methods=['POST'])
def submit():
    item_name = json.loads(request.form.get('titleValues'))
    grid_side=int(item_name[0][0])
    grid_size=grid_side*grid_side
    item_name = item_name[1:]
    item_thumb = []
    rf="Custom"
    code=[grid_side]
    code.append(rf)
    for i in item_name:
        for j in items:
            if j['Name'] == i:
                item_thumb.append(j['Thumb'])
                code.append(hex(j['ID'])[2:])
    
    code = json.dumps(code, separators=(',', ':')).replace('"','')[1:-1]
    enc_code = base64.b64encode(code.encode()).decode()
    enc_code = createeasycode(enc_code)
    global selected_items
    selected_items=item_name
    return render_template('game.html', item_thumb=item_thumb, item_name=item_name, code=enc_code, grid_size=grid_size, grid_side=grid_side, rf=rf)

@app.route('/list')
def list():
    item_names = []
    item_thumbs = []
    for i in items:
        item_names.append(i['Name'])
        item_thumbs.append(i['Thumb'])
    itemlen = len(item_names)
    return render_template('list.html', item_names=item_names, item_thumbs=item_thumbs, itemlen=itemlen)

@app.route('/get_description_list')
def get_description_list():
    description_list = []
    names_list = []
    items_now = []
    for i in selected_items:
        for j in items:
            if i == j['Name']:
                items_now.append(j)
                break
    for i in items_now:
        pools = ""
        colors = ""
        for pool in i['Item Pool']:
            pools+=f"{pool}, "
        for color in i['Colors']:
            colors+=f"{color}, "
        pools=pools[:-2]
        colors=colors[:-2]
        description_list.append(f'"{i["Quote"]}"\nQuality: {i["Quality"]}\nType: {i["Type"]}\nRelease: {i["Release"]}\nUnlock: {i["Unlock"]}\nPool: {pools}\nColors: {colors}') #\n---\nNormal colors: {i["OldColors"]}
        names_list.append(i['Name'])
    return jsonify({'description_list': description_list, 'names_list': names_list})

if __name__ == '__main__':
    Thread(target=backup_auto).start()
    app.run()