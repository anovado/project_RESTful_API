# resources.py
# from flask_jwt_extended import 
from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from sqlalchemy import desc
from .model import Clients

import hashlib, uuid

from blueprints import db, app, internal_required

bp_client = Blueprint('client', __name__)
api = Api(bp_client)


class ClientList(Resource):
    def __init__(self):
        pass
    
    @internal_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument('id', type=int, location='args')
        parser.add_argument('status', location='args', choices=('true','false','True','False'))
        parser.add_argument('orderby', location='args', help='invalid orderby value', choices=('id','status'))
        parser.add_argument('sort', location='args', help='invalid sort value', choices=('desc','asc'))
        args = parser.parse_args()
        
        offset = (args['p'] * args['rp']) - args['rp']
        
        qry = Clients.query
        
        if args['id'] is not None:
            qry = qry.filter_by(id=args['id'])
        
        if args['status'] is not None:
            qry = qry.filter_by(status=True if args['status'].lower()  == 'true' else False) 
        
        if args['orderby'] is not None:
            if args['orderby'] == 'id':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Clients.id))
                else:
                    qry = qry.order_by(Clients.id)
            
            elif args['orderby'] == 'status':
                # if args['orderby'] == 'status':
                qry = qry.order_by(Clients.status)
        
        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Clients.response_field))
        
        return rows, 200
        
        
class ClientResource(Resource):
    def __init__(self):
        pass

    @internal_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('client_key', location='json', required=True)
        parser.add_argument('client_secret', location='json', required=True)
        parser.add_argument('status', location='json')
        data = parser.parse_args()

        salt = uuid.uuid4().hex
        encoded = ('%s%s' % (data['client_secret'], salt)).encode('utf-8')
        hash_pass = hashlib.sha512(encoded).hexdigest()
        
        client = Clients(data['client_key'], hash_pass, salt, data['status'])
        db.session.add(client)
        db.session.commit()
        
        app.logger.debug('DEBUG : %s', client)
        
        return marshal(client, Clients.response_field), 200, {'Content-Type': 'application/json'}

 
    @internal_required
    def get(self, id):
        qry = Clients.query.get(id)
        if qry is not None:
            return marshal(qry, Clients.response_field), 200
        return {'status':'NOT_FOUND'}, 404

    @internal_required
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('client_key', location='json', required=True)
        parser.add_argument('client_secret', location='json', required=True)
        parser.add_argument('status', location='json')
        data = parser.parse_args()

        qry = Clients.query.get(id)
        if qry is None:
            return {'status':'NOT_FOUND'}, 404

        qry.client_key = data['client_key']
        qry.client_secret = data['client_secret']
        qry.status = data['status']
        
        db.session.commit()

        return marshal(qry, Clients.response_field), 200
   
    @internal_required
    def delete(self, id):
        qry = Clients.query.get(id)
        if qry is None:
            return {'status':'NOT_FOUND'}, 404
        db.session.delete(qry)
        db.session.commit()
        return {'status':'DELETED'}, 200

    @internal_required
    def patch(self):
        return 'Not yet implemented', 501


    
api.add_resource(ClientList, '', '/')
api.add_resource(ClientResource, '', '/<id>')