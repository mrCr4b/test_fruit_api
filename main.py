from sqlalchemy import Boolean, DateTime, Integer, LargeBinary
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, fields, marshal_with
from flask import Flask, redirect, url_for, render_template, request, session
from datetime import datetime, timedelta
import base64

app = Flask(__name__)
api = Api(app)
app.secret_key = 'hola'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/proj_py'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://uoexdjffbgmyt7li:3uR8bghc5iTVqkQCLbLs@barkpver6ovbbjugzkkz-mysql.services.clever-cloud.com:3306/barkpver6ovbbjugzkkz'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

db = SQLAlchemy(app)

class tai_khoan(db.Model):
    id_tai_khoan = db.Column(Integer, primary_key=True, nullable=False)
    ten_dang_nhap = db.Column(db.String(50), nullable=False)
    mat_khau = db.Column(db.String(50), nullable=False)
    phan_quyen = db.Column(Integer, nullable=False)
    khoa = db.Column(Integer, nullable=False)
    
class san_pham(db.Model):
    id_san_pham = db.Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    ten_san_pham = db.Column(db.String(50), nullable=False)
    gia_tien = db.Column(Integer, nullable=False)
    hinh_anh = db.Column(LargeBinary, nullable=False)
    
class gio_hang(db.Model):
    id_gio_hang = db.Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    id_tai_khoan = db.Column(Integer, index=True, nullable=False)
    ten_san_pham = db.Column(db.String(50), nullable=False)
    so_luong = db.Column(Integer, nullable=False)
    so_tien = db.Column(Integer, nullable=False)
    
class hoa_don(db.Model):
    id_hoa_don = db.Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    id_tai_khoan = db.Column(Integer, index=True, nullable=False)
    ngay_tao = db.Column(DateTime, index=True, nullable=False)
    tong_tien = db.Column(Integer, nullable=False)
    
class chi_tiet_hoa_don(db.Model):
    id_chi_tiet_hoa_don = db.Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    id_hoa_don = db.Column(Integer, index=True, nullable=False)
    ten_san_pham = db.Column(db.String(50), nullable=False)
    so_luong = db.Column(Integer, nullable=False)
    so_tien = db.Column(Integer, nullable=False)
    
class Login(Resource):
    def post(self):
        username = request.form['user']
        password = request.form['pass']
        
        check_admin = tai_khoan.query.filter_by(ten_dang_nhap=username, mat_khau=password, phan_quyen=1).first()
        check_user = tai_khoan.query.filter_by(ten_dang_nhap=username, mat_khau=password, phan_quyen=0, khoa=0).first()
        if check_admin:
            return {"login": "admin", "id": check_admin.id_tai_khoan}
        if check_user:
            return {"login": "user", "id": check_user.id_tai_khoan}
        
def encode_image(image_binary):
    return base64.b64encode(image_binary).decode('utf-8')
        
rf = {
    'id_san_pham': fields.Integer,
    'ten_san_pham': fields.String(50),
    'gia_tien': fields.Integer,
    'hinh_anh': fields.String(attribute=lambda x: encode_image(x.hinh_anh))
}
        
class Products(Resource):
    @marshal_with(rf)
    def get(self):
        products = san_pham.query.all()
        return products
    
    def post(self):
        product_name = request.form['name']
        product_price = request.form['price']
        product_image = request.files['image'].read()
        
        # Create a new product object
        new_product = san_pham(ten_san_pham=product_name, gia_tien=product_price, hinh_anh=product_image)
        
        # Add the new product to the database session
        db.session.add(new_product)
        
        # Commit the transaction to save the changes to the database
        db.session.commit()
        
        return ''
        #return {"message": "Product added"}, 201
    def delete(self):
        id_san_pham = request.form['id']
        rows_to_delete = san_pham.query.filter_by(id_san_pham=id_san_pham)

        # Delete the selected rows
        rows_to_delete.delete()
        
        # Commit the transaction to save the changes to the database
        db.session.commit()
        
        return ''

class Edit_Product(Resource):
    @marshal_with(rf)
    def get(self):
        id_san_pham = request.args.get('id')

        product = san_pham.query.filter_by(id_san_pham=id_san_pham).first()
        
        return product
    
    def put(self):
        id_san_pham = request.form['id']
        ten_san_pham = request.form['name']
        gia_tien = request.form['price']
        
        product = san_pham.query.filter_by(id_san_pham=id_san_pham).first()
        if product:
            product.ten_san_pham = ten_san_pham
            product.gia_tien = gia_tien
                     
            db.session.commit()
        return ''
        
    
        
api.add_resource(Login, "/login")
api.add_resource(Products, "/all_products")
api.add_resource(Edit_Product, "/edit_product")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
