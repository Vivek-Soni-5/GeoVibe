import json
from flask import Flask, jsonify, redirect, request, render_template, url_for
import pyrebase
import math
import recommendation
import pandas as pd
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure the Flask app for sending emails using Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Default SMTP port is 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'geovibee@gmail.com'
app.config['MAIL_PASSWORD'] = 'siel wuts zfcv gbzv'
app.config['MAIL_DEFAULT_SENDER'] = 'geovibee@gmail.com'
mail = Mail(app)

firebaseConfig = {
    "apiKey": "AIzaSyDpY5pFAxuPGkHJxx8gTo7DTCdMdzh9Gxs",
    "authDomain": "ontime-37adc.firebaseapp.com",
    "databaseURL": "https://ontime-37adc-default-rtdb.firebaseio.com/",
    "projectId": "ontime-37adc",
    "storageBucket": "ontime-37adc.appspot.com",
    "messagingSenderId": "936861616079",
    "appId": "1:936861616079:web:6a327c9b741e551c9374ba",
    "measurementId": "G-1QWMD8WMHS"
  }

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()


def search(query):
    result = []
    
    # Get all vendors from the database
    vendors = db.child("vendor").get().val()
    
    # Iterate through each vendor and check if the query matches any field
    for vendor_key, vendor_data in vendors.items():
        # Check if the query matches any search prefix
        if any(prefix in query.lower() for prefix in vendor_data.get("search_prefixes", [])):
            result.append(vendor_data)
        else:
            # Check if the query matches any other field (business_name, owner_name, address, etc.)
            for field, value in vendor_data.items():
                if isinstance(value, str) and query.lower() in value.lower():
                    result.append(vendor_data)
                    break  # Break the loop if a match is found
    
    return result

#calculating distance between two location
def dist_btn(lat1, lon1, lat2, lon2):
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)
    R = 6371  # Radius of the Earth in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c

    return distance*1000

#sendig email to user whose location is nearest to vendors shop
@app.route('/send_email', methods = ['POST'])
def send_email(): 
    # Create a Message object
    flag = 0
    data = request.get_json()
    recipient = data['email']
    json_data = data['data']
    
    for item in json_data:
        shop_name = item['value']['business_name']
        email = item['value']['email']
        address = item['value']['address']
        subject = "Recommedations"
        message_body = shop_name + "\n" + "Feel free to contact: " + email + "\n" + "Address: " + address
        
        message = Message(
            subject=subject,
            recipients=[recipient],
            body=message_body
        )
        try:
            mail.send(message)
        except Exception as e:
            flag = 1
    if flag == 1:
        res = "email not sent successfully !"
        return jsonify(res)
    return jsonify("email sent successfully !")

@app.route('/contact', methods = ['POST', 'GET'])
def contact():
    return render_template('contact.html')


