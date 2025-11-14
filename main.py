from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)


CATEGORIES = {
    'supercars': {'name': 'Суперкары', 'icon': '🏎️'},
    'sportscars': {'name': 'Спорт-кары', 'icon': '🚗'},
    'motorcycles': {'name': 'Топ-мотоциклы', 'icon': '🏍️'}
}


def load_products_from_files():
    products = []

    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(base_dir, 'data')
    
    for product_file in os.listdir(base_path):
        if product_file.endswith('.txt'):
            with open(os.path.join(base_path, product_file), 'r', encoding='utf-8') as f:
                product_data = {}
                # простой парсер, мини аналог json в txt; функция извлекает все продукты
                for line in f:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'images':
                            product_data[key] = [img.strip() for img in value.split(',')]
                        elif key == 'specs':
                            specs = {}
                            for spec in value.split('|'):
                                if ':' in spec:
                                    spec_key, spec_value = spec.split(':', 1)
                                    specs[spec_key.strip()] = spec_value.strip()
                            product_data[key] = specs
                        elif key in ['price', 'stock', 'bestseller']:
                            try:
                                product_data[key] = int(value)
                            except:
                                product_data[key] = 0
                        else:
                            product_data[key] = value
                
                products.append(product_data)

    return products


def get_products_by_category(category):
    # продукты какой-то категории
    all_products = load_products_from_files()
    ans = [p for p in all_products if p['category'] == category]
    ans.sort(key=lambda x: x['bestseller'], reverse=True)
    return ans


def create_product_page(product_id, *args, **kwargs):
    products = load_products_from_files()
    product = None
    
    for p in products:
        if p['id'] == product_id:
            product = p
            break
    
    if not product:
        return "Товар не найден", 404
    
    template_data = {
        'product': product,
        'category_name': get_category_name(product['category']),
        'category_url': product['category']
    }
    template_data.update(kwargs)

    return render_template('product.html', **template_data)


def get_category_name(category):
    category_names = {
        'supercars': 'Суперкары',
        'sportscars': 'Спорт-кары', 
        'motorcycles': 'Топ-мотоциклы'
    }
    return category_names.get(category, 'Категория')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/category/<category>')
def create_category_page(category):
    products = get_products_by_category(category)
    
    # Применяем фильтры если они есть
    filtered_products = []
    
    for product in products:
        include_product = True
        
        # Фильтр по цене
        min_price = request.args.get('min_price')
        if min_price:
            try:
                if product['price'] < int(min_price):
                    include_product = False
            except:
                pass
        
        max_price = request.args.get('max_price')
        if max_price:
            try:
                if product['price'] > int(max_price):
                    include_product = False
            except:
                pass
        
        # Фильтр по брендам
        brands = request.args.getlist('brand')
        if brands and product.get('brand') not in brands:
            include_product = False
        
        if include_product:
            filtered_products.append(product)
    
    return render_template('category.html', 
                         products=filtered_products,
                         category_id=category,
                         category_name=CATEGORIES[category]['name'],
                         category_icon=CATEGORIES[category]['icon'])


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/compare/<category>')
def compare_category(category):
    products = get_products_by_category(category)
    all_specs = set()
    
    for product in products:
        if 'specs' in product:
            # какие-либо не основные данные о продуках, за правдивость их не ручаюсь
            all_specs.update(product['specs'].keys())
    
    return render_template('compare_category.html', 
                         category=category, 
                         products=products, 
                         all_specs=sorted(all_specs),
                         category_name=get_category_name(category))


@app.route('/product/<product_id>')
def product_detail(product_id):
    return create_product_page(product_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    elif request.method == 'POST':
        data = request.form
        for key in data:
            print(key, "->", data[key])
        return render_template("success_la.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        data = request.form
        for key in data:
            print(key, "->", data[key])
        return redirect(url_for('profile'))
    

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'GET':
        return render_template("add_product.html")
    elif request.method == 'POST':
        data = request.form
        for key in data:
            print(key, "->", data[key])
        
        product_data = f"""id: {data['id']}
        name: {data['name']}
        category: {data['category']}
        price: {data['price']}
        stock: {data['stock']}
        images: default.jpg
        description: {data['description']}
        specs: Мощность: {data.get('power', 'N/A')}|Разгон 0-100: {data.get('acceleration', 'N/A')}|Тип: {data.get('type', 'N/A')}
        bestseller: 0
        brand: {data['brand']}"""
        
        category = data['category']
        filename = f"{data['id']}.txt"
        os.makedirs(f'data/', exist_ok=True)
        
        with open(f'data/{filename}', 'w', encoding='utf-8') as f:
            f.write(product_data)
        
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)