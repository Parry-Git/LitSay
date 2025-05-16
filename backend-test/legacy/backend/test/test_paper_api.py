import unittest
import requests

BASE_URL = 'http://localhost:5000/api/papers'

class TestPaperAPI(unittest.TestCase):
    def test_get_all_papers(self):
        response = requests.get(BASE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
    
    def test_search_papers(self):
        response = requests.get(f"{BASE_URL}/search?q=数据库")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
    
    def test_get_single_paper(self):
        # 假设存在ID为1的文献
        response = requests.get(f"{BASE_URL}/1")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

if __name__ == '__main__':
    unittest.main()