from flask import Response, request
from flask_restful import Resource
from models import Bookmark, Post, db
import json
from . import can_view_post
from my_decorators import *

class BookmarksListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # Your code here
        bookmarks = Bookmark.query.filter_by(user_id=self.current_user.id).all()
        json_list = [bookmark.to_dict() for bookmark in bookmarks]
        return Response(json.dumps(json_list), mimetype="application/json", status=200)

    @check_missing_post_id
    @is_post_id_a_valid_int
    @is_post_in_database
    @secure_bookmark
    @handle_db_insert_error
    def post(self):
        # 1. Check if int
        # 2. Check if post exists
        # 3. Check that you have access to the post
        # 4. Do insert

        body = request.get_json()
        post_id = body.get('post_id')
        bookmark = Bookmark(self.current_user.id, post_id)
        db.session.add(bookmark)
        db.session.commit()
        return Response(json.dumps(bookmark.to_dict()), mimetype="application/json", status=201)     

class BookmarkDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @is_id_a_valid_int
    def delete(self, id):
        bookmark = Bookmark.query.get(id)
        if not bookmark:
            response_obj = {
                'message': 'Invalid bookmark_id={0}'.format(id)
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=404)
        
        # before I delete it, do I own it?
        if bookmark.user_id != self.current_user.id:
            response_obj = {
                'message': 'Unauthorized bookmark_id={0}'.format(id)
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=404)
        
        Bookmark.query.filter_by(id=id).delete()
        db.session.commit()
        return Response(json.dumps({}), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        BookmarksListEndpoint, 
        '/api/bookmarks', 
        '/api/bookmarks/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        BookmarkDetailEndpoint, 
        '/api/bookmarks/<id>', 
        '/api/bookmarks/<id>',
        resource_class_kwargs={'current_user': api.app.current_user}
    )


'''
from flask import Response, request
from flask_restful import Resource
from models import Bookmark, db
import json

from my_decorators import insert_or_404, is_post_id_a_valid_int, is_post_in_database, is_id_a_valid_int, secure_bookmark
from . import can_view_post


class BookmarksListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # Your code here
        bookmarks = Bookmark.query.filter_by(user_id = self.current_user.id).all()
        json_list = [bookmark.to_dict() for bookmark in bookmarks]
        return Response(json.dumps(json_list), mimetype="application/json", status=200)

    @is_post_id_a_valid_int
    @is_post_in_database
    @secure_bookmark
    @insert_or_404
    def post(self):
        # Your code here

        body = request.get_json()
        post_id = body.get('post_id')
        
        #security test
        if not can_view_post(post_id, self.current_user):
            response_obj = {
                'message': 'Post does not exist'
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=404)
        
        bookmark = Bookmark(self.current_user.id, post_id)
        db.session.add(bookmark)
        db.session.commit()
        return Response(json.dumps(bookmark.to_dict()), mimetype="application/json", status=201)

class BookmarkDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @is_id_a_valid_int
    def delete(self, id):
        # Your code here
        bookmark = Bookmark.query.get(id)
        if not bookmark:
            response_obj = {
                'message': 'Bookmark does not exist'
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=404)

        #security check
        if bookmark.user_id != self.current_user.id:
            response_obj = {
                'message': 'Bookmark unauthorised'
            }
            return Response(json.dumps(response_obj), mimetype="application/json", status=404)
        
        Bookmark.query.filter_by(id=id).delete()
        db.session.commit()
        return Response(json.dumps({}), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        BookmarksListEndpoint, 
        '/api/bookmarks', 
        '/api/bookmarks/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        BookmarkDetailEndpoint, 
        '/api/bookmarks/<id>', 
        '/api/bookmarks/<id>',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
'''