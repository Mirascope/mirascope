CREATE TABLE ReadingList (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    status TEXT CHECK(status IN ('Not Started', 'In Progress', 'Complete')) NOT NULL,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5)
);
