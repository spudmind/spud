from flask import Flask, url_for, render_template, abort
from flask.ext.restful import Api, Resource, reqparse
from web.controllers import mps
from web.api import get_mps_function
from web.api import get_mp_function
import os

template_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'web/templates'
)
static_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'web/static'
)
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config.from_object(__name__)
api = Api(app)


@app.route('/mps')
def show_mps():
    return render_template('show_mps.html', entity=None)


class GetMps(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('party', type=str)
        self.reqparse.add_argument('interests_gt', type=int)
        self.reqparse.add_argument('interests_lt', type=int)
        self.reqparse.add_argument('donations_gt', type=int)
        self.reqparse.add_argument('donations_lt', type=int)
        super(GetMps, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return get_mps_function.MpsApi().request(args)


class GetMp(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str)
        super(GetMp, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        return get_mp_function.MpApi().request(args)


api.add_resource(GetMps, '/api/v0.1/getMps', endpoint='getMps')
api.add_resource(GetMp, '/api/v0.1/getMp', endpoint='getMp')

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1')
    app.run()
