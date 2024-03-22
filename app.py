from flask import Flask, jsonify, request, render_template
from models import User, Company, RawMaterial, Item, Order
from mongoengine import connect
from flask_cors import CORS
import json
import hashlib
import re

def isValidMasterCardNo(str):

   
    regex = "^[0-9]{2}[A-Z]{5}[0-9]{4}" + "[A-Z]{1}[1-9A-Z]{1}" +  "Z[0-9A-Z]{1}$"

    p = re.compile(regex)
    if (str == None):
        return False
    if(re.search(p, str)):
        return True
    else:
        return False


app = Flask(__name__)
with open('config.json') as config_file:
    config = json.load(config_file)
# connect(host="mongodb+srv://{username}:{password}@{dbName}/?retryWrites=true&w=majority".format(username=config['database_username'],password=config['database_password'],dbName=config['database_server']),db="ims")
connect(host='mongodb://localhost:27017/stock-and-inventory')
@app.route('/')
def index():
    return jsonify({"status":"working"}),200


# User routes 

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST' and request.headers.get('source-name') == 'streamlining-inventory-management':
        data = request.get_json(force=True)
        existing_users_by_username = User.objects(username=data['username'])
        if not data['username'] or not data['password']:
            return jsonify({'message': 'Username and password are required'}), 400
        if existing_users_by_username:
            return jsonify({"result":"User already exists"}),409
        user = User(username=data['username'],name=data['name'], password=hashlib.md5(data['password'].encode()).hexdigest())
        result = user.save()
        if result:
            return jsonify({"status":"success"}), 201
    else:
        return jsonify({'res':'Request cannot be processed'}),406 

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST' and request.headers.get('source-name') == 'streamlining-inventory-management':
        data = request.get_json(force=True)
        user = User.objects(username=data['username'],password=hashlib.md5(data['password'].encode()).hexdigest())       
        if not data['username'] or not data['password']:
            return jsonify({'message': 'Username and password are required'}), 400
        if user:
            return jsonify({'username':user[0]['username']}),200 
        else:
            return {"result":"Invalid username or password"},401 
    else:
       return jsonify({'res':'Request cannot be processed'}),406    

@app.route('/delete-user', methods=['POST'])
def delete_user():
    if request.method == 'POST' and request.headers.get('source-name') == 'streamlining-inventory-management':
        data = request.get_json(force=True)
        if data['username']:
            user = User.objects(username=data['username'])
            user[0].delete()
            return jsonify({"status":"sucesss"}),202
        else: 
            return jsonify({"status":"not found"}),404

    return jsonify({'res':'Request cannot be processed'}),406


@app.route('/edit-user', methods=['POST'])
def edit_user():
    if request.method == 'POST' and request.headers.get('source-name') == 'streamlining-inventory-management':
        data = request.get_json(force=True)
        if data['username']:
            user = User.objects(username=data['username']).first()
            if data['new_username']:
                user.username = data['new_username']
                user.save()
                return jsonify({"status":"sucesss"}),200
            if data['new_password']:
                user.password = hashlib.md5(data['new_password'].encode()).hexdigest()
                user.save()
                return jsonify({"status": "successs"}), 200
            if data['new_name']:
                user.name = data['new_name']
                user.save()
                return jsonify({"status": "successs"}), 200
                    
    else: 
        return jsonify({'res':'Request cannot be processed'}),406

        

    
# Company routes
@app.route('/company')  
def get_company():
    all_companies = Company.objects
    companies = []
    for company in all_companies:
        companies.append(dict({"uuid": company.uuid, "name": company.name })) 
    return jsonify({"companies": companies})

@app.route('/company/<name>', methods = ['GET','POST'])  
def specific_company(name):
    if request.method == 'GET':
        company = (Company.objects(name=name))
        company_name = {
                "uuid" : company[0].uuid,
                "name" : company[0].name,
                "address": company[0].address,
                    "city": company[0].city,
                    "pincode":  company[0].pincode,
                    "state": company[0].state,
                    "gst_no": company[0].gst_no,
                    "company_in_sez": company[0].company_in_sez,
                    "company_type": company[0].company_type,
                    "supplier_type": company[0].supplier_type,
                    "distance_from_andheri": company[0].distance_from_andheri,
                    "distance_from_vasai": company[0].distance_from_vasai
                }
        return jsonify(company_name)
    if request.method == 'POST':
        data = request.get_json(force=True)
        if type(data) == type("s"):
            data = json.loads(data)
        company = Company.objects(name=data['name'])
        try:
            company[0].delete()
            return jsonify({"status":"working"}),200
        except:
            return jsonify({"Status":"Not found"}),404

@app.route('/add-company',methods=['POST'])
def add_company():
    if request.method == 'POST' and request.headers.get('source-name') == 'streamlining-inventory-management':
        data = request.get_json(force=True)      
        if type(data) is type("s"):
            data = json.loads(data)
        company_by_name = Company.objects(name=data['name'])
        company_by_gst = Company.objects(gst_no=data['gst_no'])
        if company_by_gst or company_by_name:
            return jsonify({"result":"Company already exists"}),409
        elif len(data['gst_no']) != 15 or (isValidMasterCardNo(data['gst_no']) is False):
            return jsonify({"result": "Invalid gst no"}), 422
        else:
            result = Company(
                    name=data['name'],
                    address= data['address'],
                    city= data['city'],
                    pincode= data['pincode'],
                    state= data['state'],
                    gst_no= data['gst_no'],
                    company_in_sez= data['company_in_sez'],
                    company_type= data['company_type'],
                    supplier_type= data['supplier_type'],
                    distance_from_andheri= data['distance_from_andheri'],
                    distance_from_vasai= data['distance_from_vasai']
                    ).save()
            return jsonify({"status":"success"}), 201


