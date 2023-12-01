# List the most expensive items in each category.
QUERY_1 = (
    """
    WITH RankedItems AS (
        SELECT
            i.item_id,
            i.title,
            i.description,
            i.price,
            c.category_name,
            ROW_NUMBER() OVER (PARTITION BY c.category_id ORDER BY i.price DESC) AS ranking
        FROM
            items i
            JOIN item_categories ic ON i.item_id = ic.item_id
            JOIN categories c ON ic.category_id = c.category_id
    )
    SELECT
        category_name,
        item_id,
        title,
        description,
        price
    FROM
        RankedItems
    WHERE
        ranking = 1;
    """
)

# List the users who posted at least two items that were posted on the same day, one has a category of X, and another has a category of Y. In terms of the user interface, you will implement two text fields so that you can input one category into each text field, and the search will return the user (or users) who (the same user) posted two different items on the same day, such that one item has a category in the first text field and the other has a category in the second text field.
QUERY_2 = (
    """
    SELECT
        u.*,
        COUNT(DISTINCT CONCAT(i1.item_id, i2.item_id)) AS item_count
    FROM
        users u
        JOIN items i1 ON u.user_id = i1.author_id
        JOIN items i2 ON u.user_id = i2.author_id
        JOIN item_categories ic1 ON i1.item_id = ic1.item_id
        JOIN item_categories ic2 ON i2.item_id = ic2.item_id
    WHERE
        i1.created_at = i2.created_at
        AND ic1.category_id = 'X' 
        AND ic2.category_id = 'Y'
    GROUP BY
        u.user_id, u.username
    HAVING
        item_count >= 2;
    """
)

# List all the items posted by user X, such that all the comments are "Excellent" or "good" for these items (in other words, these items must have comments, but these items don't have any other kinds of comments, such as "bad" or "fair" comments). User X is arbitrary and will be determined by the instructor.
QUERY_3 = (
    """
    SELECT i.*
    FROM items i
    JOIN reviews r ON i.item_id = r.item_id
    WHERE r.rating IN ('excellent', 'good')
    AND r.author_id = (SELECT user_id FROM users WHERE username = 'X')
    AND NOT EXISTS (
        SELECT 1
        FROM reviews
        WHERE item_id = i.item_id
        AND rating NOT IN ('excellent', 'good')
    );
    """
)

# List the users who posted the most number of items on a specific date like 5/1/2023; if there is a tie, list all the users who have a tie. The specific date can be hard coded into your SQL select query or given by the user.
QUERY_4 = (
    """
    SET @specific_date = '2023-05-01';

    SELECT u.*, COUNT(i.item_id) as num_items_posted
    FROM users u
    JOIN items i ON u.user_id = i.author_id
    WHERE DATE(i.created_at) = @specific_date
    GROUP BY u.user_id, u.username
    HAVING COUNT(i.item_id) = (
        SELECT COUNT(item_id) as max_num_items
        FROM items
        WHERE DATE(created_at) = @specific_date
        GROUP BY author_id
        ORDER BY max_num_items DESC
        LIMIT 1
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
    SELECT
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
    JOIN items i ON u.user_id = i.author_id
    WHERE NOT EXISTS (
        SELECT 1
        FROM reviews r
        WHERE r.item_id = i.item_id
        AND r.rating = 'poor'
    )
    OR NOT EXISTS (
        SELECT 1
        FROM reviews r
        WHERE r.item_id = i.item_id
    );
    """
)

# List a user pair (A, B) such that they always gave each other "excellent" reviews for every single item they posted.
QUERY_10 = (
    """
    SELECT
        u1.user_id AS userA_id,
        u1.username AS userA_username,
        u2.user_id AS userB_id,
        u2.username AS userB_username
    FROM
        users u1
        JOIN users u2 ON u1.user_id < u2.user_id -- Ensuring unique pairs
        JOIN items i1 ON u1.user_id = i1.author_id
        JOIN items i2 ON u2.user_id = i2.author_id
    WHERE
        NOT EXISTS (
            SELECT 1
            FROM
                reviews r1
                JOIN reviews r2 ON r1.item_id = i1.item_id AND r2.item_id = i2.item_id
            WHERE
                r1.author_id = u1.user_id
                AND r2.author_id = u2.user_id
                AND (r1.rating != 'excellent' OR r2.rating != 'excellent')
        )
        AND EXISTS (
            SELECT 1
            FROM
                reviews r1
                JOIN reviews r2 ON r1.item_id = i1.item_id AND r2.item_id = i2.item_id
            WHERE
                r1.author_id = u1.user_id
                AND r2.author_id = u2.user_id
                AND (r1.rating = 'excellent' AND r2.rating = 'excellent')
        );
    """
)
