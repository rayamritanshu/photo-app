from flask import Response, request
from flask_restful import Resource
from models import LikePost, db
import json

from my_decorators import is_id_a_valid_int, is_post_id_a_valid_int, is_valid_int
from . import can_view_post

class PostLikesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def post(self, post_id):
        # Your code here

        try:
            post_id = int(post_id)
        except:
            response_obj = {
                'message': 'Invalid post_id={0}'.format(post_id)
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=400)
        
        if can_view_post(post_id, self.current_user):
            try:
                post_like = LikePost(self.current_user.id, post_id)
                db.session.add(post_like)
                db.session.commit()
            except Exception:
                return Response(
                    json.dumps({'message': 'Database Insert error. Post={0} already liked by user={1}.'.format(post_id, self.current_user.id)}), 
                    mimetype="application/json", 
                    status=400
                )
            return Response(json.dumps(post_like.to_dict()), mimetype="application/json", status=201)
        else:
            response_obj = {
                'message': 'You don\'t have access to post_id={0}'.format(post_id)
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=404)

class PostLikesDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    

    def delete(self, post_id, id):
        # Your code here

        try:
            id = int(id)
        except:
            response_obj = {
                'message': 'Invalid id={0}'.format(id)
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=400)

        post_like = LikePost.query.get(id)

        if not post_like or post_like.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Post_id = {} not liked by user={}'.format(post_id, self.current_user.id)}), mimetype="application/json", status=404)
        
        LikePost.query.filter_by(id=id).delete()
        db.session.commit()
        ser_data = {
            'message': 'Unliked, id={0}.'.format(id)
        }
        return Response(json.dumps(ser_data), mimetype="application/json", status=200)





def initialize_routes(api):
    api.add_resource(
        PostLikesListEndpoint, 
        '/api/posts/<post_id>/likes', 
        '/api/posts/<post_id>/likes/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        PostLikesDetailEndpoint, 
        '/api/posts/<post_id>/likes/<id>', 
        '/api/posts/<post_id>/likes/<id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
