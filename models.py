from mongoengine import Document, StringField, EmailField, IntField, FloatField, BooleanField

class User(Document):
    username= StringField(max_length=255)
    email= EmailField()
    password= StringField()

class Company(Document):
    name= StringField(max_length=255)
    address= StringField()
    city= StringField(max_length=255)
    pincode= StringField(max_length=255)
    state= StringField(max_length=255)
    gst_no= StringField(min_length=15,max_length=15)
    company_in_sez= BooleanField()
    company_type= StringField(max_length=255)
    supplier_type= StringField(max_length=255)
    distance_from_andheri= StringField()
    distance_from_vasai= StringField()

class RawMaterial(Document):
    company_name = StringField(max_length=255)
    challan_no = StringField(max_length=255)
    type_ = StringField(max_length=255)
    type_ = StringField(max_length=255)
    apm_challan_no = StringField(max_length=255)
    size = StringField(max_length=255)
    quantity = StringField(max_length=255)
    purpose_for = StringField(max_length=255)
    cutting_size = StringField(max_length=255)
    cutting_weight =  StringField(max_length=255)
    order_no = StringField(max_length=255)
    order_size = StringField(max_length=255)

class Item(Document):
    item = StringField(max_length=255)
    rod_diameter = StringField(max_length=255)
    line_weight = StringField(max_length=255)
    unit_price = StringField(max_length=255)
    quantity = StringField(max_length=255)
    total = StringField(max_length=255)


class Order(Document):
    order_no = StringField(max_length=255)
    rate = StringField(max_length=255)
    items = StringField()

    