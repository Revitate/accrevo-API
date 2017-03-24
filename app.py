#!flask/Scripts/python
from flask import Flask, jsonify, abort, make_response, request
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

#Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/accdev'
db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)

class Companykey(db.Model):
    __table__ = db.Model.metadata.tables['companykey']

class Company(db.Model):
    __table__ = db.Model.metadata.tables['companys']

#auth config
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'admin':
        return 'admin'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)

def companyToJson(company):
    return jsonify({'company':
                    {
                        'name':company.name,
                        'address': company.address,
                        'id13': company.id13,
                        'taxbr': company.taxbr,
                        'type': company.type,
                        'comment': company.comment,
                        'contactperson': company.contactperson,
                        'contacttel': company.contacttel,
                        'year': company.year,
                        'owner': company.owner,
                        'partner': company.partner,
                        'code': company.code,
                        'created_at': company.created_at,
                        'updated_at': company.updated_at
                    }
                    })
def keyToJson(companykey):
    return jsonify({'companykey':
                    {
                        'company_id' : companykey.company_id,
                        'key' : companykey.key,
                        'partner_id' : companykey.partner_id
                    }
                    })

#route path
@app.route('/company', methods=['POST'])
@auth.login_required
def create_company():
    if not 'id13' in request.json:
        abort(400)
    company = Company(
        name = request.json.get('name', ""),
        address = request.json.get('address', ""),
        id13 = request.json['id13'],
        taxbr = request.json.get('taxbr', ""),
        type = request.json.get('type', 0),
        comment = request.json.get('comment', ""),
        contactperson = request.json.get('contactperson', ""),
        contacttel = request.json.get('contacttel', ""),
        year = request.json.get('year', 0),
        owner = request.json.get('owner', ""),
        partner = request.json.get('partner', ""),
        code = request.json.get('code', ""),
        created_at = request.json.get('created_at', None),
        updated_at = request.json.get('updated_at', None)
    )
    db.session.add(company)
    db.session.commit()
    return companyToJson(company)

@app.route('/company/<companyname>', methods=['GET'])
def get_company(companyname):
    company = Company.query.filter_by(name = companyname).first_or_404()
    return companyToJson(company)

@app.route('/company/getnewAPIKey', methods=['GET'])
def get_new_companykey():
    company = Company.query.filter_by(name = request.args['company_name']).first_or_404()
    companykey = Companykey.query.filter_by(company_id = company.id).first()
    newKey = str(random.randint(1,10000000))
    if(companykey is None):
        companykey = Companykey(
            company_id = company.id,
            key = newKey,
            partner_id = 0
        )
        db.session.add(companykey)
        db.session.commit()
    else:
        companykey.key = newKey
        db.session.commit()
    return newKey

if __name__ == '__main__':
    app.run(debug=True)
