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
        shop_name = item['value']['shop_name']
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

@app.route('/login', methods=['GET', 'POST'])
def index_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
        except:
            return render_template('login_signup.html', result = "not ok", msg = "Wrong Email or Password !")
        
        return redirect(url_for('users'))

    # Render the HTML form
    return render_template('login_signup.html')

@app.route('/vendor_dashboard', methods=['GET', 'POST'])
def vendor_dashboard():
    if request.method == 'POST':
        shop_name = request.form['shop_name']
        category = request.form['category']
        products = request.form['products']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        working_hour = request.form['working_hour']
        longitude = request.form['longitude']
        latitude = request.form['latitude']
        
        data = {
            "shop_name":shop_name,
            "category":category,
            "products":products,
            "phone":phone,
            "email":email,
            "address":address,
            "working_hour":working_hour,
            "longitude":longitude,
            "latitude":latitude
        }
        
        db.child('vendor').push(data)
        
        return render_template('vendor.html', result = "ok")
    return render_template('vendor.html')

@app.route('/users', methods = ['GET','POST'])
def users(): 
    current_user = auth.current_user
    email = str(current_user['email'])
    if request.method == 'POST':
        #user_ip = request.remote_addr
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        user_want = request.form['user_want']
        print(user_want)
        #if user searches for anything then it will execute
        if user_want == "":
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
            return render_template('users.html', result = "ok dialog", msg = data_json, cur_user = cur_user)
        else:        
            query = db.child("vendor").get()
            dist_key = {}
            whole_data = []
            
            train_x_data = pd.read_csv('static/train_x.csv')['restaurant'].tolist()
            train_y_data = pd.read_csv('static/train_y.csv')['restaurant'].tolist()
            
            rec_sys = recommendation.AccessoriesRecommendation(train_x_data, train_y_data)
            recommendations = rec_sys.recommend_phone(user_want)
            if recommendations:
                re = recommendations[0]
                string = re.split("\t")[0]
            else:
                string = ""
            #print(string)
            
            # Iterate through the query results
            if query.each():
                for result in query.each():
                    document_id = result.key()
                    data = result.val()
                    if data['category'] == string:
                        distance = dist_btn(data['latitude'], data['longitude'], latitude, longitude)
                        dist_key[distance] = document_id
                sorted_keys = sorted(dist_key.keys())
                for keys in sorted_keys:
                    d = db.child("vendor").child(dist_key[keys]).get()
                    value = d.val()
                    if keys > 1000:
                        dd = str(round(keys/1000,2)) +"km"
                    else:
                        dd = str(round(keys,2)) +"m"
                    dis = {"distance":dd,
                        "value":value
                        }
                    whole_data.append(dis)
            else:
                print("No documents found.")
            json_whole_data = json.dumps(whole_data)
            return render_template('users.html', result = "ok", msg = json_whole_data)
                
    # json_whole_data = json.dumps(whole_data)      
    return render_template('users.html')
        
        
        

if __name__ == '__main__':
    app.run(debug=True)
