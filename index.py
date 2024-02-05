# This Python file uses the following encoding: utf-8
import os
# import sys
# sys.path.append('/home/c/cx77384/myenv/lib/python3.6/site-packages/')

from flask import Flask, render_template, redirect, request, session, url_for
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_sqlalchemy import SQLAlchemy
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


# App
app = Flask(__name__)
application = app

# DataBase
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///avionika.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)


# Uploads
app.config['UPLOAD_FOLDER'] = 'static/img'



# # User`s URL
# Home
@app.route('/')
def home():
    #news = News.query.order_by(-News.id).all()
    news=0
    return render_template('user/home.html', news=news)


# About
@app.route('/about')
def about():
    return render_template('user/about.html')


# Shop
@app.route('/shop', methods=['POST', 'GET'])
def shop():
    products = Shop.query.order_by(-Shop.id).all()

    categories = []

    for i in products:
        if (i.category not in categories) and (i.quantity > 0):
            categories.append(i.category)
    categories.sort()

    return render_template('user/shop.html', product=products, categories=categories)


@app.route('/shop/<category>')
def shop_category(category):
    products = Shop.query.filter(Shop.category == category).all()

    return render_template('user/shop_order.html', product=products)


@app.route('/shop/product<int:id>')
def product(id):
    product = Shop.query.get(id)
    return render_template('user/product.html', product=product)


@app.route('/shop/buy/product<int:id>', methods=['POST', 'GET'])
def buy_product(id):
    product = Shop.query.get(id)

    if request.method == 'POST':
        products = id
        surname = request.form['surname']
        name = request.form['name']
        middle_name = request.form['middle_name']
        e_mail = request.form['e_mail']
        phone = request.form['phone']
        type_of_delivery = request.form['type_of_delivery']
        address = request.form['address']
        quantity = request.form['quantity']
        data = datetime.date.today()
        price = int(product.price) * int(quantity)

        order = Orders(price=price, data=data, products=products, surname=surname, name=name, middle_name=middle_name,
                       e_mail=e_mail, phone=phone, type_of_delivery=type_of_delivery,
                       quantity=quantity, address=address)
        product.quantity = product.quantity - int(quantity)

        try:
            buyer(e_mail)
            seller()
        except:
            pass

        try:
            db.session.add(order)
            db.session.commit()
            return redirect(url_for('shop'))
        except:
            return 'Ошибка, попробуйте позже.'

    return render_template('user/order_product.html', product=product)


# Calls
@app.route('/call', methods=['POST', 'GET'])
def call():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        device = request.form['device']
        problem = request.form['problem']

        try:
            seller()
        except:
            pass

        calls = Calls(name=name, phone=phone, address=address, device=device, problem=problem)

        try:
            db.session.add(calls)
            db.session.commit()
            return redirect(url_for('home'))
        except:
            return 'Ошибка, попробуйте позже.'

    return render_template('user/call.html')


@app.errorhandler(404)
def not_found(error):
    return render_template('user/error.html')


# Admin`s URL
@app.route('/admin', methods=['POST', 'GET'])
def admin_log():

    if 'userLogged' in session:
        return redirect(url_for('admin_main'))

    elif 'userLogged' not in session and request.method == 'POST':
        if request.form['FirstField'] == 'avionika' and check_password_hash(admin_password, request.form['Pass']):
            session['userLogged'] = 'avionika'
        return redirect(request.referrer)

    else:
        return render_template('admin/login.html')


# Admin - Main
@app.route('/admin/main', methods=['POST', 'GET'])
def admin_main():

    #news = News.query.order_by(-News.id).all()
    border = {'main': 'border: 2px solid black;', 'shop': '', 'orders': '', 'calls': ''}

    if 'userLogged' in session:

        if request.method == 'POST' and request.form['AdminLogOut'] == 'LogOut':
            session.pop('userLogged', None)
            return redirect(request.referrer)

        if request.method == 'POST':
            if request.form['act'] == 'Сохранить':
                if request.files['poster']:
                    file = request.files['poster']
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                    poster = News(image=filename)
                    try:
                        db.session.add(poster)
                        db.session.commit()
                        return redirect(url_for('admin_main'))
                    except:
                        return 'Ошибка, попробуйте позже.'

            elif request.form['act'] != 'Сохранить':
                article = News.query.get(int(request.form['act']))
                if os.path.isfile('static/img/' + article.image):
                    os.remove('static/img/' + article.image)
                try:
                    db.session.delete(article)
                    db.session.commit()
                    return redirect(url_for('admin_main'))
                except:
                    return 'Ошибка, повторите позже.'

        return render_template('admin/main/admin_main.html', news=news, border=border)

    else:
        return redirect(url_for('admin_log'))


# Admin - Shop
@app.route('/admin/shop', methods=['POST', 'GET'])
def admin_shop():

    border = {'main': '', 'shop': 'border: 2px solid black;', 'orders': '', 'calls': ''}
    items = Shop.query.all()

    if 'userLogged' in session:
        if request.method == 'POST' and request.form['AdminLogOut'] == 'LogOut':
            session.pop('userLogged', None)
            return redirect(request.referrer)

        return render_template('admin/shop/admin_shop.html', items=items, border=border)

    else:
        return redirect(url_for('admin_log'))


