from flask import Response, request
from flask_restful import Resource
from views import security 
import json
from models import db, Comment, Post

class CommentListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @security.post_id_is_valid
    @security.user_can_view_post
    def post(self):
        body = request.get_json()
        post_id = body.get('post_id')
        text = body.get('text')
        if not text:
            return Response(json.dumps({'message': '"text" parameter required in post body.'}), mimetype="application/json", status=400)

        comment = Comment(text, self.current_user.id, post_id)
        db.session.add(comment)
        db.session.commit()
        return Response(json.dumps(comment.to_dict()), mimetype="application/json", status=201)
        
class CommentDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
  
    @security.id_is_valid
    @security.user_can_edit_comment
    def delete(self, id):
        Comment.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message': 'Comment {0} successfully deleted.'.format(id)
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)


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
        '/api/comments/<id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
