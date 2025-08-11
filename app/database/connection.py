# app/database/connection.py
import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)


def get_connection():
    """
    Create and return a database connection
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        raise ConnectionError(f"Database connection error: {e}")


def execute_query(query, params=None, fetch_all=True):
    """
    Execute a database query and return results if it's a SELECT query.
    
    Args:
        query (str): SQL query to execute
        params (tuple or list): Query parameters
        fetch_all (bool): Whether to fetch all results or just one
        
    Returns:
        list/dict/None: Query results for SELECT queries, None for other queries
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Handle batch insert case
            if isinstance(params, list) and all(isinstance(item, tuple) for item in params):
                cursor.executemany(query, params)
            else:
                cursor.execute(query, params)
            
            # Only fetch results for SELECT queries
            if query.strip().upper().startswith("SELECT"):
                if fetch_all:
                    results = [dict(row) for row in cursor.fetchall()]
                else:
                    row = cursor.fetchone()
                    results = dict(row) if row else None
                return results
            else:
                # For non-SELECT queries (INSERT, UPDATE, DELETE), commit and return None
                conn.commit()
                return None
    except Exception as e:
        logger.error(f"Database error: {e}")
        if conn:
            conn.rollback()  # Rollback transaction on error
        raise  # Re-raise the exception after logging
    finally:
        if conn:
            conn.close()