@app.route('/admin/shop/add', methods=['POST', 'GET'])
def admin_shop_add():
    if 'userLogged' in session:
        if request.method == 'POST':
            title = request.form['title']
            article_number = request.form['article_number']
            category = request.form['category']
            description = request.form['description']
            specifications = request.form['specifications']
            price = request.form['price']
            quantity = request.form['quantity']
            keywords = request.form['keywords']

            file = request.files['image']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            item = Shop(image=filename, title=title, keywords=keywords, article_number=article_number, category=category, description=description, specifications=specifications, price=price, quantity=quantity)

            try:
                db.session.add(item)
                db.session.commit()
                return redirect(url_for('admin_shop'))
            except:
                return 'Ошибка, попробуйте позже.'

        return render_template('admin/shop/admin_shop_add.html')
    else:
        return redirect(url_for('admin_log'))


@app.route('/admin/shop/<int:id>', methods=['POST', 'GET'])
def admin_certain_product(id):
    if 'userLogged' in session:
        product = Shop.query.get(id)
        if request.method == 'POST':
            if request.form['act'] == 'Удалить':
                if os.path.isfile('static/img/' + product.image):
                    os.remove('static/img/' + product.image)
                try:
                    db.session.delete(product)
                    db.session.commit()
                    return redirect(url_for('admin_shop'))
                except:
                    return 'Ошибка, повторите позже.'

            elif request.form['act'] == 'Сохранить':
                product.title = request.form['title']
                product.article_number = request.form['article_number']
                product.category = request.form['category']
                product.description = request.form['description']
                product.specifications = request.form['specifications']
                product.price = request.form['price']
                product.quantity = request.form['quantity']
                product.keywords = request.form['keywords']

                if request.files['image']:
                    if os.path.isfile('static/img/'+ product.image):
                        os.remove('static/img/'+ product.image)

                    file = request.files['image']
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                    product.image = filename

                try:
                    db.session.commit()
                    return redirect(request.referrer)
                except:
                    return 'Ошибка, попробуйте позже.'
        return render_template('admin/shop/admin_shop_product.html', product=product)
    else:
        return redirect(url_for('admin_log'))


# Admin - Orders
@app.route('/admin/order', methods=['POST', 'GET'])
def admin_order():
    border = {'main': '', 'shop': '', 'orders': 'border: 2px solid black;', 'calls': ''}
    orders = Orders.query.order_by(-Orders.id).all()

    counter = {}

    counter['new'] = Orders.query.filter(Orders.status == 'Не рассмотрен').count()
    counter['process'] = Orders.query.filter(Orders.status == 'В обработке').count()
    counter['complete'] = Orders.query.filter(Orders.status == 'Завершен').count()
    counter['cancel'] = Orders.query.filter(Orders.status == 'Отменен').count()

    if 'userLogged' in session:
        if request.method == 'POST' and request.form['AdminLogOut'] == 'LogOut':
            session.pop('userLogged', None)
            return redirect(request.referrer)
        return render_template('admin/order/admin_order.html', orders=orders, border=border, counter=counter)

    else:
        return redirect(url_for('admin_log'))


@app.route('/admin/order/<int:id>', methods=['POST', 'GET'])
def admin_certain_order(id):

    order = Orders.query.get(id)
    product = Shop.query.get(order.products)
    count = int(product.quantity) + int(order.quantity)

    if 'userLogged' in session:
        if request.method == 'POST':
            if request.form['act'] == 'Сохранить':
                product.quantity = int(product.quantity) + int(order.quantity)
                order.quantity = request.form['quantity']
                product.quantity = int(product.quantity) - int(request.form['quantity'])

                order.address = request.form['address']
                order.price = int(product.price) * int(request.form['quantity'])
                order.comment = request.form['comment']
                order.status = request.form['status']

                try:
                    db.session.commit()
                    return redirect(request.referrer)
                except:
                    return 'Ошибка. Повторите позже.'

            elif request.form['act'] == 'Удалить':
                try:
                    db.session.delete(order)
                    db.session.commit()
                    return redirect(url_for('admin_order'))
                except:
                    return 'Ошибка. Повторите позже.'
        return render_template('admin/order/admin_certain_order.html', order=order, product=product, count=count)
    else:
        return redirect(url_for('admin_log'))


# Admin - Calls
@app.route('/admin/call', methods=['POST', 'GET'])
def admin_call():

    border = {'main': '', 'shop': '', 'orders': '', 'calls': 'border: 2px solid black;'}
    calls = Calls.query.order_by(-Calls.id).all()

    # Counter
    counter = {}

    counter['new'] = Orders.query.filter(Orders.status == 'Не рассмотрен').count()
    counter['process'] = Orders.query.filter(Orders.status == 'В обработке').count()
    counter['complete'] = Orders.query.filter(Orders.status == 'Завершен').count()
    counter['cancel'] = Orders.query.filter(Orders.status == 'Отменен').count()


    if 'userLogged' in session:
        if request.method == 'POST' and request.form['AdminLogOut'] == 'LogOut':
            session.pop('userLogged', None)
            return redirect(request.referrer)

        return render_template('admin/call/admin_call.html', calls=calls, counter=counter, border=border)
    else:
        return redirect(url_for('admin_log'))


@app.route('/admin/call/<int:id>', methods=['POST', 'GET'])
def admin_certain_call(id):

    call = Calls.query.get(id)

    if 'userLogged' in session:
        if request.method == 'POST':
            if request.form['act'] == 'Удалить':
                try:
                    db.session.delete(call)
                    db.session.commit()
                    return redirect(url_for('admin_call'))
                except:
                    return 'Ошибка, попробуйте позже.'

            elif request.form['act'] == 'Подтвердить':
                call.status = request.form['status']
                call.comment = request.form['comment']
                try:
                    db.session.commit()
                    return redirect(request.referrer)
                except:
                    return 'Ошибка, попробуйте позже.'
        return render_template('admin/call/admin_certain_call.html', call=call)
    else:
        return redirect(url_for('admin_log'))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
