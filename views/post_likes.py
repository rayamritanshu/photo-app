from flask import Response
from flask_restful import Resource
from models import LikePost, db
import json
from views import security
from my_decorators import *
import flask_jwt_extended

class PostLikesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    @security.post_id_is_valid
    @security.user_can_view_post
    def post(self, post_id):
        try:
            post_like = LikePost(self.current_user.id, post_id)
            db.session.add(post_like)
            db.session.commit()
        except Exception:
            import sys
            print(sys.exc_info()[1])
            return Response(
                json.dumps({
                    'message': 'DB insertion error. Post already liked by user.'}
                ), 
                mimetype="application/json", 
                status=400
            )

        return Response(json.dumps(post_like.to_dict()), mimetype="application/json", status=201)

class PostLikesDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    @security.id_is_valid
    def delete(self, post_id, id):
        print(post_id, id)
        post_like = LikePost.query.get(id)

        if not post_like or post_like.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Like does not exist'}), mimetype="application/json", status=404)
        
        LikePost.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message': 'Like deleted!'
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        PostLikesListEndpoint, 
        '/api/posts/<post_id>/likes', 
        '/api/posts/<post_id>/likes/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )

    api.add_resource(
        PostLikesDetailEndpoint, 
        '/api/posts/<post_id>/likes/<id>', 
        '/api/posts/<post_id>/likes/<id>/',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
