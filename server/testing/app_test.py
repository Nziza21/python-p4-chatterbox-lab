
import unittest
from datetime import datetime
from flask import Flask
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

class TestApp(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    with app.app_context():
        db.create_all()

        messages_to_delete = Message.query.filter(
            Message.body == "Hello 👋",
            Message.username == "Liza"
        ).all()

        for message in messages_to_delete:
            db.session.delete(message)

        db.session.commit()


    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        db.session.rollback()

    def test_has_correct_columns(self):
        with app.app_context():
            hello_from_liza = Message(
                body="Hello 👋",
                username="Liza"
            )

            db.session.add(hello_from_liza)
            db.session.commit()

            self.assertEqual(hello_from_liza.body, "Hello 👋")
            self.assertEqual(hello_from_liza.username, "Liza")
            self.assertIsInstance(hello_from_liza.created_at, datetime)

    def test_returns_list_of_json_objects_for_all_messages_in_database(self):
        with app.app_context():
            response = self.app.get('/messages')
            records = Message.query.all()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/json')

            for message in response.json:
                self.assertIn(message['id'], [record.id for record in records])
                self.assertIn(message['body'], [record.body for record in records])

    def test_creates_new_message_in_the_database(self):
        with app.app_context():
            response = self.app.post(
                '/messages',
                json={
                    "body": "Hello 👋",
                    "username": "Liza",
                },
                headers={'Content-Type': 'application/json'}
            )

            self.assertEqual(response.status_code, 200)

            h = Message.query.filter_by(body="Hello 👋").first()
            self.assertIsNotNone(h)

            db.session.delete(h)
            db.session.commit()

    def test_returns_data_for_newly_created_message_as_json(self):
        with app.app_context():
            response = self.app.post(
                '/messages',
                json={
                    "body": "Hello 👋",
                    "username": "Liza",
                },
                headers={'Content-Type': 'application/json'}
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json["body"], "Hello 👋")
            self.assertEqual(response.json["username"], "Liza")

            h = Message.query.filter_by(body="Hello 👋").first()
            self.assertIsNotNone(h)

            db.session.delete(h)
            db.session.commit()

    def test_updates_body_of_message_in_database(self):
        '''updates the body of a message in the database.'''
        with app.app_context():

            m = Message.query.first()
            id = m.id
            body = m.body

            app.test_client().patch(
                f'/messages/{id}',
                json={
                    "body":"Goodbye 👋",
                }
            )

            g = Message.query.filter_by(body="Goodbye 👋").first()
            assert(g)

            g.body = body
            db.session.add(g)
            db.session.commit()

    def test_returns_data_for_updated_message_as_json(self):
        '''returns data for the updated message as JSON.'''
        with app.app_context():

            m = Message.query.first()
            id = m.id
            body = m.body

            response = app.test_client().patch(
                f'/messages/{id}',
                json={
                    "body":"Goodbye 👋",
                }
            )

            assert(response.content_type == 'application/json')
            assert(response.json["body"] == "Goodbye 👋")

            g = Message.query.filter_by(body="Goodbye 👋").first()
            g.body = body
            db.session.add(g)
            db.session.commit()

    def test_deletes_message_from_database(self):
        '''deletes the message from the database.'''
        with app.app_context():

            hello_from_liza = Message(
                body="Hello 👋",
                username="Liza")
            
            db.session.add(hello_from_liza)
            db.session.commit()

            app.test_client().delete(
                f'/messages/{hello_from_liza.id}'
            )

            h = Message.query.filter_by(body="Hello 👋").first()
            assert(not h)

if __name__ == '__main__':
    unittest.main()
