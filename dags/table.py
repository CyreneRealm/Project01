import psycopg2
from get_api import get_data


def connect():
    # Try connecting within the Docker network
    conn = psycopg2.connect(
        host="db",
        port="5432",
        user="postgres_user",
        password="postgres_password",
        database="database01",
        connect_timeout=3
    )
    return conn


def create_schema(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS p1;
            
            CREATE TABLE IF NOT EXISTS p1.raw_weather_data (
                id SERIAL PRIMARY KEY,
                city TEXT,
                temperature FLOAT,
                weather_descriptions TEXT,
                wind_speed FLOAT,
                observation_time TIMESTAMP,
                inserted_at TIMESTAMP DEFAULT NOW(),
                utc_offset TEXT,
                CONSTRAINT unique_city_time UNIQUE (city, observation_time) 
            );
        """)
    conn.commit()


def format_utc_offset(offset_seconds: int) -> str:
    sign = '+' if offset_seconds >= 0 else '-'
    hours, remainder = divmod(abs(offset_seconds), 3600)
    minutes = remainder // 60
    return f"{sign}{hours:02d}:{minutes:02d}"


def insert_data(conn, data):
    cursor = conn.cursor()
    try:
        cursor.execute("""
                INSERT INTO p1.raw_weather_data (
                    city,
                    temperature,
                    weather_descriptions,
                    wind_speed,
                    observation_time,
                    inserted_at,
                    utc_offset
                ) VALUES (%s, %s, %s, %s, to_timestamp(%s), NOW(), %s)
                ON CONFLICT (city, observation_time) DO NOTHING;
            """, (
            data['name'],
            data['main']['temp'],
            data['weather'][0]['description'],
            data['wind']['speed'],
            data['dt'],
            format_utc_offset(data['timezone']),
        ))
        conn.commit()
        print("Da chen du lieu thanh cong!")
    except Exception as e:
        conn.rollback()
        print(f"Loi khi chen du lieu: {e}")
    finally:
        cursor.close()


def main():
    conn = None
    try:
        data = get_data()
        conn = connect()
        create_schema(conn)
        insert_data(conn, data)
    except Exception as e:
        print(f"Loi trong qua trinh chay pipeline: {e}")
    finally:
        if conn is not None:
            conn.close()
            print("Da dong ket noi database.")


if __name__ == "__main__":
    main()
