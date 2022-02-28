from flask import Response, request
from flask_restful import Resource
from . import can_view_post
import json
from models import db, Comment, Post

from my_decorators import *

class CommentListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @is_post_id_a_valid_int
    def post(self):
        # Your code here
        body = request.get_json()
        post_id = body.get('post_id')
        text = body.get('text')
        if not text:
            return Response(json.dumps({'message': 'enter valid text.'}), mimetype="application/json", status=400)
        
        if can_view_post(post_id, self.current_user):
            comment = Comment(text, self.current_user.id, post_id)
            db.session.add(comment)
            db.session.commit()
            return Response(json.dumps(comment.to_dict()), mimetype="application/json", status=201)
        else:
            response_obj = {
                'message': 'You do not have access to post_id = {0}'.format(post_id)
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=404)     


class CommentDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @is_id_a_valid_int
    @is_comment_in_database
    @check_ownership_of_comment
    def delete(self, id):
        # Your code here
        Comment.query.filter_by(id=id).delete()
        db.session.commit()
        ser_data = {
            'message': 'Comment {0} successfully deleted.'.format(id)
        }
        return Response(json.dumps(ser_data), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        CommentListEndpoint, 
        '/api/comments', 
        '/api/comments/',
        resource_class_kwargs={'current_user': api.app.current_user}

    )
    api.add_resource(
        CommentDetailEndpoint, 
        '/api/comments/<id>', 
        '/api/comments/<id>',
        resource_class_kwargs={'current_user': api.app.current_user}
    )