import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from collections import deque
import heapq

# Define a simple class hierarchy
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"
    
# Extend the Animal class hierarchy
class Bird(Animal):
    def speak(self):
        return f"{self.name} says Chirp!"
    
# Add functionality for retrieving all animals
def get_all_animals_handler():
    animals = db.get_all_animals()
    return json.dumps({'animals': animals})

# Define a simple database-like functionality using SQLite
class AnimalDatabase:
    def __init__(self, db_file="animals.db"):
        self.db_file = db_file
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS animals (
                id INTEGER PRIMARY KEY,
                name TEXT,
                type TEXT
            )
        ''')
        self.connection.commit()

    def add_animal(self, name, animal_type):
        self.cursor.execute('INSERT INTO animals (name, type) VALUES (?, ?)', (name, animal_type))
        self.connection.commit()

    def get_animal_by_type(self, animal_type):
        self.cursor.execute('SELECT name FROM animals WHERE type = ?', (animal_type,))
        result = self.cursor.fetchall()
        return [row[0] for row in result]

    def get_all_animals(self):
        self.cursor.execute('SELECT name, type FROM animals')
        result = self.cursor.fetchall()
        return [{'name': row[0], 'type': row[1]} for row in result]

# Data structure: Queue (using deque from collections)
class AnimalQueue:
    def __init__(self):
        self.queue = deque()

    def enqueue(self, animal):
        self.queue.append(animal)

    def dequeue(self):
        if self.queue:
            return self.queue.popleft()
        else:
            return None

# Sorting algorithm: Heap Sort
def heap_sort(data):
    heapq.heapify(data)
    sorted_data = []
    while data:
        sorted_data.append(heapq.heappop(data))
    return sorted_data

# Add functionality for queue operations
def queue_operations_handler():
    animal_queue = AnimalQueue()
    animal_queue.enqueue(Dog("Buddy"))
    animal_queue.enqueue(Cat("Whiskers"))
    dequeued_animal = animal_queue.dequeue()

    return f"Dequeued animal: {dequeued_animal.speak() if dequeued_animal else 'None'}"

class MyHandler(BaseHTTPRequestHandler):
    def _send_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'message': message}).encode('utf-8'))

    def do_GET(self):
        print(f"Requested path: {self.path}")  # Add this line for debugging

        if self.path == '/dog':
            animal = Dog("Buddy")
            self._send_response(animal.speak())
        elif self.path == '/cat':
            animal = Cat("Whiskers")
            self._send_response(animal.speak())
        elif self.path == '/bird':
            animal = Bird("Tweetie")
            self._send_response(animal.speak())
        elif self.path == '/add_dog':
            db.add_animal("Max", "dog")
            self._send_response("Dog added to the database.")
        elif self.path == '/get_dogs':
            dogs = db.get_animal_by_type("dog")
            self._send_response(f"Dogs in the database: {', '.join(dogs)}")
        elif self.path == '/get_all_animals':
            response = get_all_animals_handler()
            self._send_response(response)
        elif self.path == '/queue_operations':
            response = queue_operations_handler()
            self._send_response(response)
        elif self.path == '/heap_sort':
            data = [5, 2, 9, 1, 5, 6]
            sorted_data = heap_sort(data.copy())
            self._send_response(f"Original data: {data}, Sorted data: {sorted_data}")
        else:
            self._send_response("Invalid path")

# Initialize the AnimalDatabase outside the __main__ block
db = AnimalDatabase()

# Run the HTTP server
def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, MyHandler)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
