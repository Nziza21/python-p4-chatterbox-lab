from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.all()
    messages_list = [{'id': message.id, 'body': message.body, 'username': message.username, 'created_at': message.created_at} for message in messages]
    return jsonify(messages_list)

@app.route('/messages/<int:id>', methods=['GET'])
def get_message_by_id(id):
    message = Message.query.get(id)
    if message:
        return jsonify({'id': message.id, 'body': message.body, 'username': message.username, 'created_at': message.created_at})
    else:
        return jsonify({'error': 'Message not found'}), 404

if __name__ == '__main__':
    app.run(port=5555)
