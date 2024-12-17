import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))
from app.models import schema
from app.utils import settings
from app.modules.client import thanosql_client


def get_tables_info_query(tables: list[schema.base.Table]):
    # Generate the SQL query to get column details for all specified tables
    queries = []
    for table in tables:
        table_schema = table.table_schema
        table_name = table.table_name
        query = f"""
        SELECT
            '{table_schema}' AS table_schema,
            '{table_name}' AS table_name,
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = '{table_schema}' AND table_name = '{table_name}'
        """
        queries.append(query)
    return " UNION ALL ".join(queries)


def generate_create_table_statement(table_schema, table_name, columns):
    # Start creating the CREATE TABLE statement
    create_table_sql = f"CREATE TABLE {table_schema}.{table_name} (\n"
    column_definitions = []

    for column in columns:
        column_name = column[0]
        data_type = column[1]
        is_nullable = column[2]
        column_default = column[3]

        column_def = f"  {column_name} {data_type}"
        if is_nullable == "NO":
            column_def += " NOT NULL"
        if column_default:
            column_def += f" DEFAULT {column_default}"

        column_definitions.append(column_def)

    create_table_sql += ",\n".join(column_definitions)
    create_table_sql += "\n);"
    return create_table_sql


def get_create_table_statement(table_list: list[schema.base.Table]) -> str:
    table_columns = {}
    table_info_query = get_tables_info_query(table_list)
    table_info_list = thanosql_client.query.execute(table_info_query).records.data

    for row in table_info_list:
        table_schema = row["table_schema"]
        table_name = row["table_name"]
        column_info = [
            row["column_name"],
            row["data_type"],
            row["is_nullable"],
            row["column_default"],
        ]
        table_key = (table_schema, table_name)
        if table_key not in table_columns:
            table_columns[table_key] = []
        table_columns[table_key].append(column_info)

    # Generate and print the CREATE TABLE statements
    create_table_sql = ""

    for table_key, columns in table_columns.items():
        table_schema, table_name = table_key
        create_table_sql += (
            f"{generate_create_table_statement(table_schema, table_name, columns)} \n"
        )

    return create_table_sql


def merge_list(list1, list2):
    result = []
    if list1:
        result.extend(list1)
    if list2:
        result.extend(list2)

    return result


def mask_string(s: str) -> str:
    """Mask 80% of the string, showing the first and last characters."""
    if not s:
        return ""  # Return empty string if the input is None or empty

    length = len(s)
    # Calculate the number of characters to keep visible
    visible_chars_count = max(1, length // 10)  # At least 1 character should be visible

    # Get the beginning and end parts of the string
    start = s[:visible_chars_count]
    end = s[-visible_chars_count:]

    # Calculate how many characters to mask
    mask_length = length - (visible_chars_count * 2)

    # Return the masked string
    return f"{start}{'*' * mask_length}{end}"


# Retrieve chat control settings from Redis and pack into model
def pack_chat_control_response() -> schema.chat.ChatSettingsResponse:
    # Define the fields that need to be fetched from Redis
    field_names = [
        "openai_model",
        "openai_base_url",
        "openai_api_key",
        "text2sql_model",
        "text2sql_base_url",
        "text2sql_api_key",
        "temperature",
        "max_temperature",
        "system_prompt",
    ]

    # Use a dictionary comprehension to fetch values from Redis
    configs = {
        field: mask_string(settings.redis.get(field))
        if "api_key" in field
        else (settings.redis.get(field) or "")
        for field in field_names
    }

    return schema.chat.ChatSettingsResponse(**configs)
