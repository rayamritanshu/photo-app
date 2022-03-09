from flask import Response, request
from flask_restful import Resource
from models import Bookmark, db
import json
from views import security
from my_decorators import *
import flask_jwt_extended

class BookmarksListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def get(self):
        bookmarks = Bookmark.query.filter_by(user_id=self.current_user.id)
        return Response(json.dumps([bookmark.to_dict() for bookmark in bookmarks]), mimetype="application/json", status=200)

    @flask_jwt_extended.jwt_required()
    @security.post_id_is_valid
    @security.user_can_view_post
    def post(self):
        body = request.get_json()
        post_id = body.get('post_id')

        try:
            bookmark = Bookmark(self.current_user.id, post_id)
            db.session.add(bookmark)
            db.session.commit()
        except Exception:
            import sys
            print(sys.exc_info()[1])
            return Response(
                json.dumps({
                    'message': 'DB insertion error. Post already bookmarked'}
                ), 
                mimetype="application/json", 
                status=400
            )

        return Response(json.dumps(bookmark.to_dict()), mimetype="application/json", status=201)

class BookmarkDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    @security.id_is_valid
    def delete(self, id):
        bookmark = Bookmark.query.get(id)

        if not bookmark or bookmark.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Bookmark does not exist'}), mimetype="application/json", status=404)
        
        Bookmark.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message': 'Bookmark {0} successfully deleted.'.format(id)
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        BookmarksListEndpoint, 
        '/api/bookmarks', 
        '/api/bookmarks/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )

    api.add_resource(
        BookmarkDetailEndpoint, 
        '/api/bookmarks/<id>', 
        '/api/bookmarks/<id>',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
