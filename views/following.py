from flask import Response, request
from flask_restful import Resource
from models import Following, User, db
from views import security
import json

def get_path():
    return request.host_url + 'api/posts/'

class FollowingListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        following = Following.query.filter_by(user_id=self.current_user.id)
        return Response(json.dumps([model.to_dict_following() for model in following]), mimetype="application/json", status=200)

    @security.user_id_is_valid
    def post(self):
        body = request.get_json()
        user_id = body.get('user_id') 
        user = User.query.get(user_id)
        if not user:
            return Response(
                json.dumps({
                    'message': 'User id={0} does not exist'.format(user_id)
                }), mimetype="application/json", status=404)
        try:
            following = Following(self.current_user.id, user_id)
            db.session.add(following)
            db.session.commit() 
        except Exception:
            import sys
            print(sys.exc_info()[1])
            return Response(
                json.dumps({
                    'message': 'Database Insert error. Are you already following user={0}? Please see the log files.'.format(user_id)}
                ), 
                mimetype="application/json", 
                status=400
            ) 
        return Response(json.dumps(following.to_dict_following()), mimetype="application/json", status=201)

class FollowingDetailEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    @security.id_is_valid
    def delete(self, id):
        following = Following.query.get(id)

        if not following or following.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Following record does not exist'}), mimetype="application/json", status=404)
        
        username = following.following.username
        Following.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message': 'You have successfully unfollowed {0} (user={1})'.format(username, id)
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)




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
