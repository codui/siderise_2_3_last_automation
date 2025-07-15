import logging
import sqlite3
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


def create_database_if_not_exist(
    name_database: str = "side_rise_database.db",
    name_table: str = "photos",
    subfolder: str = "subfolder_with_photo",
) -> None:
    """Creates a database table if it does not exist.

    Args:
        name_database (str, optional): Name of file database.
            Defaults to "side_rise_database.db".
        name_table (str): Name of table database.
            Defaults to "photos".
        subfolder (str): Name of subfolder with photos.
            Defaults to "subfolder_with_photo".
    """
    # ! CREATE DATABASE IF NOT EXISTS
    # Start data base
    connection = sqlite3.connect(name_database)
    # Cursor object for executing SQL queries and database operations
    cursor = connection.cursor()
    # # cursor=<sqlite3.Cursor object at 0x000001E740B76C40>, type(cursor)=<class 'sqlite3.Cursor'>
    # logging.info(f"{cursor=}, {type(cursor)=}")
    # Create database table with parameters
    cursor.execute(
        f"""CREATE TABLE IF NOT EXISTS {name_table} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        building_code TEXT NOT NULL,
        {subfolder} TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    # Save changes
    connection.commit()
    # Close connection with data base
    connection.close()


def create_index_for_column_data_base(
    name_database: str,
    name_table: str,
    name_column: str,
) -> None:
    """ Create index for column spcified in "name_column".

    Args:
        name_database (str): Name of file database.
            For example:
                "side_rise_database.db"
        name_table (str): Name of table database.
            For example:
                "photos"
        name_column (str): The name of the column for which the index should be created.
            For example:
                "filename"
    """
    connection = sqlite3.connect(name_database)
    # Cursor object for executing SQL queries and database operations
    cursor = connection.cursor()
    # Create index for column "file_hash"
    cursor.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{name_column} ON {name_table} ({name_column})"
    )
    # Save changes and close connection
    connection.commit()
    connection.close()


def add_photos_to_data_base(
    building_code: str,
    subfolder: str,
    photos: list[Path],
    name_database: str = "side_rise_database.db",
    name_table: str = "photos",
) -> None:
    """ Gets a list of photos in a folder. Checks if the photo is in the database.
    If the photo is not in the database, then it adds it there.
    If the photo is there, then it simply displays a log that this photo is already in the database
    and moves on to the next photo.

    DATABASE:
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        building_code TEXT NOT NULL,
        subfolder TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    Args:
        building_code (str): The apartment code adopted in this project.
            The code consists of three parts - Block, Level, Plot.
                Block - one letter from this letters (A,B,C,D,E,F,G)
                Level - big letter "L" plus one number from this numbers (1,2,3,4,5,6,7,8)
                Plot - word "Plot" plus one number from this numbers (1, ... 456)
            For example:
                "A_L1_Plot_1"
        subfolder (str): A folder containing photographs whose information needs to be recorded in the database.
            For example:
                "2.3\photos_on_asite"
        photos (list[Path]): List of photos that need to be added to the database.
    """
    # Establish a connection to the database
    connection = sqlite3.connect(name_database)
    cursor = connection.cursor()

    for photo in photos:
        # logging.info(f"{photo=}")
        # 'plot 02 block A lev 1 WA0118.jpg'
        filename: str = photo.name
        logging.info(f"{filename=}")
        # Size of photo in bytes like: 194918
        file_size: int = photo.stat().st_size
        logging.info(f"{file_size=}, {type(file_size)=}")
        # Check that the photo is not in the database
        cursor.execute(
            f'SELECT filename FROM {name_table} WHERE filename = "{filename}"'
        )
        filename_in_database = cursor.fetchone()
        if filename_in_database:
            logging.info(
                f"Файл с именем {filename_in_database} уже в базе данных."
                "\nНе нужно его повторно вносить."
            )
        else:
            # Insert data in database if hash of photo not in database
            cursor.execute(
                f"""INSERT INTO {name_table}
                (building_code, subfolder_with_photo, filename, file_size) VALUES (?, ?, ?, ?)""",
                (building_code, subfolder, filename, file_size),
            )
            connection.commit()
            logging.info(
                f"Файл с именем {filename_in_database} успешно внесен в базу данных."
            )
    # Close the database connection
    connection.close()