@app.route('/signup', methods=['GET', 'POST'])
def index_signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.create_user_with_email_and_password(email, password)
        except:
            return render_template('login_signup.html', result = "not ok", msg = "User Already Exists !")
        
        return render_template('login_signup.html', result = "ok", msg = "Account Created Successfully !")

    # Render the HTML form
    return render_template('login_signup.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        email_check = email.replace('@','_').replace('.','_')
        flag = 0
        try:
            user = auth.sign_in_with_email_and_password(email, password)
        except:
            return render_template('login_signup.html', result = "not ok", msg = "Wrong Email or Password !")
        
        
        vendor = db.child('vendor').get()
        if vendor.each():
            for v in vendor.each():
                if email_check == v.key():
                    flag = 1
        if flag == 1:
            return redirect(url_for('vendor_dashboard'))
        else:
            return redirect(url_for('users'))

    # Render the HTML form
    return render_template('login_signup.html')

@app.route('/login', methods=['GET', 'POST'])
def index_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        email_check = email.replace('@','_').replace('.','_')
        flag = 0
        try:
            user = auth.sign_in_with_email_and_password(email, password)
        except:
            return render_template('login_signup.html', result = "not ok", msg = "Wrong Email or Password !")
        
        
        vendor = db.child('vendor').get()
        if vendor.each():
            for v in vendor.each():
                if email_check == v.key():
                    flag = 1
        if flag == 1:
            return redirect(url_for('vendor_dashboard'))
        else:
            return redirect(url_for('users'))

    # Render the HTML form
    return render_template('login_signup.html')

@app.route('/forget_password', methods = ['POST', 'GET'])
def forget_password():
    if request.method == 'POST':
        email = request.form['email']
        try:
            auth.send_password_reset_email(email)
            msg = ("Password reset email sent successfully.")
            return render_template('forget_password.html', result = "ok", msg_data = msg)
        except Exception as e:
            msg = (f"Error sending password reset email: {e}")
            return render_template('forget_password.html', result = "not ok", msg_data = msg)
        
    return render_template('forget_password.html')

@app.route('/signin_anonymous', methods = ['POST', 'GET'])
def signin_phone_number():
    try:
        user = auth.sign_in_anonymous()
        print("Successfully signed in anonymously. UID:", user['localId'])
        return redirect(url_for('users'))
    except Exception as e:
        res = (f"Error signing in anonymously: {e}")
        return render_template('login_signup.html', result = "not ok", msg = res)
        


@app.route('/vendor_registration', methods=['GET', 'POST'])
def vendor_registration():
    if request.method == 'POST':
        business_name = request.form['business_name']
        category = request.form['category']
        business_description = request.form['business_description']
        phone = request.form['phone']
        email = request.form['email']
        owner_name = request.form['owner_name']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        pin_code = request.form['pin_code']
        country = request.form['country']
        longitude = request.form['longitude']
        latitude = request.form['latitude']
        password = request.form['password']
        image = request.files['file']
        
        # Generate search prefixes from the vendor name
        search_prefixes = [prefix.lower() for prefix in business_name.split()]
        
        # Upload the file to Firebase Storage
        storage.child("uploads/" + image.filename).put(image)

        # Get the download URL of the uploaded file
        image_url = storage.child("uploads/" + image.filename).get_url(None)
        
        vendor = auth.create_user_with_email_and_password(
        email=email,
        password=password
        )
        
        cleaned_email = email.replace('.', '_').replace('@', '_')
        vendor_ref = db.child('vendor').child(cleaned_email)
        vendor_ref.set({
            "business_name":business_name,
            "category":category,
            "business_description":business_description,
            "phone":phone,
            "email":email,
            "owner_name":owner_name,
            "address":address,
            "city": city,
            "state": state,
            "pin_code":pin_code,
            "country": country,
            "password": password,
            "longitude":longitude,
            "latitude":latitude,
            "image_url": image_url,
            'search_prefixes': search_prefixes
        })
        # db.child('vendor').push(data)
        return render_template('vendor.html', result = "ok")
    
    return render_template('vendor.html')

@app.route('/vendor_dashboard', methods = ['POST', 'GET'])
def vendor_dashboard():
    current_user = auth.current_user
    if current_user:
        email = str(current_user['email'])
        key = email.replace('@', '_').replace('.', '_')
        
        if request.method == 'POST':
            if 'menu_image' in request.files:
                menu_image = request.files['menu_image']
                # Upload the file to Firebase Storage
                storage.child("uploads/" + menu_image.filename).put(menu_image)
                # Get the download URL of the uploaded file
                menu_image_url = storage.child("uploads/" + menu_image.filename).get_url(None)
                current_images = db.child("vendor").child(key).child("menu_image").get().val()
                print(type(current_images))
                img_list = []
                if current_images is not None:
                    # Append the new menu_image_url to the list
                    img_list = (current_images)
                    img_list.append(menu_image_url)
                else:
                    img_list.append(menu_image_url)
                
                vendor_ref = db.child('vendor').child(key)
                vendor_ref.update({
                    "menu_image":img_list
                })
                #Displaying existing data
                vendor = db.child('vendor').child(key).get()
                value = vendor.val()
                vendor_data = dict(value)
                print(vendor_data)
                return render_template('vendor_dashboard.html', result = "initial", data = vendor_data)
            
            elif 'discount_offer' in request.form:
                discount_offer = request.form['discount_offer']
                if 'discount_description' in request.form:
                    discount_description = request.form['discount_description']
                else:
                    discount_description = "None"
                vendor_discount = db.child('vendor').child(key)
                vendor_discount.update({
                    "discount_offer":discount_offer,
                    "discount_description":discount_description
                })
                #Displaying existing data
                vendor = db.child('vendor').child(key).get()
                value = vendor.val()
                vendor_data = dict(value)
                return render_template('vendor_dashboard.html', result = "initial", data = vendor_data)
        
        #Displaying existing data
        vendor = db.child('vendor').child(key).get()
        value = vendor.val()
        vendor_data = dict(value)
        return render_template('vendor_dashboard.html', result = "initial", data = vendor_data)
    else:
        return redirect(url_for('index_login'))
        

@app.route('/dialog_box', methods = ['POST', 'GET'])
def dialog_box():
    current_user = auth.current_user
    if current_user:
        email = str(current_user['email'])
        if request.method == 'POST':
            #user_ip = request.remote_addr
            latitude = request.form['latitude']
            longitude = request.form['longitude']

            # # Assuming data contains latitude and longitude
            # latitude = data.get('latitude')
            # longitude = data.get('longitude')
            
            whole_vendor_data = []
            query_all_vendor = db.child("vendor").get()
            if query_all_vendor.each():
                for result in query_all_vendor.each():
                    document_id = result.key()
                    data = result.val()
                    distance = dist_btn(data['latitude'], data['longitude'], latitude, longitude)
                    print(distance)
                    distance_radius = 1000
                    if distance <= distance_radius:
                        dd = {
                            "distance":distance,
                            "value":data
                        }
                        #msg = data['shop_name'] + "\n" + "feel free to contact: " + data['email'] + "\n" + "Address: " + data['address'] +"\n"
                        #send_email(current_user['email'], "Recommendations", msg)
                        whole_vendor_data.append(dd)
            json_whole_vendor_data = json.dumps(whole_vendor_data)
            data_json = json.loads(json_whole_vendor_data)
            r = json.dumps(email)
            cur_user = json.loads(r)
            return jsonify({'result': 'ok dialog', 'msg': data_json, 'cur_user': cur_user})
        
@app.route('/users', methods = ['GET','POST'])
def users():  
    current_user = auth.current_user
    flag = 0
    if current_user:
        if 'email' in current_user:       
            email = str(current_user['email'])
        else:
            flag = 1
        if request.method == 'POST':
            #user_ip = request.remote_addr
            
            # print("latitude:", latitude)
            
            # print(user_want)
            #if user searches for anything then it will execute
            if "logout" in request.form:
                return redirect(url_for('index_login'))
            elif "notification" in request.form:
                latitude = request.form['Nlatitude']
                longitude = request.form['Nlongitude']
                whole_vendor_data = []
                query_all_vendor = db.child("vendor").get()
                if query_all_vendor.each():
                    for result in query_all_vendor.each():
                        document_id = result.key()
                        data = result.val()
                        distance = dist_btn(data['latitude'], data['longitude'], latitude, longitude)
                        print(distance)
                        if distance > 1000:
                            ddd = str(round(distance/1000,2)) +" km"
                        else:
                            ddd = str(round(distance/1000,2)) +" km"
                        distance_radius = 1000
                        if distance <= distance_radius:
                            dd = {
                                "distance":ddd,
                                "value":data
                            }
                            #msg = data['shop_name'] + "\n" + "feel free to contact: " + data['email'] + "\n" + "Address: " + data['address'] +"\n"
                            #send_email(current_user['email'], "Recommendations", msg)
                            whole_vendor_data.append(dd)
                json_whole_vendor_data = json.dumps(whole_vendor_data)
                data_json = json.loads(json_whole_vendor_data)
                
                if flag == 0:
                    r = json.dumps(email)
                    cur_user = json.loads(r)
                    return render_template('users.html', result = "ok dialog", msg = data_json, cur_user = cur_user)
                elif flag == 1:
                    r = json.dumps("null")
                    cur_user = json.loads(r)
                    return render_template('users.html', result = "ok dialog", anonymous = "yes", msg = data_json, cur_user = "Anonymous")
                # return jsonify({'result': 'ok dialog', 'msg': data_json, 'cur_user': cur_user})
            else :
                latitude = request.form['latitude']
                longitude = request.form['longitude']
                user_want = request.form['user_want']        
                query = db.child("vendor").get()
                dist_key = {}
                whole_data = []
                
                # train_x_data = pd.read_csv('static/train_x.csv')['restaurant'].tolist()
                # train_y_data = pd.read_csv('static/train_y.csv')['restaurant'].tolist()
                
                # rec_sys = recommendation.AccessoriesRecommendation(train_x_data, train_y_data)
                # recommendations = rec_sys.recommend_phone(user_want)
                # if recommendations:
                #     re = recommendations[0]
                #     string = re.split("\t")[0]
                # else:
                #     string = ""
                #print(string)
                # string = ""
                
                
                #searching through business name
                # Get all vendors from the database
                vendors = db.child("vendor").get().val()
                # Iterate through each vendor and check if the query matches any field
                for vendor_key, vendor_data in vendors.items():
                #     # Check if the query matches any search prefix
                #     if any(prefix in user_want.lower() for prefix in vendor_data.get("search_prefixes", [])):
                #         distance_prefixes = dist_btn(vendor_data['latitude'], vendor_data['longitude'], latitude, longitude)
                #         if distance_prefixes > 1000:
                #             dd = str(round(distance_prefixes/1000,2)) +"km"
                #         else:
                #             dd = str(round(distance_prefixes/1000,2)) +"km"
                #         dsds = {
                #             "distance":dd,
                #             "value":vendor_data
                #         }
                #         whole_data.append(dsds)
                #     else:
                        # Check if the query matches any other field (business_name, owner_name, address, etc.)
                    for field, value in vendor_data.items():
                        user_want_split = user_want.split(' ')
                        for user in user_want_split:
                            if isinstance(value, str) and user.lower() in value.lower():
                                distance_prefixes = dist_btn(vendor_data['latitude'], vendor_data['longitude'], latitude, longitude)
                                if distance_prefixes > 1000:
                                    dd = str(round(distance_prefixes/1000,2)) +" km"
                                else:
                                    dd = str(round(distance_prefixes/1000,2)) +" km"
                                dsds = {
                                    "distance":dd,
                                    "value":vendor_data
                                }
                                if dsds not in whole_data:
                                    whole_data.append(dsds)
                                break  # Break the loop if a match is found
                
                # Iterate through the query results (AI search )
                # if query.each():
                #     for result in query.each():
                #         document_id = result.key()
                #         data = result.val()
                #         if data['category'] == string:
                #             distance = dist_btn(data['latitude'], data['longitude'], latitude, longitude)
                #             dist_key[distance] = document_id
                #     sorted_keys = sorted(dist_key.keys())
                #     for keys in sorted_keys:
                #         d = db.child("vendor").child(dist_key[keys]).get()
                #         value = d.val()
                #         if keys > 1000:
                #             dd = str(round(keys/1000,2)) +"km"
                #         else:
                #             dd = str(round(keys,2)) +"m"
                #         dis = {"distance":dd,
                #             "value":value
                #             }
                #         whole_data.append(dis)
                # else:
                #     print("No documents found.")
                # json_whole_data = json.dumps(whole_data)
                sorted_whole_data = sorted(whole_data, key = lambda x: x['distance'])
                if flag == 0:
                    r = json.dumps(email)
                    cur_user = json.loads(r)
                else:
                    r = json.dumps("Anonymous")
                    cur_user = json.loads(r)
                return render_template('users.html', result = "ok", msg = sorted_whole_data, cur_user = cur_user)
    else:
        return redirect(url_for('index_login'))            
    # json_whole_data = json.dumps(whole_data)
    if 'email' in current_user:      
        return render_template('users.html', cur_user = current_user['email'])
    else:
        return render_template('users.html', cur_user = "Anonymous")

@app.route('/detail_page', methods = ['POST', 'GET'])
def detail_page():
    # Get the business_id parameter from the URL
    if request.method == 'POST':
        user_want = request.form['user_want']
        if user_want == 'logout':
            return redirect(url_for('index_login'))
    
    business_email = request.args.get('business_email')
    distance = request.args.get('distance')
    cur_user = request.args.get('current_user')
    key = business_email.replace('@','_').replace('.','_')
    print(key)
    vendors = db.child('vendor').child(key).get()
    value = vendors.val()
    print(type(value))
    result = {
        "distance": distance,
        "value": dict(value)
    }
    data = []
    data.append(result)
    print(data)
    return render_template('detail_page.html', result = "ok", msg = data, cur_user = cur_user)
        
@app.route('/direction', methods = ['POST', 'GET'])
def direction():
    # Get the business_id parameter from the URL
    business_email = request.args.get('business_email')
    distance = request.args.get('distance')
    key = business_email.replace('@','_').replace('.','_')
    print(key)
    vendors = db.child('vendor').child(key).get()
    value = vendors.val()
    print(type(value))
    result = {
        "distance": distance,
        "value": dict(value)
    }
    data = []
    data.append(result)
    print(data)
    return render_template('direction.html', result = "ok", msg = data)
        

if __name__ == '__main__':
    app.run(debug=True)
