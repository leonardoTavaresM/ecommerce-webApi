from flask import Flask, request
from flask import jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Inicializa a aplicação com configuracoes padrao
app = Flask(__name__)
CORS(app)

# inicializa a conexao com um banco de dados SQlite em memória
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Cria a entidade de produto
class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(255), unique=False, nullable=False)
  amount = db.Column(db.Numeric, unique=False, nullable=False)
  installments = db.Column(db.Integer, unique=False, nullable=False)
  installments_fee = db.Column(db.Boolean, unique=False, nullable=False)
  
  # facilitar para modelar as entidades
  def __repr__(self):
    return '<Product %r>' % self.title
  
  # retornando um json da tabela
  @property
  def serialized(self):
    return {
      'id': self.id,
      'title': self.title,
      'amount': round(self.amount, 2),
      'installments': {
        'number': self.installments,
        'total': round(self.amount / self.installments, 2)
      }
    }
    
# Configurações do banco de dados em memória
with app.app_context():
    db.create_all()
    
    # Cria dois produtos
    product1 = Product(title='Caneca Personalizada de Porcelana', amount=49.99,
                       installments=3, installments_fee=False)
    
    product2 = Product(title='Caneca de Tulipa', amount=34.99,
                       installments=3, installments_fee=False)
    
    # Insere os dois produtos no banco de dados em memória
    db.session.add(product1)
    db.session.add(product2)
    
    # Commit a transaction do banco de dados
    db.session.commit()

app.app_context().push()

# Insere os dois produtos no banco de dados em memória
db.session.add(product1)
db.session.add(product2)

# Commit a transaction do banco de dados
db.session.commit()

# Cria uma rota para consulta de produtos baseada no parâmetro query.
@app.route("/products", methods=['GET'])
def get_products():
  # admnistra tudo oque esta vindo no request da requisicao
  args = request.args.to_dict() # transformando os argumentos em dicionario
  query = args.get("query")
  
  if query is None:
    all_products = Product.query.all()
  else:
    all_products = Product.query.filter(
      Product.title.like(f'%{query}%')).all()
  
  return jsonify({
    'query': query,
    'size': len(all_products),
    'start': 'MA==',
    'results': [p.serialized for p in all_products]
  })


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)