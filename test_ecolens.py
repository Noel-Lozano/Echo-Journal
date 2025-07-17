import unittest
from app import create_app, db
from app.api.openfood_api import fetch_product_by_barcode
from app.models.pantry import Pantry

class TestEcoLens(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def test_valid_barcode(self):
        barcode = "0096619313952"
        result = fetch_product_by_barcode(barcode)
        self.assertTrue(result['success'])
        self.assertIn("product", result)
        self.assertIn("product_name", result["product"])
        self.assertIn("Kirkland Chocolate Chip Soft", result["product"]["product_name"])

    def test_invalid_barcode(self):
        barcode = "invalid_barcode"
        result = fetch_product_by_barcode(barcode)
        self.assertFalse(result['success'])

    def test_add_to_pantry(self):
        with self.app.app_context():
            pantry_item1 = Pantry(
                user_id=1,
                product_name="Test Product",
                eco_score=5,
                score=4,
                pros="Good for the environment",
                cons="Expensive"
            )
            db.session.add(pantry_item1)
            db.session.commit()

            item = Pantry.query.filter_by(product_name="Test Product").first()
            self.assertIsNotNone(item)
            self.assertEqual(item.eco_score, '5')
            self.assertEqual(item.score, '4')

    def test_pantry_display(self):
        with self.app.app_context():
            pantry_item1 = Pantry(
                user_id=1,
                product_name="Test Product",
                eco_score=5,
                score=4,
                pros="Good for the environment",
                cons="Expensive"
            )
            db.session.add(pantry_item1)
            pantry_item2 = Pantry(
                user_id=1,
                product_name="Test Product 2",
                eco_score=7,
                score=3,
                pros="Good for the environment",
                cons="Expensive"
            )
            db.session.add(pantry_item2)
            db.session.commit()

            items = Pantry.query.filter_by(user_id=1).all()
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0].product_name, "Test Product")
            self.assertEqual(items[1].product_name, "Test Product 2")

            eco_sort = Pantry.query.filter_by(user_id=1).order_by(Pantry.eco_score.desc()).all()
            self.assertEqual(eco_sort[0].product_name, "Test Product 2")
            self.assertEqual(eco_sort[1].product_name, "Test Product")

    def test_signup_and_login(self):
        response = self.client.post("/signup", data={"username": "testuser", "password": "secret"}, follow_redirects=True)
        self.assertIn(b"dashboard", response.data)

        self.client.post("/logout")

        response = self.client.post("/login", data={"username": "testuser", "password": "secret"}, follow_redirects=True)
        self.assertIn(b"dashboard", response.data)

    def test_invalid_login(self):
        response = self.client.post("/login", data={"username": "wronguser", "password": "wrongpass"}, follow_redirects=True)
        self.assertIn(b"Invalid credentials!", response.data)
