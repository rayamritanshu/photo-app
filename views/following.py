from flask import Response, request
from flask_restful import Resource
from models import Following, User, db
import json

from my_decorators import handle_db_insert_error, is_id_a_valid_int, is_user_id_valid_int, is_valid_int

def get_path():
    return request.host_url + 'api/posts/'

class FollowingListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # Your code here
        following = Following.query.filter_by(user_id=self.current_user.id)
        sol = [model.to_dict_following() for model in following]
        return Response(json.dumps(sol), mimetype="application/json", status=200)

    @is_user_id_valid_int
    @handle_db_insert_error
    def post(self):
        # Your code here
        body = request.get_json()
        user_id = body.get('user_id') 
        user = User.query.get(user_id)
        if not user:
            return Response(
                json.dumps({'message': 'Invalid user id={0}'.format(user_id)}), mimetype="application/json", status=404)

        following = Following(self.current_user.id, user_id)
        db.session.add(following)
        db.session.commit() 
        return Response(json.dumps(following.to_dict_following()), mimetype="application/json", status=201)


class FollowingDetailEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    @is_id_a_valid_int
    def delete(self, id):
        # Your code here
        following = Following.query.get(id)

        if not following or following.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Record not found'}), mimetype="application/json", status=404)
        
        username = following.following.username
        Following.query.filter_by(id=id).delete()
        db.session.commit()
        ser_data = {
            'message': 'Unfollowed {0})'.format(username)
        }
        return Response(json.dumps(ser_data), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        FollowingListEndpoint, 
        '/api/following', 
        '/api/following/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
    api.add_resource(
        FollowingDetailEndpoint, 
        '/api/following/<id>', 
        '/api/following/<id>/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