@app.route('/remove-company', methods=['POST'])
def remove_company():
    if request.method == 'POST' and request.headers.get('source-name') == 'streamlining-inventory-management':
        data = request.get_json(force=True)
        if data['name']:
            company = Company.objects(name=data['name'])
            company[0].delete()
            return jsonify({"status":"sucesss"}),202
        elif data['gst_no']:
            company = Company.objects(gst_no=data['gst_no'])  
            company[0].delete()
            return jsonify({"status":"sucesss"}),202
        else:
            return jsonify({"status":"not found"}),404



# Raw material routes
@app.route('/raw-material', methods=['GET'])
def get_materials():
    if request.method == 'GET' and request.arg.get('uuid'):
        raw_material = RawMaterial.objects(uuid=str(request.arg.get('uuid')))
        json_res = {'uuid' : raw_material.uuid, 'stage':3, 'quantity' : raw_material.quantity, 'completed_quantity': raw_material.completed_quantituy, 'size' : raw_material.size}
    if request.method == 'GET':
        all_raw_materials = RawMaterial.objects
        raw_materials = []
        for raw_material in all_raw_materials:
            raw_materials.append(dict({"uuid": raw_material.uuid, "name": raw_material.item_name, "size" : raw_material.size
                })) 
        return jsonify({"raw_materials": raw_materials})

@app.route('/raw-material/<name>')  
def get_specific_material(name):
    raw_material = (RawMaterial.objects(item_name=name))
    raw_material_name = {
            "uuid" : raw_material[0].uuid,
            "name" : raw_material[0].item_name
            }
    return jsonify(raw_material_name)


@app.route('/add-material', methods=['POST'])
def add_material():
    if request.method == 'POST' and request.headers.get('source-name') == 'streamlining-inventory-management':
        data = request.get_json()
        if type(request.get_json()) is str:
            data = json.loads(data)
        RawMaterial(
                company_name = data['company_name'],
                challan_no = data['challan_no'],
                type_ = data['type'],
                apm_challan_no = data['apm_challan_no'],
                size = data['size'],
                quantity = data['quantity'],
                purpose_for = data['purpose_for'],
                cutting_size = data['cutting_size'],
                cutting_weight = data['cutting_weight'],
                order_no= data['order_no'],
                order_size = data['order_size'],
                stage = data['stage']
              ).save()
        return jsonify({"status":"success"}), 201
    return jsonify({'res':'Request cannot be processed'}),406

@app.route('/remove-material', methods=['POST'])
def remove_material():
    if request.method == 'POST' and request.headers.get('source-name') == 'streamlining-inventory-management':
        data = request.get_json(force=True)
        if data['item_name']:
            user = RawMaterial.objects(item_name=data['item_name'])
            user[0].delete()
            return jsonify({"status":"sucesss"}),202
        else:
            return jsonify({"status":"not found"}),404
        

@app.route('/add-item', methods=['POST'])
def add_item():
    if request.method == 'POST' and request.headers.get('source-name') == 'streamlining-inventory-management':
        data = request.get_json(force=True)
        if type(data) is type(' '):
            data = json.loads(data)
        result = Item(
                item = data['item'],
                rod_diameter = data['rod_diameter'],
                #line_weight = data['line_weight'],
                unit_price = data['unit_price'],
                quantity = data['quantity'],
                total = data['total']
                ).save()
        return jsonify({"status": "success"}), 201


@app.route('/item', methods=['GET'])
def get_items():
    if request.method == 'GET':
        all_orders = Order.objects
        print(all_orders)
        all_items = []
        for order in all_orders:
            items = order.items
            order_no = order.order_no
            order_items = json.loads(items)
            for item in order_items:
                single_item = {'uuid': item['uuid'], 'item_name': item['item_name'], 'stage':  item['stage'], 'order_no': order_no, 'total_quantity': item['quantity']}
                all_items.append(single_item)
        return jsonify({"Items": all_items}), 200

@app.route('/add-order', methods=['POST'])
def add_order():
    if request.method == 'POST' and request.headers.get('source-name') == 'streamlining-inventory-management':
        data = request.get_json(force=True)
        if type(data) is type(" "):
            data = json.loads(data)
        result = Order(
           # company_name = data['company_name'],
            order_no = data['order_no'],
            rate= data['rate'],
            items= str(data['items'])
                ).save()
        if result:
            return jsonify({'Status': "success"}), 201
        

@app.route('/orders', methods=['GET'])
def get_orders():
    if request.method == 'GET':
        all_orders = Order.objects
        orders = []
        for order in all_orders:
            new_order = {'uuid': order.uuid, 'order_no': order.no}        
            orders.append(new_order)
        return jsonify({"orders": orders})
    
@app.route('/users', methods=['GET'])
def get_users():
    if request.method == 'GET':
        all_users = User.objects
        users = []
        for user in all_users:
            new_user = {'uuid': user.uuid, 'username': user.username, 'name': user.name}
            users.append(new_user)
        return jsonify({"Users": users})
    
@app.route('/track')
def track():
    return render_template("track.html")
