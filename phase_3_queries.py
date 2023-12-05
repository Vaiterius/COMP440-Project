# List the most expensive items in each category.
QUERY_1 = (
    """
    SELECT
        c.category_name,
        MAX(i.item_id) AS item_id,
        MAX(i.title) AS title,
        MAX(i.description) AS description,
        MAX(i.price) AS price
    FROM
        categories c
    LEFT JOIN item_categories ic ON c.category_id = ic.category_id
    LEFT JOIN items i ON ic.item_id = i.item_id
    WHERE
        i.price = (
            SELECT MAX(price)
            FROM items
            WHERE item_id = i.item_id
        )
        OR i.price IS NULL
    GROUP BY
        c.category_name;
    """
)

# List the users who posted at least two items that were posted on the same day, one has a category of X, and another has a category of Y. In terms of the user interface, you will implement two text fields so that you can input one category into each text field, and the search will return the user (or users) who (the same user) posted two different items on the same day, such that one item has a category in the first text field and the other has a category in the second text field.
QUERY_2 = (
    """
    SELECT u.*
    FROM users u
    JOIN items i1 ON u.user_id = i1.author_id
    JOIN items i2 ON u.user_id = i2.author_id
    JOIN item_categories ic1 ON i1.item_id = ic1.item_id
    JOIN item_categories ic2 ON i2.item_id = ic2.item_id
    JOIN categories c1 ON ic1.category_id = c1.category_id AND c1.category_name = %s
    JOIN categories c2 ON ic2.category_id = c2.category_id AND c2.category_name = %s
    WHERE DATE(i1.created_at) = DATE(i2.created_at)
    AND i1.item_id <> i2.item_id;
    """
)

# List all the items posted by user X, such that all the comments are "Excellent" or "good" for these items (in other words, these items must have comments, but these items don't have any other kinds of comments, such as "bad" or "fair" comments). User X is arbitrary and will be determined by the instructor.
QUERY_3 = (
    """
    SELECT i.*
    FROM items i
    JOIN reviews r ON i.item_id = r.item_id
    JOIN users u ON i.author_id = u.user_id
    WHERE u.username = %s
    GROUP BY i.item_id, i.title, i.description, i.price
    HAVING SUM(r.rating NOT IN ('excellent', 'good')) = 0;
    """
)

# List the users who posted the most number of items on a specific date like 5/1/2023; if there is a tie, list all the users who have a tie. The specific date can be hard coded into your SQL select query or given by the user.
QUERY_4 = (
    """
    WITH UserPostCount AS (
    SELECT
        u.user_id,
        u.username,
        COUNT(i.item_id) AS post_count
    FROM
        users u
    LEFT JOIN
        items i ON u.user_id = i.author_id
            AND DATE(i.created_at) = %s
    GROUP BY
        u.user_id, u.username
    )
    SELECT
    user_id,
    username,
    post_count
    FROM
    UserPostCount
    WHERE
    post_count = (
        SELECT MAX(post_count)
        FROM UserPostCount
    );
    """
)

# List the other users who are favorited by both users X, and Y. Usernames X and Y will be selected from dropdown menus by the instructor. In other words, the user (or users) C are the favorite for both X and Y.
QUERY_5 = (
    """

    """
)

# Display all the users who never posted any "excellent" items: an item is excellent if at least three reviews are excellent.
QUERY_6 = (
    """
    SELECT u.*
    FROM users u
    WHERE NOT EXISTS (
        SELECT 1
        FROM items i
        JOIN reviews r ON i.item_id = r.item_id
        WHERE i.author_id = u.user_id
        AND r.rating = 'excellent'
        GROUP BY i.item_id
        HAVING COUNT(r.review_id) >= 3
    );
    """
)

# Display all the users who never posted a "poor" review.
QUERY_7 = (
    """
    SELECT u.*
    FROM users u
    WHERE NOT EXISTS (
        SELECT 1
        FROM reviews r
        WHERE r.author_id = u.user_id
        AND r.rating = 'poor'
    );
    """
)

# Display all the users who posted some reviews, but each of them is "poor".
QUERY_8 = (
    """
    SELECT DISTINCT
        u.user_id,
        u.username
    FROM
        users u
        JOIN reviews r ON u.user_id = r.author_id
    WHERE
        r.rating = 'poor';
    """
)

# Display those users such that each item they posted so far never received any "poor" reviews. In other words, these users must have posted some items; however, these items have never received any poor reviews or have not received any reviews at all.
QUERY_9 = (
    """
    SELECT DISTINCT u.*
    FROM users u
    JOIN reviews r ON u.user_id = r.author_id
    WHERE NOT EXISTS (
        SELECT 1
        FROM reviews
        WHERE author_id = u.user_id
        AND rating != 'poor'
    )
    AND EXISTS (
        SELECT 1
        FROM reviews
        WHERE author_id = u.user_id
    );
    """
)

# List a user pair (A, B) such that they always gave each other "excellent" reviews for every single item they posted.
QUERY_10 = (
    """
    SELECT DISTINCT ua.user_id AS user_a_id, ua.username AS user_a_username,
        ub.user_id AS user_b_id, ub.username AS user_b_username
    FROM users ua
    JOIN items ia ON ua.user_id = ia.author_id
    JOIN reviews ra ON ia.item_id = ra.item_id AND ra.rating = 'excellent'
    JOIN users ub ON ra.author_id = ub.user_id
    JOIN items ib ON ub.user_id = ib.author_id
    JOIN reviews rb ON ib.item_id = rb.item_id AND rb.rating = 'excellent'
    WHERE ua.user_id < ub.user_id;
    """
)
