import tkinter as tk
from tkinter import messagebox
import pandas as pd
import sqlite3
from sklearn.neighbors import NearestNeighbors
import re
import textwrap

class BookRecommenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Recommendation System")

        # Set window size and center the window
        window_width = 600
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f'{window_width}x{window_height}+{position_x}+{position_y}')

        self.setup_ui()  # Set up the user interface

        self.init_db()  # Initialize the database
        self.populate_db()  # Populate the database with book data
        self.model, self.isbn_list = self.train_model()  # Train the recommendation model

    def setup_ui(self):
        # Create and arrange the UI components
        self.label = tk.Label(self.root, text="Enter a Book Title:")
        self.label.pack(pady=10)

        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack(pady=10)

        self.button = tk.Button(self.root, text="Get Recommendations", command=self.get_recommendations)
        self.button.pack(pady=10)

        self.result_label = tk.Label(self.root, text="Recommendations:", anchor="w")
        self.result_label.pack(pady=10)

        self.result_text = tk.Text(self.root, height=10, width=72)  # Set width to 72 characters
        self.result_text.pack(pady=10)

    def init_db(self):
        # Create the books table in the SQLite database
        conn = sqlite3.connect('books.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS books (
                ISBN TEXT PRIMARY KEY,
                Book_Title TEXT,
                Book_Author TEXT,
                Year_Of_Publication INTEGER,
                Publisher TEXT,
                Avg_Rating REAL,
                Num_Ratings INTEGER,
                Std_Rating REAL,
                Cleaned_Book_Title TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def clean_title(self, title):
        # Clean the book title for case-insensitivity and punctuation
        title = title.lower()
        title = re.sub(r'[.,:;()\'"]&#?!-', '', title)
        title = title.strip()
        return title

    def aggregate_ratings(self):
        # Aggregate ratings from the Ratings.csv file
        ratings_df = pd.read_csv('../data/Ratings.csv')
        aggregated_ratings = ratings_df.groupby('ISBN').agg({
            'Book_Rating': ['mean', 'count', 'std']
        }).reset_index()
        aggregated_ratings.columns = ['ISBN', 'Avg_Rating', 'Num_Ratings', 'Std_Rating']
        aggregated_ratings['Std_Rating'].fillna(0, inplace=True)  # Fill NaN std ratings with 0
        return aggregated_ratings

    def populate_db(self):
        # Read book and user data from CSV files
        books_df = pd.read_csv('../data/Books.csv', low_memory=False)
        ratings_df = pd.read_csv('../data/Ratings.csv')
        users_df = pd.read_csv('../data/Users.csv')

        # Aggregate ratings and merge with books data
        aggregated_ratings = self.aggregate_ratings()
        books_df = pd.merge(books_df, aggregated_ratings, on='ISBN')

        # Clean the data
        books_df['Year_Of_Publication'] = pd.to_numeric(books_df['Year_Of_Publication'], errors='coerce')
        books_df['Year_Of_Publication'].fillna(books_df['Year_Of_Publication'].median(), inplace=True)
        books_df['Year_Of_Publication'] = books_df['Year_Of_Publication'].astype(int)

        # Clean Book_Title and store cleaned title
        books_df['Cleaned_Book_Title'] = books_df['Book_Title'].apply(self.clean_title)

        # Keep only relevant columns
        books_df = books_df[['ISBN', 'Book_Title', 'Book_Author', 'Year_Of_Publication', 'Publisher', 'Avg_Rating', 'Num_Ratings', 'Std_Rating', 'Cleaned_Book_Title']]

        # Store the cleaned data in the database
        conn = sqlite3.connect('books.db')
        books_df.to_sql('books', conn, if_exists='replace', index=False)
        conn.commit()
        conn.close()

    def train_model(self):
        # Load the book data from the database
        conn = sqlite3.connect('books.db')
        books_df = pd.read_sql_query("SELECT * FROM books", conn)
        conn.close()

        # Shuffle the dataset to add some randomness
        books_df = books_df.sample(frac=1).reset_index(drop=True)

        # Use aggregated features for more variation
        book_features = books_df[['Avg_Rating', 'Num_Ratings', 'Std_Rating', 'Year_Of_Publication']].values
        isbn_list = books_df['ISBN'].tolist()

        # Train the k-NN model
        model = NearestNeighbors(n_neighbors=10)
        model.fit(book_features)
        return model, isbn_list

    def get_recommendations(self):
        # Get book title from the user input and clean it
        book_title = self.clean_title(self.entry.get())

        # Query the database for the book
        conn = sqlite3.connect('books.db')
        c = conn.cursor()
        c.execute("SELECT * FROM books WHERE Cleaned_Book_Title=?", (book_title,))
        book = c.fetchone()
        conn.close()

        if book:
            # Get features for the book
            avg_rating = book[5]  # Avg_Rating
            num_ratings = book[6]  # Num_Ratings
            std_rating = book[7]  # Std_Rating
            year_of_publication = book[3]  # Year_Of_Publication

            # Find similar books using k-NN model
            features = [[avg_rating, num_ratings, std_rating, year_of_publication]]
            distances, indices = self.model.kneighbors(features)
            recommendations = self.fetch_recommendations(indices[0], book[0])
            self.display_recommendations(recommendations)
        else:
            messagebox.showerror("Error", "Book not found!")

    def fetch_recommendations(self, indices, input_isbn):
        # Fetch book recommendations from the database
        conn = sqlite3.connect('books.db')
        c = conn.cursor()
        recommendations = set()
        for idx in indices:
            if len(recommendations) >= 3:
                break
            isbn = self.isbn_list[idx]
            if isbn == input_isbn:
                continue  # Skip the input book itself
            c.execute("SELECT Book_Title, Book_Author FROM books WHERE ISBN=?", (isbn,))
            result = c.fetchone()
            if result:
                book_title_author = f"{result[0]} by {result[1]}"
                recommendations.add(book_title_author)
            else:
                print(f"Warning: No book found for ISBN {isbn}")
        conn.close()
        return list(recommendations)

    def display_recommendations(self, recommendations):
        # Display book recommendations in the text widget
        self.result_text.delete(1.0, tk.END)
        if recommendations:
            for book in recommendations:
                wrapped_text = textwrap.fill(f"• {book}", width=70, subsequent_indent='  ')
                self.result_text.insert(tk.END, f"{wrapped_text}\n")
        else:
            self.result_text.insert(tk.END, "No recommendations found.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookRecommenderApp(root)
    root.mainloop()
